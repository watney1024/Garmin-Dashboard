# -*- coding: utf-8 -*-
"""profile_wizard.py — runner-profile questionnaire wizard, validator and YAML-subset parser (stdlib only).

A runner's profile (schema: docs/08) is the one file the runner owns, and today filling it in
means hand-writing YAML. This script turns that into three entry points:

  * interactive wizard          python scripts/profile_wizard.py [--out <path>]
  * fillable questionnaire      python scripts/profile_wizard.py --emit-questionnaire
  * dependency-free validator   python scripts/profile_wizard.py --check <path>
  * canonical question list     python scripts/profile_wizard.py --questions [--lang zh|en]
  * self-consistency check      python scripts/profile_wizard.py --selfcheck

`FIELDS` below is the SINGLE SOURCE OF TRUTH for the schema. The question list, the fillable
questionnaire and the validator are all derived from it; nothing else may restate the fields.
Editing `FIELDS` without regenerating `examples/runner_profile.questionnaire.yaml` makes
`--selfcheck` (and the unit tests) fail — that is the anti-drift guard.

⚠ There is deliberately NO `import yaml` (this repo is stdlib-only). The parser accepts a
restricted YAML subset and rejects the rest loudly:

  accepted : block mappings, block sequences, inline flow sequences ("[a, b]", "[]"),
             single/double quoted scalars — including ones spanning several physical lines —
             plain scalars continued on the next line, inline and full-line comments,
             a leading BOM, CRLF endings, a leading "---".
  rejected : tab indentation, flow mappings ("{...}"), block scalars ("|", ">"),
             anchors ("&"), aliases ("*"), merge keys ("<<"), tags ("!"), duplicate keys,
             inconsistent indentation, unterminated quotes or flow sequences.

Unknown TOP-LEVEL keys (e.g. a runner's private "measured:" block) are captured verbatim and
never parsed, so a hand-maintained extension block can live alongside the documented schema
without breaking validation — and the wizard writes it back untouched.

Exit codes (same policy as the other scripts): 0 = no errors, 1 = errors / parse failure /
wizard aborted, 2 = usage or configuration error.

Examples:
    python scripts/profile_wizard.py                              # fill in workspace/runner_profile.yaml
    python scripts/profile_wizard.py --check workspace/runner_profile.yaml
    python scripts/profile_wizard.py --questions --lang en
    python scripts/profile_wizard.py --emit-questionnaire
    python scripts/profile_wizard.py --selfcheck
"""

import argparse
import datetime
import os
import re
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, ".agents", "skills")
EXAMPLES_DIR = os.path.join(REPO_ROOT, "examples")
EXAMPLE_PROFILE = os.path.join(EXAMPLES_DIR, "runner_profile.example.yaml")
QUESTIONNAIRE_FILE = os.path.join(EXAMPLES_DIR, "runner_profile.questionnaire.yaml")
DEFAULT_PROFILE = os.path.join(REPO_ROOT, "workspace", "runner_profile.yaml")

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# Values that mean "I have not filled this in yet". They are a warning, not an error: the real
# profile is allowed to carry a known gap (the runner owes an answer), it just gets reported.
UNFILLED = ("待补", "待定", "未定", "tbd", "todo", "fixme")


# ===========================================================================
# FIELDS — the single source of truth
# ===========================================================================

FIELDS = (
    # ---- identity -------------------------------------------------------
    {"path": "identity.alias", "type": "str", "required": True,
     "label": {"zh": "称呼", "en": "Alias"},
     "question": {"zh": "我该怎么称呼你？（请勿填真实姓名）",
                  "en": "What should I call you? (never your real name)"},
     "help": {"zh": "只是给 agent 用的代称，会出现在计划 HTML 的标题里。",
              "en": "A handle only; it shows up in the plan HTML title."},
     "example": "示例跑者", "placeholder": "<alias / 称呼>"},
    {"path": "identity.language", "type": "enum", "required": True, "enum": ["zh", "en"],
     "label": {"zh": "文档语言", "en": "Docs language"},
     "question": {"zh": "计划和教练文档用中文还是英文？",
                  "en": "Should the plan and coach docs be Chinese or English?"},
     "help": {"zh": "决定加载 .agents/skills/coach-*/references/coach-*_<lang>.md。",
              "en": "Selects which coach references file gets loaded."},
     "example": "zh", "placeholder": "<zh | en>"},
    {"path": "identity.timezone", "type": "str", "required": True,
     "label": {"zh": "时区", "en": "Timezone"},
     "question": {"zh": "你的 IANA 时区是什么？",
                  "en": "What is your IANA timezone?"},
     "help": {"zh": "决定“周”的边界。注意 Garmin 账户时区可能与手机时区不同（同为 UTC+8 则周界一致）。",
              "en": "Defines the week boundary. Garmin's account timezone can differ from your phone's."},
     "example": "Asia/Shanghai", "placeholder": "<IANA tz, e.g. Asia/Shanghai>"},
    {"path": "identity.birth_year", "type": "int", "required": False,
     "range": [1900, 2100],
     "label": {"zh": "出生年（可选）", "en": "Birth year (optional)"},
     "question": {"zh": "出生年份？（可留空）",
                  "en": "Year of birth? (blank to skip)"},
     "help": {"zh": "与 sex 一起才会启用年龄/性别修正 VDOT（docs/09 §8）；年龄落在 18–38 则不需要修正。",
              "en": "Only with sex does it enable age-graded VDOT (docs/09 §8); ages inside 18–38 need no correction."},
     "example": 1985, "placeholder": "<year>"},
    {"path": "identity.sex", "type": "enum", "required": False, "enum": ["F", "M"],
     "label": {"zh": "生理性别（可选）", "en": "Sex (optional)"},
     "question": {"zh": "生理性别 F/M？（可留空）",
                  "en": "Sex F/M? (blank to skip)"},
     "help": {"zh": "仅在启用年龄/性别修正时使用。",
              "en": "Used only for the age/sex-graded tables."},
     "example": "M", "placeholder": "<F | M>"},

    # ---- races ----------------------------------------------------------
    {"path": "races[].name", "type": "str", "required": True,
     "label": {"zh": "比赛名", "en": "Race name"},
     "question": {"zh": "这场比赛叫什么？（可用代称）",
                  "en": "What is this race called? (a nickname is fine)"},
     "help": {"zh": "会出现在计划的赛事卡与闸门里。",
              "en": "Appears in the plan's race cards and gates."},
     "example": "示例湖半程马拉松", "placeholder": "<race name / 比赛名>"},
    {"path": "races[].date", "type": "date", "required": True,
     "label": {"zh": "比赛日期", "en": "Race date"},
     "question": {"zh": "哪一天？（YYYY-MM-DD）",
                  "en": "Which day? (YYYY-MM-DD)"},
     "help": {"zh": "周期从 A 赛倒推，日期错了整套课表都要重排。",
              "en": "The whole cycle counts back from the A race, so a wrong date reshuffles everything."},
     "example": "2027-11-21", "placeholder": "<YYYY-MM-DD>"},
    {"path": "races[].distance", "type": "str", "required": True,
     "label": {"zh": "距离", "en": "Distance"},
     "question": {"zh": "什么距离？（marathon / half / 10k / 5k / …）",
                  "en": "What distance? (marathon / half / 10k / 5k / …)"},
     "help": {"zh": "开放取值——不限于这几种，写你实际报的项目。",
              "en": "Open value — write whatever you actually entered."},
     "example": "marathon", "placeholder": "<marathon | half | 10k | 5k>"},
    {"path": "races[].role", "type": "enum", "required": True,
     "enum": ["A", "attempt", "training"],
     "label": {"zh": "角色", "en": "Role"},
     "question": {"zh": "它的角色是？A＝唯一全力赛 / attempt＝认真但不全力 / training＝当训练课",
                  "en": "Its role? A = the one all-out race / attempt = serious but not all-out / training = a tune-up"},
     "help": {"zh": "一个周期内只能有 1 个 A；比赛必须标 role，三者互斥。",
              "en": "At most one A per cycle; role is mandatory and the three values are mutually exclusive."},
     "example": "A", "placeholder": "<A | attempt | training>"},
    {"path": "races[].note", "type": "str", "required": False,
     "label": {"zh": "备注（可选）", "en": "Note (optional)"},
     "question": {"zh": "这场比赛有什么要提醒我的？（补给/赛道/目标；可留空）",
                  "en": "Anything I should know about this race? (fuelling, course, goal; blank to skip)"},
     "help": {"zh": "自由文本，会进规划的判断依据。",
              "en": "Free text; it feeds the planning judgement."},
     "example": "赛道起伏，目标 4:05", "placeholder": "<free text / 自由文本>"},

    # ---- weekly ---------------------------------------------------------
    {"path": "weekly.runs_per_week", "type": "int", "required": True, "range": [1, 14],
     "label": {"zh": "每周跑几次", "en": "Runs per week"},
     "question": {"zh": "一周打算跑几次？",
                  "en": "How many runs per week?"},
     "help": {"zh": "目标次数；加量时逐周往上加，不要一步到位。",
              "en": "The target count; build up week by week rather than all at once."},
     "example": 4, "placeholder": "<runs per week / 每周次数>"},
    {"path": "weekly.days", "type": "map", "required": True,
     "key_type": "weekday", "value_type": "enum",
     "value_enum": ["quality", "easy", "long"], "sparse": True,
     "label": {"zh": "可训日与角色", "en": "Trainable days and roles"},
     "question": {"zh": "哪几天跑？各是什么角色（quality/easy/long）？",
                  "en": "Which weekdays do you run, and with which role (quality/easy/long)?"},
     "help": {"zh": "不跑的天整行删掉。质量课定义由教练包给。",
              "en": "Omit rest days entirely. The coach package defines what \"quality\" means."},
     "example": {"Tuesday": "quality", "Thursday": "easy", "Sunday": "long"},
     "placeholder": "<easy | quality | long>"},
    {"path": "weekly.long_run_day", "type": "weekday", "required": True,
     "label": {"zh": "长距离日", "en": "Long-run day"},
     "question": {"zh": "长距离放在星期几？",
                  "en": "Which weekday carries the long run?"},
     "help": {"zh": "前一天不要安排下肢大负荷（docs/03）。",
              "en": "Nothing heavy for the legs the day before (docs/03)."},
     "example": "Sunday", "placeholder": "<weekday / 星期几>"},
    {"path": "weekly.quality_days", "type": "list[weekday]", "required": True,
     "label": {"zh": "质量课日", "en": "Quality days"},
     "question": {"zh": "质量课放在哪几天？（可以多个，用逗号分隔）",
                  "en": "Which weekdays carry quality sessions? (several allowed, comma-separated)"},
     "help": {"zh": "必须与 weekly.days 里的 quality 角色一致。",
              "en": "Must agree with the quality roles in weekly.days."},
     "example": ["Tuesday"], "placeholder": "[weekday, …]"}, 
    {"path": "weekly.max_run_min", "type": "int", "required": False, "range": [30, 400],
     "label": {"zh": "单次时长上限（可选）", "en": "Max single-run minutes (optional)"},
     "question": {"zh": "单次跑步最长多少分钟？（可留空）",
                  "en": "Longest single run in minutes? (blank to skip)"},
     "help": {"zh": "超过教练包默认上限时，计划必须把这条偏离写进第十章。",
              "en": "Exceeding the coach default means the plan must log the deviation in chapter 10."},
     "example": 180, "placeholder": "<minutes / 分钟>"},

    # ---- pr -------------------------------------------------------------
    {"path": "pr.5k", "type": "time", "format": "MM:SS", "group": "pr", "required": False,
     "label": {"zh": "5K 最好成绩", "en": "5K PR"},
     "question": {"zh": "最近半年内的 5K 成绩？（没有就回车跳过）",
                  "en": "A 5K result from the last six months? (blank to skip)"},
     "help": {"zh": "四项 PR 至少填一个才能推导 VDOT（docs/09）。",
              "en": "At least one of the four is needed to derive VDOT (docs/09)."},
     "example": "23:45", "placeholder": "<MM:SS>"},
    {"path": "pr.10k", "type": "time", "format": "MM:SS", "group": "pr", "required": False,
     "label": {"zh": "10K 最好成绩", "en": "10K PR"},
     "question": {"zh": "10K 成绩？（没有就回车跳过）",
                  "en": "A 10K result? (blank to skip)"},
     "help": {"zh": "越接近当前体能、越近期的成绩，VDOT 越可信。",
              "en": "The more recent and the closer to current fitness, the more trustworthy the VDOT."},
     "example": "49:30", "placeholder": "<MM:SS>"},
    {"path": "pr.half", "type": "time", "format": "H:MM:SS", "group": "pr", "required": False,
     "label": {"zh": "半马最好成绩", "en": "Half-marathon PR"},
     "question": {"zh": "半马成绩？（没有就回车跳过）",
                  "en": "A half-marathon result? (blank to skip)"},
     "help": {"zh": "格式 H:MM:SS。",
              "en": "Format H:MM:SS."},
     "example": "1:52:30", "placeholder": "<H:MM:SS>"},
    {"path": "pr.marathon", "type": "time", "format": "H:MM:SS", "group": "pr", "required": False,
     "label": {"zh": "全马最好成绩", "en": "Marathon PR"},
     "question": {"zh": "全马成绩？（没有就回车跳过）",
                  "en": "A marathon result? (blank to skip)"},
     "help": {"zh": "若非全力跑的，务必在 constraints 里注明——它会决定 VDOT 是下限还是真值。",
              "en": "If it was not an all-out effort, say so in constraints — it decides whether the VDOT is a floor or the truth."},
     "example": "3:54:04", "placeholder": "<H:MM:SS>"},

    # ---- coach ----------------------------------------------------------
    {"path": "coach", "type": "enum", "required": True, "validator": "coach_dir",
     "enum": ["daniels_vdot", "polarized_80_20", "hanson",
              "advanced_marathoning", "lydiard"],
     "label": {"zh": "教练包", "en": "Coach package"},
     "question": {"zh": "想用哪套教练方法？",
                  "en": "Which coaching method do you want?"},
     "help": {"zh": "取值对应 .agents/skills/coach-<id>/（id 里的 _ 换成 -）。",
              "en": "Values map to .agents/skills/coach-<id>/ (underscore becomes dash)."},
     "example": "daniels_vdot", "placeholder": "<coach id>"},

    # ---- strength -------------------------------------------------------
    {"path": "strength.sessions_per_week", "type": "int", "required": True, "range": [1, 7],
     "label": {"zh": "每周力量次数", "en": "Strength sessions per week"},
     "question": {"zh": "一周做几次力量？",
                  "en": "How many strength sessions per week?"},
     "help": {"zh": "整块可选；填了就要把两个子字段都填全。",
              "en": "The whole block is optional; if present, both children are required."},
     "example": 2, "placeholder": "<sessions per week / 每周次数>"},
    {"path": "strength.days", "type": "map", "required": True,
     "key_type": "weekday", "value_type": "str", "sparse": True,
     "label": {"zh": "力量日与内容", "en": "Strength days and content"},
     "question": {"zh": "力量放在哪几天？各练什么？",
                  "en": "Which weekdays, and what does each session work?"},
     "help": {"zh": "用块状写法，一天一行；不要写成 {周几: 内容} 那种流式映射。",
              "en": "Use block style, one day per line — not a {day: content} flow mapping."},
     "example": {"Wednesday": "lower body (squat/RDL/lunge/calf)"},
     "placeholder": "<what you train / 练什么>"},

    # ---- constraints ----------------------------------------------------
    {"path": "constraints", "type": "list[str]", "required": False,
     "label": {"zh": "约束与偏好", "en": "Constraints & preferences"},
     "question": {"zh": "有什么我必须知道的？（伤病史/作息/出差/恢复偏好/跑团固定场次；没有就填 []）",
                  "en": "Anything I must know? (injury history, schedule, travel, recovery, fixed club sessions; [] if none)"},
     "help": {"zh": "可以有多条，也可以留空（[]）。这条清单会影响排课与判灯。",
              "en": "Zero or more entries; [] is valid. It feeds scheduling and the light judgements."},
     "example": ["早睡早起型；周末白天可安排长距离",
                 "曾患足底筋膜炎（已愈），日常做提踵/足底放松"],
     "placeholder": "<free text / 自由文本>"},

    # ---- metric_baselines ----------------------------------------------
    {"path": "metric_baselines.resting_hr", "type": "number", "required": True,
     "range": [25, 110],
     "label": {"zh": "静息心率基线", "en": "Resting-HR baseline"},
     "question": {"zh": "晨起静息心率的常态是多少？（取近期中位数）",
                  "en": "Your usual morning resting HR? (a recent median)"},
     "help": {"zh": "黄/红灯的锚点：+8 bpm 连续 1 天＝黄，连续 2 天＝红（docs/03 §4）。",
              "en": "The light anchor: +8 bpm for 1 day = yellow, 2 consecutive days = red (docs/03 §4)."},
     "example": 50, "placeholder": "<bpm>"},
    {"path": "metric_baselines.weight_kg", "type": "number", "required": True,
     "range": [25, 200],
     "label": {"zh": "体重基线", "en": "Weight baseline"},
     "question": {"zh": "晨起空腹体重多少 kg？",
                  "en": "Morning fasted weight in kg?"},
     "help": {"zh": "只做趋势与异常波动判断，不是硬性指标。",
              "en": "Trends and unexplained swings only; never a hard rule."},
     "example": 62.0, "placeholder": "<kg>"},
    {"path": "metric_baselines.sleep_h", "type": "number", "required": True,
     "range": [2, 14],
     "label": {"zh": "睡眠基线", "en": "Sleep baseline"},
     "question": {"zh": "平时一晚睡多少小时？",
                  "en": "How many hours do you usually sleep?"},
     "help": {"zh": "用近期中位数；明显低于个人常态时会降低当周强度课负荷。",
              "en": "A recent median; clearly below your own norm cuts that week's quality load."},
     "example": 7.2, "placeholder": "<hours / 小时>"},

    # ---- devices --------------------------------------------------------
    {"path": "devices[].kind", "type": "enum", "required": True,
     "enum": ["hr_strap", "running_pod", "power_meter"],
     "label": {"zh": "配件类型", "en": "Accessory kind"},
     "question": {"zh": "什么配件？hr_strap＝心率带 / running_pod＝跑步豆 / power_meter＝功率计",
                  "en": "Which accessory? hr_strap / running_pod / power_meter"},
     "help": {"zh": "决定哪些高阶指标可用——没有对应传感器就不许在计划里引用它的指标。",
              "en": "Decides which advanced metrics exist; without the sensor the plan must not cite its metrics."},
     "example": "hr_strap", "placeholder": "<hr_strap | running_pod | power_meter>"},
    {"path": "devices[].since", "type": "date", "required": True,
     "label": {"zh": "首次出现日期", "en": "First-seen date"},
     "question": {"zh": "这个配件从哪天起出现在你的数据里？（YYYY-MM-DD）",
                  "en": "From which date does this accessory appear in your data? (YYYY-MM-DD)"},
     "help": {"zh": "这就是【数据断点】：同名字段的标尺变了，不可跨它比较（docs/02 §6.10）。",
              "en": "This IS the data break point: the ruler changes, so never trend across it (docs/02 §6.10)."},
     "example": "2027-01-05", "placeholder": "<YYYY-MM-DD>"},
    {"path": "devices[].note", "type": "str", "required": False,
     "label": {"zh": "备注（可选）", "en": "Note (optional)"},
     "question": {"zh": "型号、哪几次漏戴？（可留空）",
                  "en": "Model, which sessions it was left off? (blank to skip)"},
     "help": {"zh": "漏戴的那几次是数据盲区，写下来 agent 才不会误比。",
              "en": "Missed sessions are data blind spots; writing them down stops the agent mis-comparing."},
     "example": "HRM-Dual；2027-02-11 那次漏戴", "placeholder": "<free text / 自由文本>"},
)

# Container facts that no single field can express.
BLOCKS = {
    "identity": {"required": True, "kind": "map"},
    "races": {"required": True, "kind": "list", "min_items": 1},
    "weekly": {"required": True, "kind": "map"},
    "pr": {"required": True, "kind": "map",
           "at_least_one": ("pr.5k", "pr.10k", "pr.half", "pr.marathon")},
    "coach": {"required": True, "kind": "scalar", "validator": "coach_dir"},
    "strength": {"required": False, "kind": "map"},
    "constraints": {"required": False, "kind": "list", "min_items": 0},
    "metric_baselines": {"required": True, "kind": "map"},
    "devices": {"required": False, "kind": "list", "min_items": 0},
}

TOP_LEVEL_ORDER = tuple(
    dict.fromkeys(f["path"].split(".")[0].split("[")[0] for f in FIELDS))

# Pinned literally in --selfcheck: an accidental reorder must fail loudly, because the
# questionnaire order and the interview order both follow it.
TOP_LEVEL_ORDER_EXPECTED = ("identity", "races", "weekly", "pr", "coach", "strength",
                            "constraints", "metric_baselines", "devices")

_LABELS = {
    "zh": {"required": "*必填*", "optional": "(可选)", "q": "问：", "help": "说明：",
           "example": "示例：", "current": "当前：", "answer": "> ",
           "list_hint": "可有多项"},
    "en": {"required": "*required*", "optional": "(optional)", "q": "Q: ", "help": "help: ",
           "example": "example: ", "current": "current: ", "answer": "> ",
           "list_hint": "repeatable"},
}
_LABELS["en"]["list_hint"] = "repeatable block"


def _block_of(path):
    """'races[].name' -> 'races'; 'coach' -> 'coach'."""
    return path.split(".")[0].split("[")[0]


def _child_of(path):
    """'races[].name' -> 'name'; 'coach' -> None."""
    return path.split(".", 1)[1] if "." in path else None


def _is_list_item(path):
    return "[]" in path


def _specs_of(block):
    return tuple(f for f in FIELDS if _block_of(f["path"]) == block)


def _find_spec(path):
    for f in FIELDS:
        if _block_of(f["path"]) == _block_of(path) and _child_of(f["path"]) == _child_of(path):
            return f
    return None


def _list_item_blocks():
    """Top-level blocks whose items are mappings, derived from FIELDS (no second schema)."""
    return tuple(b for b in TOP_LEVEL_ORDER
                 if any(_is_list_item(f["path"]) for f in _specs_of(b)))


# ===========================================================================
# Restricted YAML-subset parser
# ===========================================================================

class YamlSubsetError(ValueError):
    def __init__(self, line, col, msg):
        super(YamlSubsetError, self).__init__(
            "line %d, column %d: %s" % (line, col, msg))
        self.line = line
        self.col = col
        self.msg = msg


class _Line(object):
    __slots__ = ("no", "indent", "text", "raw")

    def __init__(self, no, indent, text, raw):
        self.no = no
        self.indent = indent
        self.text = text
        self.raw = raw


_RE_INT = re.compile(r"^[+-]?\d+$")
_RE_FLOAT = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?$")
_RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RE_TIME_MS = re.compile(r"^\d{1,3}:[0-5]\d$")
_RE_TIME_HMS = re.compile(r"^\d{1,2}:[0-5]\d:[0-5]\d$")
_RE_PLACEHOLDER = re.compile(r"^<.*>$")

_REJECT_MSGS = {
    "flow_map": "flow mappings ('{...}') are not supported; use block style",
    "block_scalar": "block scalars ('|' / '>') are not supported; use a single-line quoted string",
    "anchor": "anchors ('&') are not supported",
    "alias": "aliases ('*') are not supported",
    "merge": "merge keys ('<<') are not supported",
    "tag": "tags ('!') are not supported",
}


def _strip_comment(s, in_d=False, in_s=False):
    """Strip a comment from `s`, quote-aware. Returns (content, in_double, in_single).

    The quote state is threaded in and out because a quoted scalar may span physical lines.
    A '#' only starts a comment at line start or after whitespace, and never inside quotes —
    which is exactly what keeps `note: "a # b"` intact.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if in_d:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(s[i + 1])
                i += 2
                continue
            if ch == '"':
                in_d = False
        elif in_s:
            if ch == "'" and i + 1 < n and s[i + 1] == "'":
                out.append("''")
                i += 2
                continue
            out.append(ch)
            if ch == "'":
                in_s = False
        elif ch == '"':
            in_d = True
            out.append(ch)
        elif ch == "'":
            in_s = True
            out.append(ch)
        elif ch == "#" and (i == 0 or s[i - 1] in " \t"):
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out).rstrip(), in_d, in_s


def _scan(text):
    """Split text into logical lines: (indent, comment-stripped text), folding quoted scalars."""
    raw_lines = text.split("\n")
    if raw_lines and raw_lines[0].startswith("\ufeff"):
        raw_lines[0] = raw_lines[0][1:]

    out = []
    i = 0
    while i < len(raw_lines):
        raw = raw_lines[i].rstrip("\r")
        no = i + 1
        consumed = [raw]
        i += 1
        j = 0
        while j < len(raw) and raw[j] in " \t":
            j += 1
        lead = raw[:j]
        if "\t" in lead:
            raise YamlSubsetError(no, lead.index("\t") + 1,
                                  "tab character in indentation (use spaces)")
        indent = j
        content, in_d, in_s = _strip_comment(raw[j:])
        while in_d or in_s:
            if i >= len(raw_lines):
                raise YamlSubsetError(no, indent + 1, "unterminated quoted string")
            cont = raw_lines[i].rstrip("\r")
            consumed.append(cont)
            piece, in_d, in_s = _strip_comment(cont.strip(), in_d, in_s)
            i += 1
            content = content + " " + piece
        content = content.strip()
        if not content or content == "---":
            continue
        out.append(_Line(no, indent, content, "\n".join(consumed)))
    return out, raw_lines


def _decode_scalar(s, no, col):
    """Plain/quoted scalar -> value. Quoted scalars always stay strings."""
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        body = s[1:-1]
        return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), body)
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].replace("''", "'")
    if s in ("", "~", "null", "Null", "NULL"):
        return None
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    if _RE_INT.match(s):
        return int(s)
    if _RE_FLOAT.match(s):
        return float(s)
    return s


def _decode_flow_seq(s, no, col):
    if not s.endswith("]"):
        raise YamlSubsetError(no, col, "unterminated flow sequence '['")
    inner = s[1:-1].strip()
    if inner == "":
        return []
    parts = []
    buf = []
    in_d = in_s = False
    for ch in inner:
        if in_d:
            buf.append(ch)
            if ch == '"':
                in_d = False
        elif in_s:
            buf.append(ch)
            if ch == "'":
                in_s = False
        elif ch == '"':
            in_d = True
            buf.append(ch)
        elif ch == "'":
            in_s = True
            buf.append(ch)
        elif ch == ",":
            parts.append("".join(buf))
            buf = []
        elif ch == "[":
            raise YamlSubsetError(no, col, "nested flow sequences are not supported")
        elif ch == "{":
            raise YamlSubsetError(no, col, _REJECT_MSGS["flow_map"])
        else:
            buf.append(ch)
    parts.append("".join(buf))
    if in_d or in_s:
        raise YamlSubsetError(no, col, "unterminated quoted string")
    values = []
    for p in parts:
        p = p.strip()
        if p == "":
            raise YamlSubsetError(no, col, "trailing comma in flow sequence")
        values.append(_decode_scalar(p, no, col))
    return values


def _decode_value(s, no, col):
    """Decode an inline value token, rejecting the unsupported constructs."""
    if s.startswith("{"):
        raise YamlSubsetError(no, col, _REJECT_MSGS["flow_map"])
    if s.startswith("|") or s.startswith(">"):
        raise YamlSubsetError(no, col, _REJECT_MSGS["block_scalar"])
    if s.startswith("&"):
        raise YamlSubsetError(no, col, _REJECT_MSGS["anchor"])
    if s.startswith("*"):
        raise YamlSubsetError(no, col, _REJECT_MSGS["alias"])
    if s.startswith("!"):
        raise YamlSubsetError(no, col, _REJECT_MSGS["tag"])
    if s.startswith("["):
        return _decode_flow_seq(s, no, col)
    return _decode_scalar(s, no, col)


def _split_key(text, no, col):
    """Split 'key: value'. Returns (key, value-or-None) or None if this is not a mapping entry.

    The split point is the first ':' that is outside quotes AND followed by whitespace or the
    end of line — that is what keeps `5k: 23:45` and `marathon: 3:54:04` correct.
    """
    in_d = in_s = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if in_d:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                in_d = False
        elif in_s:
            if ch == "'" and i + 1 < n and text[i + 1] == "'":
                i += 2
                continue
            if ch == "'":
                in_s = False
        elif ch == '"':
            in_d = True
        elif ch == "'":
            in_s = True
        elif ch == ":" and (i + 1 == n or text[i + 1] in " \t"):
            key = text[:i].strip()
            if not key:
                raise YamlSubsetError(no, col + i, "empty key")
            if key == "<<":
                raise YamlSubsetError(no, col + i, _REJECT_MSGS["merge"])
            val = text[i + 1:].strip()
            return key, (val if val != "" else None)
        i += 1
    return None


def _is_entry(line):
    if line.text == "-" or line.text.startswith("- "):
        return True
    return _split_key(line.text, line.no, line.indent + 1) is not None


def _fold_continuation(text, lines, pos, indent):
    """Fold plain-scalar continuation lines (deeper than `indent`, not entries) into `text`."""
    while pos < len(lines):
        nxt = lines[pos]
        if nxt.indent <= indent or _is_entry(nxt):
            break
        text = (text + " " + nxt.text).strip()
        pos += 1
    return text, pos


def _parse_block(lines, pos, indent, unknown=None, known_top=None):
    if lines[pos].text == "-" or lines[pos].text.startswith("- "):
        return _parse_sequence(lines, pos, indent)
    return _parse_mapping(lines, pos, indent, {}, unknown, known_top)


def _parse_sequence(lines, pos, indent):
    items = []
    while pos < len(lines):
        ln = lines[pos]
        if ln.indent < indent:
            break
        if ln.indent > indent:
            raise YamlSubsetError(ln.no, ln.indent + 1,
                                  "inconsistent indentation: expected indent %d, got %d"
                                  % (indent, ln.indent))
        if not (ln.text == "-" or ln.text.startswith("- ")):
            raise YamlSubsetError(ln.no, ln.indent + 1, "expected '- item'")
        rest = ln.text[1:].strip()
        pos += 1
        if rest == "":
            if pos < len(lines) and lines[pos].indent > indent:
                value, pos = _parse_block(lines, pos, lines[pos].indent)
            else:
                value = None
            items.append(value)
            continue
        entry = _split_key(rest, ln.no, ln.indent + 3)
        if entry is None:
            value = _decode_value(rest, ln.no, ln.indent + 3)
            if isinstance(value, str):
                value, pos = _fold_continuation(value, lines, pos, indent)
            items.append(value)
            continue
        # "- key: value" starts a mapping item; its remaining keys sit at a deeper indent.
        key, val = entry
        item = {}
        if val is None:
            if pos < len(lines) and lines[pos].indent > indent:
                item[key], pos = _parse_block(lines, pos, lines[pos].indent)
            else:
                item[key] = None
        else:
            item[key] = _decode_value(val, ln.no, ln.indent + 3)
            if isinstance(item[key], str):
                item[key], pos = _fold_continuation(item[key], lines, pos, indent)
        if pos < len(lines) and lines[pos].indent > indent:
            _, pos = _parse_mapping(lines, pos, lines[pos].indent, item, None, None)
        items.append(item)
    return items, pos


def _parse_mapping(lines, pos, indent, node, unknown, known_top):
    while pos < len(lines):
        ln = lines[pos]
        if ln.indent < indent:
            break
        if ln.indent > indent:
            raise YamlSubsetError(ln.no, ln.indent + 1,
                                  "inconsistent indentation: expected indent %d, got %d"
                                  % (indent, ln.indent))
        entry = _split_key(ln.text, ln.no, ln.indent + 1)
        if entry is None:
            raise YamlSubsetError(ln.no, ln.indent + 1, "expected 'key: value' or '- item'")
        key, val = entry
        if unknown is not None and known_top is not None and key not in known_top:
            pos = _capture_unknown(lines, pos, key, unknown)
            continue
        if key in node:
            raise YamlSubsetError(ln.no, ln.indent + 1, "duplicate key '%s'" % key)
        pos += 1
        if val is None:
            if pos < len(lines) and lines[pos].indent > indent:
                node[key], pos = _parse_block(lines, pos, lines[pos].indent)
            else:
                node[key] = None
        else:
            node[key] = _decode_value(val, ln.no, ln.indent + 1)
            if isinstance(node[key], str):
                node[key], pos = _fold_continuation(node[key], lines, pos, indent)
    return node, pos


def _capture_unknown(lines, pos, key, unknown):
    """Record an unknown top-level block verbatim and skip over it without parsing."""
    start = pos
    pos += 1
    while pos < len(lines) and lines[pos].indent > 0:
        pos += 1
    unknown[key] = [l.raw for l in lines[start:pos]]
    return pos


def parse_yaml_subset(text, known_top=TOP_LEVEL_ORDER):
    """Parse the restricted subset. Returns (data, unknown_top_level_blocks).

    `known_top` is what makes a hand-maintained extension block (e.g. the runner's private
    `measured:`) survive untouched: any top-level key outside it is captured verbatim and
    never parsed, so it cannot trip the subset restrictions. Pass `known_top=None` for a
    strict, schema-agnostic parse (used by the embedded rejection spec in --selfcheck).
    """
    lines, _raw = _scan(text)
    if not lines:
        return {}, {}
    if lines[0].indent != 0:
        raise YamlSubsetError(lines[0].no, lines[0].indent + 1,
                              "the document must start at indentation 0")
    unknown = {} if known_top is not None else None
    data, pos = _parse_mapping(lines, 0, 0, {}, unknown, known_top)
    if pos < len(lines):
        raise YamlSubsetError(lines[pos].no, lines[pos].indent + 1, "unexpected content")
    return data, (unknown or {})


def parse_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return parse_yaml_subset(f.read())


# ===========================================================================
# Rendering (block style only, LF, no BOM, no timestamps)
# ===========================================================================

_NEEDS_QUOTE = set('#:[]{},&*|><!%@`"\'')


def _fmt_scalar(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v) if isinstance(v, float) else str(v)
    s = str(v)
    plain_ok = bool(s) and s.strip() == s
    if plain_ok:
        for ch in s:
            if ch in _NEEDS_QUOTE:
                plain_ok = False
                break
    if plain_ok and (s[0].isdigit() or _RE_INT.match(s) or _RE_FLOAT.match(s)
                     or s.lower() in ("true", "false", "null", "~")):
        plain_ok = False
    if not plain_ok:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'
    return s


def _render_value(lines, key, value, indent):
    pad = " " * indent
    if isinstance(value, dict):
        if not value:
            lines.append("%s%s: {}" % (pad, key))
            return
        lines.append("%s%s:" % (pad, key))
        for k in _ordered_keys(value):
            _render_value(lines, k, value[k], indent + 2)
        return
    if isinstance(value, list):
        if not value:
            lines.append("%s%s: []" % (pad, key))
            return
        lines.append("%s%s:" % (pad, key))
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append("%s  - {}" % pad)
                    continue
                keys = _ordered_keys(item)
                first = keys[0]
                if isinstance(item[first], (dict, list)):
                    lines.append("%s  - %s:" % (pad, first))
                    _render_value(lines, first, item[first], indent + 4)
                else:
                    lines.append("%s  - %s: %s" % (pad, first, _fmt_scalar(item[first])))
                for k in keys[1:]:
                    _render_value(lines, k, item[k], indent + 4)
            else:
                lines.append("%s  - %s" % (pad, _fmt_scalar(item)))
        return
    lines.append("%s%s: %s" % (pad, key, _fmt_scalar(value)))


def _ordered_keys(d):
    known = [k for k in TOP_LEVEL_ORDER if k in d]
    rest = sorted(k for k in d if k not in TOP_LEVEL_ORDER)
    return known + rest


def _ordered_item_keys(block, item):
    order = [(_child_of(f["path"]) or "") for f in _specs_of(block)]
    return [k for k in order if k in item] + sorted(k for k in item if k not in order)


def render_yaml_subset(data, unknown=None, header=(), newline="\n"):
    """Render a profile dict back to the restricted subset (block style only)."""
    lines = []
    for h in header:
        lines.append("# %s" % h if h else "#")
    if header:
        lines.append("")
    for key in _ordered_keys(data):
        value = data[key]
        if isinstance(value, list) and value and isinstance(value[0], dict):
            lines.append("%s:" % key)
            for item in value:
                keys = _ordered_item_keys(key, item)
                first = keys[0]
                if isinstance(item[first], (dict, list)):
                    lines.append("  - %s:" % first)
                    _render_value(lines, first, item[first], 4)
                else:
                    lines.append("  - %s: %s" % (first, _fmt_scalar(item[first])))
                for k in keys[1:]:
                    _render_value(lines, k, item[k], 4)
        else:
            _render_value(lines, key, value, 0)
    if unknown:
        for key in sorted(unknown):
            if lines:
                lines.append("")
            lines.append("# " + "-" * 74)
            lines.append("# Preserved unknown top-level block '%s' — not part of the documented" % key)
            lines.append("# schema and NOT edited by the wizard. Original text kept verbatim.")
            lines.append("# 未知顶层块：原样保留，向导不编辑。")
            lines.append("# " + "-" * 74)
            lines.extend(unknown[key])
    text = newline.join(lines)
    if not text.endswith(newline):
        text += newline
    return text


# ===========================================================================
# Derived artifacts: question list and fillable questionnaire
# ===========================================================================

def questions_text(lang="zh"):
    """The canonical, ordered question list — used by the interview prompt and by agents."""
    if lang not in _LABELS:
        raise ValueError("unknown language %r" % lang)
    L = _LABELS[lang]
    out = ["# runner profile questions — %s · %d fields" % (lang, len(FIELDS)),
           "# source of truth: scripts/profile_wizard.py FIELDS — do not edit by hand",
           ""]
    current = None
    n = 0
    for spec in FIELDS:
        block = _block_of(spec["path"])
        if block != current:
            current = block
            note = ""
            if block in _list_item_blocks():
                note = "  [%s]" % L["list_hint"]
            out.append("[%s]%s" % (block, note))
        n += 1
        tag = L["required"] if spec.get("required") else L["optional"]
        extra = "  [%s]" % "|".join(spec["enum"]) if spec.get("type") == "enum" else ""
        out.append("%d. %s   %s%s" % (n, spec["path"], tag, extra))
        out.append("   %s%s" % (L["q"], spec["question"][lang]))
        out.append("   %s%s" % (L["help"], spec["help"][lang]))
        out.append("   %s%s" % (L["example"], spec["example"]))
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def _questionnaire_placeholder(spec):
    return spec.get("placeholder", "<value>")


def questionnaire_text():
    """A fillable, empty questionnaire generated from FIELDS (committed under examples/)."""
    out = [
        "# Garmin-Dashboard · runner profile questionnaire / 跑者档案问卷",
        "#",
        "# Fill this in and save it as workspace/runner_profile.yaml, then run:",
        "#     python scripts/profile_wizard.py --check workspace/runner_profile.yaml",
        "# 填好后另存为 workspace/runner_profile.yaml，再跑上面这条命令校验。",
        "#",
        "# Rules / 规则:",
        "#   · replace every <...> placeholder; leave a value out (delete the line) if it is optional",
        "#     （把每个 <...> 占位符换成你的答案；可选字段不需要就整行删掉）",
        "#   · block style only: no {flow: mappings}, no |block scalars, no tabs",
        "#     （只用块状写法：不要 {} 流式映射、不要 | 块标量、不要 tab 缩进）",
        "#   · schedule reference / 排期与判灯依据: docs/03, docs/06, docs/08",
        "#   · at most ONE race may have role: A （只能有一场比赛是 role: A）",
        "#",
        "# This file is generated from scripts/profile_wizard.py FIELDS — regenerate with",
        "#     python scripts/profile_wizard.py --emit-questionnaire",
        "# 本文件由 FIELDS 生成，改字段后要重新生成（--selfcheck 会检查）。",
        "",
    ]
    for block in TOP_LEVEL_ORDER:
        specs = _specs_of(block)
        kind = BLOCKS[block]["kind"]
        if kind == "scalar":
            spec = specs[0]
            _emit_questionnaire_comments(out, spec, "")
            out.append("%s: %s" % (block, _questionnaire_placeholder(spec)))
        elif block in _list_item_blocks():
            out.append("%s:" % block)
            out.append("  # %s · 每个条目重复这一整块 / repeat this block for each item"
                       % _LABELS["zh"]["list_hint"])
            _emit_questionnaire_items(out, specs, "  ")
        elif kind == "list":
            _emit_questionnaire_comments(out, specs[0], "")
            out.append("%s: []" % block)
        else:
            out.append("%s:" % block)
            for spec in specs:
                _emit_questionnaire_scalar(out, spec, "  ", _child_of(spec["path"]))
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def _emit_questionnaire_comments(out, spec, lead):
    ex = spec["example"]
    if isinstance(ex, dict):
        ex = ", ".join("%s: %s" % (k, v) for k, v in sorted(ex.items()))
    elif isinstance(ex, list):
        ex = " / ".join(str(x) for x in ex)
    out.append("%s# 问：%s｜说明：%s" % (lead, spec["question"]["zh"], spec["help"]["zh"]))
    out.append("%s# Q: %s (example: %s)" % (lead, spec["question"]["en"], ex))


def _emit_questionnaire_scalar(out, spec, pad, key):
    _emit_questionnaire_comments(out, spec, pad)
    if key is None:
        out.append("%s%s" % (pad, _questionnaire_placeholder(spec)))
        return
    if spec["type"] == "map":
        out.append("%s%s:" % (pad, key))
        for day in WEEKDAYS:
            out.append("%s  %s: %s" % (pad, day, _questionnaire_placeholder(spec)))
        out.append("%s  # 不跑/不练的天整行删掉 · delete the lines you do not use" % pad)
        return
    if spec["type"] == "list[weekday]":
        out.append("%s%s: []" % (pad, key))
        return
    out.append("%s%s: %s" % (pad, key, _questionnaire_placeholder(spec)))


def _emit_questionnaire_items(out, specs, pad):
    for idx, spec in enumerate(specs):
        key = _child_of(spec["path"])
        if idx == 0:
            out.append("%s# --- item 1 ---" % pad)
            _emit_questionnaire_comments(out, spec, pad)
            lead = "%s- " % pad
        else:
            _emit_questionnaire_comments(out, spec, pad + "  ")
            lead = "%s  " % pad
        out.append("%s%s: %s" % (lead, key, _questionnaire_placeholder(spec)))


# ===========================================================================
# Validation
# ===========================================================================

class Issue(object):
    __slots__ = ("severity", "path", "message")

    def __init__(self, severity, path, message):
        self.severity = severity
        self.path = path
        self.message = message

    def __str__(self):
        return "%s  %s: %s" % ("ERROR" if self.severity == "error" else "WARN ", self.path,
                               self.message)


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _as_str(v):
    return v if isinstance(v, str) else None


def _check_weekday_name(v):
    if not isinstance(v, str):
        return False
    for d in WEEKDAYS:
        if v.strip().lower() == d.lower():
            return True
    return False


def _parse_date(v):
    if not isinstance(v, str) or not _RE_DATE.match(v):
        return None
    try:
        return datetime.date(int(v[0:4]), int(v[5:7]), int(v[8:10]))
    except ValueError:
        return None


def _check_scalar_value(spec, value, path, issues):
    """Type/enum/format checks for one leaf value. Returns True when the value is usable."""
    t = spec["type"]
    if value is None:
        return False
    if isinstance(value, str):
        if _RE_PLACEHOLDER.match(value.strip()):
            issues.append(Issue("error", path,
                                "value is still a template placeholder (%s)" % value.strip()))
            return False
        if value.strip().lower() in UNFILLED:
            issues.append(Issue("warn", path,
                                "not filled in yet (%s) — the runner still owes this answer"
                                % value.strip()))
    if t == "str":
        if not isinstance(value, str):
            issues.append(Issue("error", path, "expected a string, got %s" % type(value).__name__))
            return False
        if not value.strip():
            issues.append(Issue("error", path, "must not be empty"))
            return False
        return True
    if t == "int":
        if not _is_int(value):
            issues.append(Issue("error", path, "expected an integer, got %r" % (value,)))
            return False
        _range_warn(spec, value, path, issues)
        return True
    if t == "number":
        if not _is_number(value):
            issues.append(Issue("error", path, "expected a number, got %r" % (value,)))
            return False
        _range_warn(spec, value, path, issues)
        return True
    if t == "enum":
        if not isinstance(value, str) or value.lower() not in [e.lower() for e in spec["enum"]]:
            issues.append(Issue("error", path, "must be one of %s (got %r)"
                                % ("|".join(spec["enum"]), value)))
            return False
        return True
    if t == "date":
        if not isinstance(value, str) or _RE_DATE.match(value) is None or _parse_date(value) is None:
            issues.append(Issue("error", path, "expected YYYY-MM-DD (got %r)" % (value,)))
            return False
        return True
    if t == "time":
        pat = _RE_TIME_MS if spec.get("format") == "MM:SS" else _RE_TIME_HMS
        if not isinstance(value, str) or pat.match(value) is None:
            issues.append(Issue("error", path, "expected %s (got %r)"
                                % (spec.get("format", "MM:SS"), value)))
            return False
        return True
    if t == "weekday":
        if not _check_weekday_name(value):
            issues.append(Issue("error", path, "%r is not a weekday" % (value,)))
            return False
        return True
    issues.append(Issue("error", path, "unknown field type %r" % t))
    return False


def _range_warn(spec, value, path, issues):
    rng = spec.get("range")
    if rng and _is_number(value) and not (rng[0] <= value <= rng[1]):
        issues.append(Issue("warn", path, "%r is outside the plausible range %s-%s"
                            % (value, rng[0], rng[1])))


def _check_map(spec, value, path, issues):
    if not isinstance(value, dict):
        issues.append(Issue("error", path, "expected a mapping of day -> value, got %s"
                            % type(value).__name__))
        return False
    ok = True
    for k, v in value.items():
        if not _check_weekday_name(k):
            issues.append(Issue("error", path, "%r is not a weekday" % (k,)))
            ok = False
            continue
        if spec.get("value_type") == "enum":
            if not isinstance(v, str) or v.lower() not in [e.lower() for e in spec["value_enum"]]:
                issues.append(Issue("error", "%s.%s" % (path, k), "must be one of %s (got %r)"
                                    % ("|".join(spec["value_enum"]), v)))
                ok = False
        else:
            if not isinstance(v, str) or not v.strip():
                issues.append(Issue("error", "%s.%s" % (path, k), "expected a non-empty string"))
                ok = False
    return ok


def _check_unknown_children(block, value, issues, path):
    """Unknown keys inside a KNOWN block are errors (only top-level unknowns are tolerated)."""
    declared = set()
    for spec in _specs_of(block):
        child = _child_of(spec["path"])
        if child:
            declared.add(child)
    if not declared:
        return
    if isinstance(value, dict):
        for k in value:
            if k not in declared:
                issues.append(Issue("error", "%s.%s" % (path, k), "unknown field"))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            if isinstance(item, dict):
                for k in item:
                    if k not in declared:
                        issues.append(Issue("error", "%s[%d].%s" % (path, i, k), "unknown field"))


def _get(data, path):
    node = data
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def validate(data, unknown=None, root=REPO_ROOT):
    """Validate a parsed profile. Returns a list of Issue (errors block, warnings do not)."""
    issues = []
    unknown = unknown or {}
    if not isinstance(data, dict):
        issues.append(Issue("error", "<root>", "expected a mapping of profile blocks"))
        return issues

    for key in sorted(unknown):
        issues.append(Issue("warn", key, "unknown top-level key (ignored)"))

    for block in TOP_LEVEL_ORDER:
        spec_block = BLOCKS[block]
        value = data.get(block)
        if value is None:
            if spec_block["required"]:
                issues.append(Issue("error", block, "missing required block"))
            continue
        kind = spec_block["kind"]
        if kind == "scalar":
            _check_scalar_value(_find_spec(block), value, block, issues)
            if spec_block.get("validator") == "coach_dir" and isinstance(value, str):
                d = os.path.join(SKILLS_DIR, "coach-" + value.replace("_", "-"))
                if not os.path.isdir(d):
                    issues.append(Issue("error", block,
                                        "%r does not resolve to .agents/skills/coach-%s/"
                                        % (value, value.replace("_", "-"))))
        elif kind == "list":
            if not isinstance(value, list):
                issues.append(Issue("error", block, "expected a list, got %s"
                                    % type(value).__name__))
                continue
            if len(value) < spec_block.get("min_items", 0):
                issues.append(Issue("error", block, "needs at least %d item(s)"
                                    % spec_block["min_items"]))
            if block in _list_item_blocks():
                for i, item in enumerate(value):
                    if not isinstance(item, dict):
                        issues.append(Issue("error", "%s[%d]" % (block, i),
                                            "expected a mapping, got %s" % type(item).__name__))
                        continue
                    _check_mapping_block(block, item, "%s[%d]" % (block, i), issues)
            else:
                for i, item in enumerate(value):
                    if not isinstance(item, str) or not item.strip():
                        issues.append(Issue("error", "%s[%d]" % (block, i),
                                            "expected a non-empty string"))
                    elif _RE_PLACEHOLDER.match(item.strip()):
                        issues.append(Issue("error", "%s[%d]" % (block, i),
                                            "value is still a template placeholder (%s)"
                                            % item.strip()))
        else:
            if not isinstance(value, dict):
                issues.append(Issue("error", block, "expected a block, got %s"
                                    % type(value).__name__))
                continue
            _check_mapping_block(block, value, block, issues)

    # ---- cross-field rules ---------------------------------------------
    races = data.get("races")
    if isinstance(races, list):
        a_races = [r for r in races if isinstance(r, dict)
                   and isinstance(r.get("role"), str) and r["role"].lower() == "a"]
        if len(a_races) > 1:
            names = ", ".join(repr(r.get("name")) for r in a_races)
            issues.append(Issue("error", "races",
                                "at most one role: A race per cycle (found %d: %s)"
                                % (len(a_races), names)))
        elif not a_races:
            issues.append(Issue("warn", "races", "no role: A race — the cycle has no anchor"))
    pr = data.get("pr")
    if isinstance(pr, dict) and all(pr.get(k) in (None, "") for k in
                                    ("5k", "10k", "half", "marathon")):
        issues.append(Issue("error", "pr", "at least one PR entry is required to derive VDOT"))

    _weekly_warnings(data, issues)
    _identity_warnings(data, issues)
    return issues


def _check_mapping_block(block, value, path, issues):
    _check_unknown_children(block, value, issues, path)
    for spec in _specs_of(block):
        child = _child_of(spec["path"])
        if child is None:
            continue
        if child not in value or value[child] is None:
            if spec.get("required"):
                issues.append(Issue("error", "%s.%s" % (path, child), "missing required field"))
            continue
        v = value[child]
        t = spec["type"]
        if t == "map":
            _check_map(spec, v, "%s.%s" % (path, child), issues)
        elif t == "list[str]":
            if not isinstance(v, list) or any(not isinstance(x, str) for x in v):
                issues.append(Issue("error", "%s.%s" % (path, child),
                                    "expected a list of strings"))
        elif t == "list[weekday]":
            if not isinstance(v, list):
                issues.append(Issue("error", "%s.%s" % (path, child),
                                    "expected a list of weekdays (e.g. [Tuesday])"))
            else:
                for i, x in enumerate(v):
                    if not _check_weekday_name(x):
                        issues.append(Issue("error", "%s.%s[%d]" % (path, child, i),
                                            "%r is not a weekday" % (x,)))
        else:
            _check_scalar_value(spec, v, "%s.%s" % (path, child), issues)


def _weekly_warnings(data, issues):
    weekly = data.get("weekly")
    if not isinstance(weekly, dict):
        return
    days = weekly.get("days")
    if isinstance(days, dict):
        mapped = [k for k in days if _check_weekday_name(k)]
        n = weekly.get("runs_per_week")
        if _is_int(n) and n != len(mapped):
            issues.append(Issue("warn", "weekly",
                                "runs_per_week is %d but weekly.days maps %d day(s)"
                                % (n, len(mapped))))
        lrd = weekly.get("long_run_day")
        if _check_weekday_name(lrd) and lrd.strip().lower() not in [d.lower() for d in mapped]:
            issues.append(Issue("warn", "weekly.long_run_day",
                                "%s is not listed in weekly.days" % lrd))
        qd = weekly.get("quality_days")
        if isinstance(qd, list):
            for d in qd:
                for k, v in days.items():
                    if isinstance(d, str) and isinstance(v, str) and \
                            k.strip().lower() == d.strip().lower() and v.lower() != "quality":
                        issues.append(Issue("warn", "weekly.quality_days",
                                            "%s is listed as quality but weekly.days says %r"
                                            % (d, v)))
    if weekly.get("max_run_min") is not None and not _is_int(weekly.get("max_run_min")):
        pass  # already reported by the field check


def _identity_warnings(data, issues):
    ident = data.get("identity")
    if not isinstance(ident, dict):
        return
    if ident.get("birth_year") is not None and ident.get("sex") is None:
        issues.append(Issue("warn", "identity.birth_year",
                            "set without identity.sex — age-graded VDOT stays disabled"))
    tz = ident.get("timezone")
    if isinstance(tz, str) and "/" not in tz:
        issues.append(Issue("warn", "identity.timezone",
                            "%r does not look like an IANA timezone (Area/City)" % tz))


def counts(issues):
    return (sum(1 for i in issues if i.severity == "error"),
            sum(1 for i in issues if i.severity == "warn"))


# ===========================================================================
# CLI
# ===========================================================================

def _print_issues(issues, path):
    for issue in issues:
        print(str(issue))
    n_err, n_warn = counts(issues)
    if issues:
        print("")
    if n_err:
        print("%s: %d error(s), %d warning(s)" % (path, n_err, n_warn))
    elif n_warn:
        print("%s: OK (0 errors, %d warning(s))" % (path, n_warn))
    else:
        print("%s: OK (0 errors, 0 warnings)" % path)


def cmd_check(path):
    if not os.path.exists(path):
        sys.stderr.write("ERROR: no such file: %s\n" % path)
        return 2
    try:
        data, unknown = parse_file(path)
    except YamlSubsetError as exc:
        print("ERROR  %s:%d:%d: %s" % (path, exc.line, exc.col, exc.msg))
        return 1
    issues = validate(data, unknown)
    _print_issues(issues, path)
    return 1 if counts(issues)[0] else 0


def _atomic_write_text(path, text, newline="\n"):
    """Temp file + os.replace, so a crash mid-write cannot leave a half-written profile."""
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    payload = text.replace("\r\n", "\n").replace("\n", newline)
    fd, tmp = tempfile.mkstemp(dir=d or ".", prefix=".runner_profile.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(payload)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def cmd_emit_questionnaire(path):
    old = None
    if os.path.exists(path):
        with open(path, "rb") as f:
            old = f.read()
    text = questionnaire_text()
    _atomic_write_text(path, text, "\n")
    with open(path, "rb") as f:
        new = f.read()
    print("%s: %s (%d bytes)" % (path, "unchanged" if old == new else "written", len(new)))
    return 0


# ---- interactive wizard -------------------------------------------------

def _ask(prompt):
    return input(prompt)


def _print_spec(spec, lang, current):
    L = _LABELS[lang]
    print("%s  %s  %s" % (spec["path"], spec["label"][lang],
                          L["required"] if spec.get("required") else L["optional"]))
    print("        %s%s" % (L["q"], spec["question"][lang]))
    print("        %s%s" % (L["help"], spec["help"][lang]))
    print("        %s%s" % (L["example"], spec["example"]))
    if current is not None:
        print("        %s%r" % (L["current"], current))


def _ask_value(spec, lang, current):
    _print_spec(spec, lang, current)
    return _ask("    %s" % _LABELS[lang]["answer"]).strip()


def _coerce_input(spec, raw, lang):
    """Turn a typed answer into a value, or return (None, error-message)."""
    t = spec["type"]
    if t == "int":
        if _RE_INT.match(raw):
            return int(raw), None
        return None, "需要一个整数 / an integer is required"
    if t in ("number",):
        if _RE_FLOAT.match(raw):
            return float(raw), None
        return None, "需要一个数字 / a number is required"
    if t == "date":
        if _parse_date(raw):
            return raw, None
        return None, "格式应为 YYYY-MM-DD / expected YYYY-MM-DD"
    if t == "time":
        pat = _RE_TIME_MS if spec.get("format") == "MM:SS" else _RE_TIME_HMS
        if pat.match(raw):
            return raw, None
        return None, "格式应为 %s / expected %s" % (spec.get("format"), spec.get("format"))
    if t == "enum":
        for e in spec["enum"]:
            if raw.lower() == e.lower():
                return e, None
        return None, "取值必须是 %s / must be one of %s" % ("|".join(spec["enum"]),
                                                          "|".join(spec["enum"]))
    if t == "weekday":
        for d in WEEKDAYS:
            if raw.lower() == d.lower():
                return d, None
        return None, "不是星期几 / not a weekday"
    if t == "list[weekday]":
        out = []
        for piece in re.split(r"[,，]", raw):
            piece = piece.strip()
            if not piece:
                continue
            got, err = _coerce_input({"type": "weekday"}, piece, lang)
            if err:
                return None, err
            out.append(got)
        return out, None
    if t == "list[str]":
        return [p.strip() for p in re.split(r"[,，]", raw) if p.strip()], None
    return raw, None


def _coerce_map_value(spec, raw):
    """Coerce one answer for a weekday->value mapping field."""
    if spec.get("value_type") == "enum":
        for e in spec["value_enum"]:
            if raw.lower() == e.lower():
                return e, None
        return None, "取值必须是 %s / must be one of %s" % ("|".join(spec["value_enum"]),
                                                          "|".join(spec["value_enum"]))
    if not raw.strip():
        return None, "不能为空 / must not be empty"
    return raw.strip(), None


def _interview(data, lang):
    """Ask every field in FIELDS order, prefilled from `data`. Uses input() (patchable)."""
    out = {}
    total = len(FIELDS)
    for idx, spec in enumerate(FIELDS, 1):
        path = spec["path"]
        block, child = _block_of(path), _child_of(path)
        if _is_list_item(path):
            continue  # handled with its block below
        current = _get(data, path) if "." in path else data.get(block)
        tries = 0
        print("\n[%d/%d]" % (idx, total))
        if spec["type"] == "map":
            _print_spec(spec, lang, current)
            old = current if isinstance(current, dict) else {}
            got = {}
            for day in WEEKDAYS:
                cur = old.get(day)
                mark = ("  [%s]" % cur) if cur is not None else ""
                raw = _ask("    %s%s > " % (day, mark)).strip()
                if raw == "":
                    if cur is not None:
                        got[day] = cur
                    continue
                value, err = _coerce_map_value(spec, raw)
                if err:
                    print("        %s" % err)
                    continue
                got[day] = value
            if got:
                out.setdefault(block, {})[child] = got
            continue
        while True:
            raw = _ask_value(spec, lang, current)
            if raw == "":
                if current is not None:
                    break
                if not spec.get("required"):
                    break
                tries += 1
                if tries >= 3:
                    print("        （仍未填写，先跳过 / still blank — moving on）")
                    break
                print("        （必填，请给一个值 / required — please answer）")
                continue
            value, err = _coerce_input(spec, raw, lang)
            if err:
                print("        %s" % err)
                continue
            current = value
            break
        if current is None:
            continue
        if "." in path:
            out.setdefault(block, {})
            if isinstance(out[block], dict):
                out[block][child] = current
        else:
            out[block] = current

    for block in _list_item_blocks():
        specs = _specs_of(block)
        print("\n[%s] %s" % (block, _LABELS[lang]["list_hint"]))
        items = []
        existing = data.get(block)
        if isinstance(existing, list):
            for i, item in enumerate(existing):
                if not isinstance(item, dict):
                    continue
                print("    已有 %s[%d]：%s" % (block, i, _summarise(item, specs)))
                keep = _ask("    保留？/ keep? [Y/n] ").strip().lower()
                if keep in ("", "y", "yes", "是"):
                    items.append(dict(item))
        while True:
            print("    新增一项 / new item:")
            item = {}
            for spec in specs:
                if spec["type"] == "map":
                    continue
                current = None
                tries = 0
                while True:
                    raw = _ask_value(spec, lang, current)
                    if raw == "":
                        if spec.get("required"):
                            tries += 1
                            if tries < 3:
                                print("        （必填，请给一个值 / required — please answer）")
                                continue
                        break
                    value, err = _coerce_input(spec, raw, lang)
                    if err:
                        print("        %s" % err)
                        continue
                    current = value
                    break
                if current is not None:
                    item[_child_of(spec["path"])] = current
            if item:
                items.append(item)
            more = _ask("    再加一项？/ add another? [y/N] ").strip().lower()
            if more not in ("y", "yes", "是"):
                break
        if items:
            out[block] = items
    return out


def _summarise(item, specs):
    keys = [(_child_of(s["path"]) or "") for s in specs]
    for k in keys:
        if k in item and item[k] is not None:
            return "%s: %r …" % (k, item[k])
    return repr(item)


def cmd_wizard(out_path, lang):
    header = []
    newline = "\n"
    existing = {}
    unknown = {}
    if os.path.exists(out_path):
        with open(out_path, "rb") as f:
            blob = f.read()
        text = blob.decode("utf-8")
        if "\r\n" in text:
            newline = "\r\n"
        try:
            existing, unknown = parse_yaml_subset(text)
        except YamlSubsetError as exc:
            sys.stderr.write("ERROR: %s is not readable (%s)\n" % (out_path, exc))
            sys.stderr.write("        refusing to overwrite a file I cannot parse.\n")
            return 1
        print("Reading defaults from %s" % out_path)
        if unknown:
            print("  (unknown block(s) will be preserved verbatim: %s)"
                  % ", ".join(sorted(unknown)))
    print("Garmin-Dashboard runner profile wizard — Enter keeps the current value.\n")
    try:
        data = _interview(existing, lang)
    except (EOFError, KeyboardInterrupt):
        print("\n已中止——%s 未被修改 / aborted, the file was not modified." % out_path)
        return 1

    old_a = _a_race(existing)
    new_a = _a_race(data)
    if old_a and new_a and old_a != new_a:
        try:
            reason = _ask("换 A 赛的原因 / reason for the A-race change: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已中止——%s 未被修改 / aborted, the file was not modified." % out_path)
            return 1
        header.append("A-race change %s: %s" % (datetime.date.today().isoformat(), reason))

    issues = validate(data, unknown)
    _print_issues(issues, out_path)
    if counts(issues)[0]:
        try:
            ans = _ask("有 %d 个错误，仍要写盘吗？/ %d error(s) — write anyway? [y/N] "
                       % (counts(issues)[0], counts(issues)[0])).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n已中止——%s 未被修改 / aborted, the file was not modified." % out_path)
            return 1
        if ans not in ("y", "yes", "是"):
            print("未写盘 / nothing written.")
            return 1

    text = render_yaml_subset(data, unknown=unknown, header=header, newline=newline)
    _atomic_write_text(out_path, text, newline)
    print("\n已写入 %s / written (%d bytes)" % (out_path, len(text.encode("utf-8"))))
    for key in sorted(unknown):
        print("WARN  已保留未知顶层块 '%s'（向导未编辑）/ preserved verbatim" % key)
    return 0


def _a_race(data):
    races = data.get("races")
    if not isinstance(races, list):
        return None
    for r in races:
        if isinstance(r, dict) and isinstance(r.get("role"), str) and r["role"].lower() == "a":
            return (r.get("name"), r.get("date"))
    return None


def cmd_questions(lang):
    sys.stdout.write(questions_text(lang))
    return 0


def _selfcheck():
    fails = []

    def check(name, ok, detail="", skip=False):
        if skip:
            print("SKIP  %s" % name)
            return
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name,
                            (" - %s" % detail) if detail and not ok else ""))
        if not ok:
            fails.append(name)

    # A. FIELDS self-consistency
    paths = [f["path"] for f in FIELDS]
    dupes = sorted(set(p for p in paths if paths.count(p) > 1))
    check("fields: paths unique", not dupes, "duplicates: %s" % dupes)
    check("fields: TOP_LEVEL_ORDER pinned", TOP_LEVEL_ORDER == TOP_LEVEL_ORDER_EXPECTED,
          "%s != %s" % (TOP_LEVEL_ORDER, TOP_LEVEL_ORDER_EXPECTED))
    missing_block = [b for b in TOP_LEVEL_ORDER if b not in BLOCKS]
    check("fields: every top-level block declared", not missing_block, str(missing_block))
    bad_enum = [f["path"] for f in FIELDS if f["type"] == "enum" and not f.get("enum")]
    check("fields: enum fields carry values", not bad_enum, str(bad_enum))
    missing_meta = []
    for f in FIELDS:
        for key in ("label", "question", "help"):
            if key not in f or set(f[key]) != {"zh", "en"}:
                missing_meta.append("%s.%s" % (f["path"], key))
        if "example" not in f or "placeholder" not in f:
            missing_meta.append("%s.example" % f["path"])
    check("fields: bilingual label/question/help + example + placeholder",
          not missing_meta, str(missing_meta[:5]))
    declared = set()
    for b in BLOCKS:
        declared.add(b)
    orphan = [f["path"] for f in FIELDS if _block_of(f["path"]) not in declared]
    check("fields: every path belongs to a declared block", not orphan, str(orphan))

    coach_dirs = []
    if os.path.isdir(SKILLS_DIR):
        for name in sorted(os.listdir(SKILLS_DIR)):
            if name.startswith("coach-") and os.path.isdir(os.path.join(SKILLS_DIR, name)):
                coach_dirs.append(name[len("coach-"):].replace("-", "_"))
    coach_enum = list(_find_spec("coach")["enum"])
    check("fields: coach enum == .agents/skills/coach-*",
          sorted(coach_dirs) == sorted(coach_enum),
          "dirs=%s enum=%s" % (coach_dirs, coach_enum))

    # B. derived artifacts
    for lang in ("zh", "en"):
        text = questions_text(lang)
        missing = [f["path"] for f in FIELDS if f["path"] not in text]
        check("questions(%s): every field appears" % lang, not missing, str(missing[:5]))
    generated = questionnaire_text()
    if os.path.exists(QUESTIONNAIRE_FILE):
        with open(QUESTIONNAIRE_FILE, "r", encoding="utf-8") as f:
            committed = f.read()
        check("questionnaire: committed file == generated",
              committed == generated,
              "run: python scripts/profile_wizard.py --emit-questionnaire")
    else:
        check("questionnaire: committed file exists", False,
              "missing %s" % QUESTIONNAIRE_FILE)

    # C. repo artifacts
    if os.path.exists(EXAMPLE_PROFILE):
        try:
            ex_data, ex_unknown = parse_file(EXAMPLE_PROFILE)
            errs = counts(validate(ex_data, ex_unknown))[0]
            check("example profile: parses and validates with 0 errors", errs == 0,
                  "%d error(s)" % errs)
        except YamlSubsetError as exc:
            check("example profile: parses", False, str(exc))
    else:
        check("example profile: present", False, EXAMPLE_PROFILE)

    try:
        q_data, q_unknown = parse_yaml_subset(generated)
        q_errs = counts(validate(q_data, q_unknown))[0]
        check("questionnaire: is a blank template (fails validation on placeholders)",
              q_errs > 0, "it validated clean — it is not a blank template")
    except YamlSubsetError as exc:
        check("questionnaire: is a blank template", False, "does not parse: %s" % exc)

    if os.path.exists(DEFAULT_PROFILE):
        try:
            p_data, p_unknown = parse_file(DEFAULT_PROFILE)
            p_errs = counts(validate(p_data, p_unknown))[0]
            check("private workspace profile: parses and validates with 0 errors", p_errs == 0,
                  "%d error(s)" % p_errs)
        except YamlSubsetError as exc:
            check("private workspace profile: parses", False, str(exc))
    else:
        check("private workspace profile", True, skip=True)

    # D. embedded rejection/acceptance spec
    reject_cases = [
        ("reject tab indent", "a:\n\tb: 1\n", "tab character"),
        ("reject flow map", "a: {b: 1}\n", "flow mappings"),
        ("reject block scalar", "a: |\n  text\n", "block scalars"),
        ("reject anchor", "a: &x 1\n", "anchors"),
        ("reject alias", "a: *x\n", "aliases"),
        ("reject merge key", "<<: x\n", "merge keys"),
        ("reject duplicate key", "a: 1\na: 2\n", "duplicate key"),
    ]
    for name, sample, needle in reject_cases:
        try:
            parse_yaml_subset(sample, known_top=None)
            check(name, False, "it parsed instead of raising")
        except YamlSubsetError as exc:
            check(name, needle in exc.msg, "message was %r" % exc.msg)

    accept_cases = [
        ("accept crlf", "a:\r\n  b: 1\r\n", {"a": {"b": 1}}),
        ("accept bom", "\ufeffa: 1\n", {"a": 1}),
        ("accept quoted hash", 'a: "x # y"\n', {"a": "x # y"}),
        ("accept inline seq", "a: [x, y]\n", {"a": ["x", "y"]}),
        ("accept empty seq", "a: []\n", {"a": []}),
        ("accept multi-line quoted", 'a: "x\n  y"\n', {"a": "x y"}),
        ("accept multi-line plain", "a: x\n  y\n", {"a": "x y"}),
    ]
    for name, sample, want in accept_cases:
        try:
            got, _ = parse_yaml_subset(sample, known_top=None)
            check(name, got == want, "got %r" % (got,))
        except YamlSubsetError as exc:
            check(name, False, str(exc))

    sample = "coach: daniels_vdot\nmeasured:\n  rhr_21d: {min: 42, median: 46}\n"
    try:
        got, unknown = parse_yaml_subset(sample)
        check("accept unknown block containing a flow map",
              got == {"coach": "daniels_vdot"} and "measured" in unknown,
              "got %r / %r" % (got, unknown))
    except YamlSubsetError as exc:
        check("accept unknown block containing a flow map", False, str(exc))

    # E. round trip
    if os.path.exists(EXAMPLE_PROFILE):
        try:
            before, _ = parse_file(EXAMPLE_PROFILE)
            after, _ = parse_yaml_subset(render_yaml_subset(before))
            check("round-trip: example profile survives render(parse(x))", before == after)
        except Exception as exc:  # noqa: BLE001 - report any failure, never crash selfcheck
            check("round-trip: example profile survives render(parse(x))", False, repr(exc))

    if fails:
        print("\nselfcheck FAILED: %d group(s)" % len(fails))
        return 1
    print("\nselfcheck PASSED")
    return 0


def cli(argv=None):
    ap = argparse.ArgumentParser(
        description="runner-profile wizard / validator for the restricted YAML subset "
                    "(stdlib only, no PyYAML).",
        epilog="Examples:\n"
               "  python scripts/profile_wizard.py\n"
               "  python scripts/profile_wizard.py --check workspace/runner_profile.yaml\n"
               "  python scripts/profile_wizard.py --questions --lang en\n"
               "  python scripts/profile_wizard.py --emit-questionnaire\n"
               "  python scripts/profile_wizard.py --selfcheck\n")
    ap.add_argument("--check", metavar="YAML", default=None,
                    help="validate a profile file; non-zero exit on errors")
    ap.add_argument("--questions", action="store_true",
                    help="print the canonical question list (from FIELDS)")
    ap.add_argument("--selfcheck", action="store_true",
                    help="validate FIELDS + the generated artifacts; non-zero on failure")
    ap.add_argument("--emit-questionnaire", action="store_true",
                    help="regenerate examples/runner_profile.questionnaire.yaml")
    ap.add_argument("--out", default=None,
                    help="target file (default: workspace/runner_profile.yaml)")
    ap.add_argument("--lang", default="zh", choices=["zh", "en"],
                    help="language for the wizard UI and --questions (default: zh)")
    a = ap.parse_args(argv)

    if a.selfcheck:
        return _selfcheck()
    if a.emit_questionnaire:
        return cmd_emit_questionnaire(a.out or QUESTIONNAIRE_FILE)
    if a.check is not None:
        return cmd_check(a.check)
    if a.questions:
        return cmd_questions(a.lang)
    return cmd_wizard(a.out or DEFAULT_PROFILE, a.lang)


if __name__ == "__main__":
    sys.exit(cli())

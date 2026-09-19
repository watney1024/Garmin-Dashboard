# -*- coding: utf-8 -*-
"""Tests for scripts/profile_wizard.py — the restricted YAML subset, the validator and the
data-safety guarantees of the wizard.

Run:  python -m unittest discover -s tests -v

Why these exist: the profile is the one file the runner owns, and it is read back and rewritten
by a hand-written parser (this repo is stdlib-only, so there is no PyYAML to lean on). Two
things therefore have to be pinned:

  * the parser must REJECT the constructs it claims not to support instead of silently
    mis-reading them, and must still ACCEPT the shapes the real profiles actually use
    (CRLF, a leading BOM, scalars spanning several physical lines, inline flow sequences);
  * a failed or interrupted write must never destroy the existing file — same rule the
    garmin_pull tests pin for the master CSV — and a hand-maintained extension block such as
    the runner's private `measured:` must survive a wizard run verbatim.
"""
import builtins
import io
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import profile_wizard as pw  # noqa: E402


def parse(text):
    """Strict, schema-agnostic parse (no unknown-top-level tolerance)."""
    return pw.parse_yaml_subset(text, known_top=None)[0]


def issues_of(data, unknown=None):
    return pw.validate(data, unknown or {})


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def errors_of(issues):
    return [i for i in issues if i.severity == "error"]


def valid_profile():
    return {
        "identity": {"alias": "示例跑者", "language": "zh", "timezone": "Asia/Shanghai",
                     "birth_year": 1985, "sex": "M"},
        "races": [{"name": "示例国际马拉松", "date": "2027-11-21", "distance": "marathon",
                   "role": "A"}],
        "weekly": {"runs_per_week": 3,
                   "days": {"Tuesday": "quality", "Thursday": "easy", "Sunday": "long"},
                   "long_run_day": "Sunday", "quality_days": ["Tuesday"],
                   "max_run_min": 180},
        "pr": {"10k": "49:30", "half": "1:52:30"},
        "coach": "daniels_vdot",
        "strength": {"sessions_per_week": 2, "days": {"Wednesday": "lower body"}},
        "constraints": ["曾患足底筋膜炎（已愈）"],
        "metric_baselines": {"resting_hr": 50, "weight_kg": 62.0, "sleep_h": 7.2},
        "devices": [{"kind": "hr_strap", "since": "2027-01-05", "note": "HRM-Dual"}],
    }


EXAMPLE = os.path.join(pw.EXAMPLES_DIR, "runner_profile.example.yaml")
QUESTIONNAIRE = pw.QUESTIONNAIRE_FILE


# ---------------------------------------------------------------------------
# parser: accepted shapes
# ---------------------------------------------------------------------------

class ParserAcceptTests(unittest.TestCase):
    def test_block_mapping_and_nesting(self):
        self.assertEqual(parse("a:\n  b: 1\n  c: two\n"), {"a": {"b": 1, "c": "two"}})

    def test_sequence_of_scalars(self):
        self.assertEqual(parse("a:\n  - x\n  - 'y z'\n"), {"a": ["x", "y z"]})

    def test_sequence_of_maps(self):
        got = parse("races:\n  - name: one\n    date: 2027-01-01\n  - name: two\n    role: A\n")
        self.assertEqual(got["races"], [{"name": "one", "date": "2027-01-01"},
                                        {"name": "two", "role": "A"}])

    def test_inline_flow_sequence(self):
        self.assertEqual(parse("a: [x, y]\n"), {"a": ["x", "y"]})

    def test_empty_inline_flow_sequence(self):
        self.assertEqual(parse("a: []\n"), {"a": []})

    def test_inline_comment_after_value(self):
        self.assertEqual(parse("a: 1   # note\n"), {"a": 1})

    def test_full_line_comment_and_blank_lines(self):
        self.assertEqual(parse("# lead\n\na: 1\n\n# trail\n"), {"a": 1})

    def test_hash_inside_quotes_is_kept(self):
        self.assertEqual(parse('a: "x # y"\n'), {"a": "x # y"})
        self.assertEqual(parse("a: 'x # y'\n"), {"a": "x # y"})

    def test_crlf_parses_like_lf(self):
        self.assertEqual(parse("a:\r\n  b: 1\r\n"), parse("a:\n  b: 1\n"))

    def test_leading_bom_is_ignored(self):
        self.assertEqual(parse("\ufeffa: 1\n"), {"a": 1})

    def test_leading_document_marker_is_ignored(self):
        self.assertEqual(parse("---\na: 1\n"), {"a": 1})

    def test_plain_scalar_continues_on_the_next_line(self):
        self.assertEqual(parse("a: one\n  two\n"), {"a": "one two"})

    def test_quoted_scalar_spans_physical_lines(self):
        self.assertEqual(parse('a: "one\n  two"\n'), {"a": "one two"})

    def test_colons_inside_values_do_not_split_the_key(self):
        got = parse("pr:\n  5k: 23:45\n  marathon: 3:54:04\n")
        self.assertEqual(got, {"pr": {"5k": "23:45", "marathon": "3:54:04"}})

    def test_scalar_types(self):
        got = parse("a: 4\nb: 56.8\nc: true\nd: ~\ne: Asia/Shanghai\n")
        self.assertEqual(got, {"a": 4, "b": 56.8, "c": True, "d": None, "e": "Asia/Shanghai"})

    def test_key_without_a_value_is_none(self):
        self.assertEqual(parse("a:\n"), {"a": None})


# ---------------------------------------------------------------------------
# parser: rejected shapes
# ---------------------------------------------------------------------------

class ParserRejectTests(unittest.TestCase):
    def assertRejects(self, text, needle):
        with self.assertRaises(pw.YamlSubsetError) as ctx:
            parse(text)
        self.assertIn(needle, ctx.exception.msg)
        self.assertIn("line ", str(ctx.exception))

    def test_rejects_tab_indentation(self):
        self.assertRejects("a:\n\tb: 1\n", "tab character")

    def test_rejects_flow_mapping(self):
        self.assertRejects("days: { Wednesday: lower }\n", "flow mappings")

    def test_rejects_flow_mapping_inside_a_sequence(self):
        self.assertRejects("a: [{b: 1}]\n", "flow mappings")

    def test_rejects_block_scalar(self):
        self.assertRejects("a: |\n  text\n", "block scalars")
        self.assertRejects("a: >-\n  text\n", "block scalars")

    def test_rejects_anchor(self):
        self.assertRejects("a: &x 1\n", "anchors")

    def test_rejects_alias(self):
        self.assertRejects("a: *x\n", "aliases")

    def test_rejects_merge_key(self):
        self.assertRejects("<<: *x\n", "merge keys")

    def test_rejects_tag(self):
        self.assertRejects("a: !!str 1\n", "tags")

    def test_rejects_duplicate_key(self):
        self.assertRejects("a: 1\na: 2\n", "duplicate key")

    def test_rejects_nested_flow_sequence(self):
        self.assertRejects("a: [[1]]\n", "nested flow sequences")

    def test_rejects_unterminated_flow_sequence(self):
        self.assertRejects("a: [1, 2\n", "unterminated flow sequence")

    def test_rejects_trailing_comma_in_flow_sequence(self):
        self.assertRejects("a: [1, ]\n", "trailing comma")

    def test_rejects_unterminated_quote(self):
        self.assertRejects('a: "oops\n', "unterminated quoted string")

    def test_rejects_inconsistent_indentation(self):
        self.assertRejects("a:\n  b: 1\n   c: 2\n", "inconsistent indentation")

    def test_rejects_bad_dedent(self):
        self.assertRejects("a:\n    b: 1\n  c: 2\n", "inconsistent indentation")

    def test_rejects_junk_line(self):
        self.assertRejects("just some words\n", "'key: value'")


# ---------------------------------------------------------------------------
# parser: unknown top-level blocks (the private `measured:` case)
# ---------------------------------------------------------------------------

class UnknownBlockTests(unittest.TestCase):
    SAMPLE = ("coach: daniels_vdot\n"
              "measured:\n"
              "  hr_max_observed: 191\n"
              "  rhr_21d: {min: 42, median: 46, max: 48}\n")

    def test_unknown_block_is_captured_and_its_interior_never_parsed(self):
        data, unknown = pw.parse_yaml_subset(self.SAMPLE)
        self.assertEqual(data, {"coach": "daniels_vdot"})
        self.assertIn("measured", unknown)
        self.assertIn("rhr_21d: {min: 42, median: 46, max: 48}", "\n".join(unknown["measured"]))

    def test_unknown_block_is_exactly_one_warning_and_no_error(self):
        _, unknown = pw.parse_yaml_subset(self.SAMPLE)
        data = valid_profile()
        issues = issues_of(data, unknown)
        self.assertEqual(errors_of(issues), [])
        named = [i for i in issues if i.path == "measured"]
        self.assertEqual(len(named), 1)
        self.assertEqual(named[0].severity, "warn")

    def test_unknown_key_inside_a_known_block_is_an_error(self):
        data = valid_profile()
        data["weekly"]["foo"] = 1
        errs = errors_of(issues_of(data))
        self.assertTrue(any("weekly.foo" in i.path for i in errs))

    def test_two_unknown_blocks_are_both_captured(self):
        _, unknown = pw.parse_yaml_subset("coach: daniels_vdot\nfoo:\n  a: 1\nbar: 2\n")
        self.assertEqual(sorted(unknown), ["bar", "foo"])

    def test_strict_mode_has_no_unknown_tolerance(self):
        with self.assertRaises(pw.YamlSubsetError):
            pw.parse_yaml_subset("measured:\n  rhr: {min: 1}\n", known_top=None)


# ---------------------------------------------------------------------------
# validator
# ---------------------------------------------------------------------------

class ValidatorTests(unittest.TestCase):
    def test_valid_profile_has_no_errors(self):
        self.assertEqual(errors_of(issues_of(valid_profile())), [])

    def test_the_shipped_example_is_clean(self):
        data, unknown = pw.parse_file(EXAMPLE)
        self.assertEqual(errors_of(issues_of(data, unknown)), [])

    def test_missing_required_block(self):
        data = valid_profile()
        del data["metric_baselines"]
        errs = errors_of(issues_of(data))
        self.assertTrue(any(i.path == "metric_baselines" for i in errs))

    def test_missing_required_field(self):
        data = valid_profile()
        del data["identity"]["alias"]
        errs = errors_of(issues_of(data))
        self.assertTrue(any(i.path == "identity.alias" for i in errs))

    def test_bad_enum(self):
        data = valid_profile()
        data["identity"]["language"] = "fr"
        errs = errors_of(issues_of(data))
        self.assertTrue(any("zh|en" in i.message for i in errs))

    def test_bad_date(self):
        data = valid_profile()
        data["races"][0]["date"] = "2027/11/21"
        errs = errors_of(issues_of(data))
        self.assertTrue(any(i.path == "races[0].date" for i in errs))

    def test_bad_times(self):
        data = valid_profile()
        data["pr"]["5k"] = "24:5"
        data["pr"]["half"] = "1:52"
        errs = errors_of(issues_of(data))
        self.assertTrue(any(i.path == "pr.5k" for i in errs))
        self.assertTrue(any(i.path == "pr.half" for i in errs))

    def test_two_a_races_is_an_error_naming_both(self):
        data = valid_profile()
        data["races"].append({"name": "第二场", "date": "2027-12-05",
                              "distance": "marathon", "role": "A"})
        errs = errors_of(issues_of(data))
        hit = [i for i in errs if i.path == "races"]
        self.assertTrue(hit)
        self.assertIn("第二场", hit[0].message)

    def test_no_a_race_is_only_a_warning(self):
        data = valid_profile()
        data["races"][0]["role"] = "training"
        issues = issues_of(data)
        self.assertEqual(errors_of(issues), [])
        self.assertTrue(any("no role: A" in i.message for i in issues))

    def test_zero_prs_is_an_error(self):
        data = valid_profile()
        data["pr"] = {}
        self.assertTrue(any(i.path == "pr" for i in errors_of(issues_of(data))))

    def test_unresolvable_coach_is_an_error_naming_the_path(self):
        data = valid_profile()
        data["coach"] = "nope"
        errs = errors_of(issues_of(data))
        self.assertTrue(any(".agents/skills/coach-nope/" in i.message for i in errs))

    def test_every_shipped_coach_resolves(self):
        for coach in pw._find_spec("coach")["enum"]:
            data = valid_profile()
            data["coach"] = coach
            self.assertEqual(errors_of(issues_of(data)), [], coach)

    def test_empty_constraints_list_is_valid(self):
        data = valid_profile()
        data["constraints"] = []
        self.assertEqual(errors_of(issues_of(data)), [])

    def test_unknown_field_inside_a_race_item(self):
        data = valid_profile()
        data["races"][0]["bogus"] = 1
        errs = errors_of(issues_of(data))
        self.assertTrue(any(i.path == "races[0].bogus" for i in errs))

    def test_devices_item_missing_since_reports_the_index(self):
        data = valid_profile()
        data["devices"][0].pop("since")
        errs = errors_of(issues_of(data))
        self.assertTrue(any(i.path == "devices[0].since" for i in errs))

    def test_placeholder_values_are_errors(self):
        data = valid_profile()
        data["identity"]["alias"] = "<alias / 称呼>"
        errs = errors_of(issues_of(data))
        self.assertTrue(any("template placeholder" in i.message for i in errs))

    def test_unfilled_marker_is_only_a_warning(self):
        data = valid_profile()
        data["identity"]["alias"] = "待补"
        issues = issues_of(data)
        self.assertEqual(errors_of(issues), [])
        self.assertTrue(any(i.severity == "warn" and i.path == "identity.alias"
                            for i in issues))

    def test_weekly_inconsistencies_are_warnings(self):
        data = valid_profile()
        data["weekly"]["runs_per_week"] = 6
        data["weekly"]["long_run_day"] = "Monday"
        data["weekly"]["quality_days"] = ["Thursday"]
        issues = issues_of(data)
        self.assertEqual(errors_of(issues), [])
        paths = {i.path for i in issues}
        self.assertIn("weekly.long_run_day", paths)
        self.assertIn("weekly.quality_days", paths)

    def test_birth_year_without_sex_is_a_warning(self):
        data = valid_profile()
        del data["identity"]["sex"]
        issues = issues_of(data)
        self.assertEqual(errors_of(issues), [])
        self.assertTrue(any(i.path == "identity.birth_year" for i in issues))

    def test_implausible_resting_hr_is_a_warning(self):
        data = valid_profile()
        data["metric_baselines"]["resting_hr"] = 400
        issues = issues_of(data)
        self.assertEqual(errors_of(issues), [])
        self.assertTrue(any(i.path == "metric_baselines.resting_hr" for i in issues))

    def test_strength_block_without_children_is_an_error(self):
        data = valid_profile()
        data["strength"] = {}
        errs = errors_of(issues_of(data))
        self.assertTrue(any(i.path == "strength.sessions_per_week" for i in errs))


# ---------------------------------------------------------------------------
# atomic writes
# ---------------------------------------------------------------------------

class AtomicWriteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.target = os.path.join(self.tmp, "runner_profile.yaml")

    def test_writes_lf_without_bom(self):
        pw._atomic_write_text(self.target, "a: 1\n")
        with open(self.target, "rb") as f:
            raw = f.read()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r\n", raw)
        self.assertTrue(raw.endswith(b"\n"))

    def test_keeps_crlf_when_asked(self):
        pw._atomic_write_text(self.target, "a: 1\n", "\r\n")
        with open(self.target, "rb") as f:
            self.assertIn(b"a: 1\r\n", f.read())

    def test_write_failure_leaves_the_original_intact_and_no_temp_files(self):
        with open(self.target, "wb") as f:
            f.write(b"original: yes\n")
        real_replace = pw.os.replace

        def boom(*a, **k):
            raise OSError("disk full")

        pw.os.replace = boom
        try:
            with self.assertRaises(OSError):
                pw._atomic_write_text(self.target, "replaced: yes\n")
        finally:
            pw.os.replace = real_replace
        with open(self.target, "rb") as f:
            self.assertEqual(f.read(), b"original: yes\n")
        leftovers = [n for n in os.listdir(self.tmp) if n.endswith(".tmp")]
        self.assertEqual(leftovers, [])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def path(self, name):
        return os.path.join(self.tmp, name)

    def write(self, name, text):
        p = self.path(name)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return p

    def run_cli(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = pw.cli(argv)
        return code, buf.getvalue()

    def test_check_accepts_a_good_profile(self):
        p = self.write("good.yaml", pw.render_yaml_subset(valid_profile()))
        code, out = self.run_cli(["--check", p])
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_check_rejects_a_bad_profile(self):
        data = valid_profile()
        data["identity"]["language"] = "fr"
        p = self.write("bad.yaml", pw.render_yaml_subset(data))
        code, out = self.run_cli(["--check", p])
        self.assertEqual(code, 1)
        self.assertIn("ERROR", out)

    def test_check_reports_a_parse_error_with_a_line_number(self):
        p = self.write("broken.yaml",
                       "identity:\n"
                       "  alias: x\n"
                       "weekly:\n"
                       "  days: {a: b}\n")
        code, out = self.run_cli(["--check", p])
        self.assertEqual(code, 1)
        self.assertIn(":4:", out)
        self.assertIn("flow mappings", out)

    def test_check_on_a_missing_file_is_a_config_error(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code, _ = self.run_cli(["--check", self.path("nope.yaml")])
        self.assertEqual(code, 2)
        self.assertIn("no such file", err.getvalue())

    def test_questions_cover_every_field(self):
        for lang in ("zh", "en"):
            code, out = self.run_cli(["--questions", "--lang", lang])
            self.assertEqual(code, 0)
            for spec in pw.FIELDS:
                self.assertIn(spec["path"], out)

    def test_selfcheck_passes(self):
        code, out = self.run_cli(["--selfcheck"])
        self.assertEqual(code, 0, out)

    def test_emit_questionnaire_matches_the_committed_file(self):
        out_path = self.path("q.yaml")
        code, _ = self.run_cli(["--emit-questionnaire", "--out", out_path])
        self.assertEqual(code, 0)
        with open(out_path, "r", encoding="utf-8") as f:
            written = f.read()
        with open(QUESTIONNAIRE, "r", encoding="utf-8") as f:
            committed = f.read()
        self.assertEqual(written, committed)


# ---------------------------------------------------------------------------
# derived artifacts stay in sync with FIELDS
# ---------------------------------------------------------------------------

class SyncTests(unittest.TestCase):
    def test_committed_questionnaire_equals_the_generator(self):
        with open(QUESTIONNAIRE, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), pw.questionnaire_text())

    def test_questionnaire_parses_and_lists_every_block(self):
        with open(QUESTIONNAIRE, "r", encoding="utf-8") as f:
            data, _ = pw.parse_yaml_subset(f.read())
        for block in pw.TOP_LEVEL_ORDER:
            self.assertIn(block, data)

    def test_questionnaire_is_a_blank_template(self):
        with open(QUESTIONNAIRE, "r", encoding="utf-8") as f:
            data, unknown = pw.parse_yaml_subset(f.read())
        self.assertTrue(errors_of(issues_of(data, unknown)),
                        "the questionnaire validated clean — it is not a blank template")

    def test_top_level_order_is_pinned(self):
        self.assertEqual(pw.TOP_LEVEL_ORDER, pw.TOP_LEVEL_ORDER_EXPECTED)

    def test_coach_enum_matches_the_shipped_skills(self):
        found = sorted(n[len("coach-"):].replace("-", "_")
                       for n in os.listdir(pw.SKILLS_DIR)
                       if n.startswith("coach-")
                       and os.path.isdir(os.path.join(pw.SKILLS_DIR, n)))
        self.assertEqual(sorted(pw._find_spec("coach")["enum"]), found)


# ---------------------------------------------------------------------------
# the wizard must not eat what it does not understand
# ---------------------------------------------------------------------------

PRIVATE_LIKE = """\
# a private profile with a hand-maintained extension block
identity:
  alias: 示例跑者
  language: zh
  timezone: Asia/Shanghai
races:
  - name: 上海马拉松
    date: 2026-12-06
    distance: marathon
    role: A
weekly:
  runs_per_week: 2
  days:
    Tuesday: easy
    Sunday: long
  long_run_day: Sunday
  quality_days: []
pr:
  marathon: 3:54:04
coach: daniels_vdot
constraints:
  - "左腿紧张，自评 4/10（单侧）"
metric_baselines:
  resting_hr: 46
  weight_kg: 56.8
  sleep_h: 6.9
devices:
  - kind: hr_strap
    since: 2026-09-06
    note: "心率带"
measured:
  hr_max_observed: 191
  rhr_21d: {min: 42, median: 46, max: 48}
  height_cm: 172
"""


class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.target = os.path.join(self.tmp, "runner_profile.yaml")
        with open(self.target, "w", encoding="utf-8", newline="") as f:
            f.write(PRIVATE_LIKE)
        self.real_input = builtins.input
        builtins.input = lambda prompt="": ""      # keep every current value
        self.addCleanup(self._restore)

    def _restore(self):
        builtins.input = self.real_input

    def test_wizard_preserves_the_unknown_block_verbatim(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = pw.cli(["--out", self.target])
        self.assertEqual(code, 0, buf.getvalue())
        with open(self.target, "r", encoding="utf-8") as f:
            written = f.read()
        self.assertIn("measured:", written)
        self.assertIn("rhr_21d: {min: 42, median: 46, max: 48}", written)
        self.assertIn("height_cm: 172", written)

    def test_wizard_keeps_existing_races_and_devices(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            pw.cli(["--out", self.target])
        with open(self.target, "r", encoding="utf-8") as f:
            data, _ = pw.parse_yaml_subset(f.read())
        self.assertEqual(len(data["races"]), 1)
        self.assertEqual(data["races"][0]["name"], "上海马拉松")
        self.assertEqual(len(data["devices"]), 1)
        self.assertEqual(data["devices"][0]["since"], "2026-09-06")

    def test_wizard_keeps_the_original_line_endings(self):
        with open(self.target, "rb") as f:
            blob = f.read()
        with open(self.target, "wb") as f:
            f.write(blob.replace(b"\n", b"\r\n"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            pw.cli(["--out", self.target])
        with open(self.target, "rb") as f:
            raw = f.read()
        self.assertIn(b"\r\n", raw)
        self.assertEqual(raw.count(b"\n"), raw.count(b"\r\n"),
                         "output must not mix LF and CRLF")

    def test_interrupt_leaves_the_file_untouched(self):
        before = read_bytes(self.target)
        builtins.input = _raise_eof
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = pw.cli(["--out", self.target])
        self.assertEqual(code, 1)
        self.assertEqual(read_bytes(self.target), before)

    def test_unparsable_target_is_refused_not_overwritten(self):
        with open(self.target, "w", encoding="utf-8", newline="") as f:
            f.write("identity:\n\tdays: {a: b}\n")
        before = read_bytes(self.target)
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            code = pw.cli(["--out", self.target])
        self.assertEqual(code, 1)
        self.assertEqual(read_bytes(self.target), before)


def _raise_eof(prompt=""):
    raise EOFError()


if __name__ == "__main__":
    unittest.main()

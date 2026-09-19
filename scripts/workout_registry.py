# -*- coding: utf-8 -*-
"""workout_registry.py — idempotency for pushing plan sessions to Garmin.

Shared by `garmin_schedule.py` (continuous runs) and `garmin_track_workout.py`
(track/interval sessions). Stdlib only.

Why this exists: both scripts used to cache `name -> workout id` and re-schedule the
cached id forever. Any change to a session whose *name* stayed the same — a widened HR
band, different minutes, a removed warm-up target — never reached the watch, and the
script still reported success. A name is not an identity for content.

So the registry now stores a **fingerprint of the exact tool arguments** that created the
workout. On every run each session is classified:

    create   not in the registry
    reuse    the cached workout is still on Garmin AND its content matches what we'd build
    replace  the cached workout is gone, or its content differs -> build new, then delete old

The remote check is what makes migration safe: an entry written by an older version (no
fingerprint) is not blindly rebuilt, and a workout someone edited by hand in Garmin
Connect is not blindly trusted.

Docs: docs/02 §4 (registry schema) and §3b (track spec).
"""
import hashlib
import json
import os
import time

SCHEMA_VERSION = 2

KIND_RUN = "run"
KIND_TRACK = "track"


class RemoteLookupError(RuntimeError):
    """Could not ASK Garmin what a cached workout looks like.

    Must not be confused with "the workout is not there": treating a failed lookup as
    "missing" would silently rebuild every workout on the watch.
    """


# ---------------------------------------------------------------------------
# fingerprint
# ---------------------------------------------------------------------------
def fingerprint(kind, args):
    """Stable id for "this exact workout definition".

    `args` must be the arguments actually handed to the tool — resolved values, not the
    raw spec (e.g. `minutes` already derived from km x pace).
    """
    payload = json.dumps({"kind": kind, "args": args},
                         ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# registry file
# ---------------------------------------------------------------------------
def load_reg(path):
    """-> {name: {"id": int, "kind": str|None, "fp": str|None}}.

    Accepts v1 (a flat `name -> id` map) and normalises it. A missing or unreadable file
    yields {} — which safely means "rebuild everything", since the registry is only a cache.
    """
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}

    if isinstance(raw.get("workouts"), dict):
        out = {}
        for name, v in raw["workouts"].items():
            if isinstance(v, dict) and v.get("id") is not None:
                out[name] = {"id": v["id"], "kind": v.get("kind"), "fp": v.get("fp")}
        return out

    # v1: flat name -> int
    return {name: {"id": v, "kind": None, "fp": None}
            for name, v in raw.items() if isinstance(v, int) and not isinstance(v, bool)}


def save_reg(path, reg):
    doc = {"schema_version": SCHEMA_VERSION,
           "workouts": {name: {"id": v["id"], "kind": v.get("kind"), "fp": v.get("fp")}
                        for name, v in sorted(reg.items())}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")


# ---------------------------------------------------------------------------
# remote comparison
# ---------------------------------------------------------------------------
def workout_exists(res):
    """A missing workout comes back as {"error": false, "raw": "... 404 ..."} — the `error`
    flag is False even then, so presence of an `id` is the only trustworthy signal."""
    return isinstance(res, dict) and res.get("id") is not None


def _num(v):
    if v is None:
        return None
    try:
        return round(float(v), 3)
    except (TypeError, ValueError):
        return v


def _canon(steps):
    """One canonical tuple per step: (type, end_condition, end_condition_value, hr_low, hr_high).

    Repeat groups contribute their own tuple and then their children's, so a built DTO and
    a remote response flatten to comparable lists. Descriptions are deliberately ignored:
    Garmin regenerates them server-side, so comparing them would rebuild forever.
    """
    out = []
    for st in steps or []:
        if not isinstance(st, dict):
            continue
        low = high = None
        # Our DTO nests `stepType`/`endCondition` as dicts; a remote response is flat.
        # Keying off `workoutSteps` is wrong — plain ExecutableStepDTOs have no children.
        if isinstance(st.get("stepType"), dict):                           # our DTO
            typ = st["stepType"].get("stepTypeKey")
            cond = (st.get("endCondition") or {}).get("conditionTypeKey")
            val = _num(st.get("endConditionValue"))
            if (st.get("targetType") or {}).get("workoutTargetTypeKey") == "heart.rate.zone":
                low, high = _num(st.get("targetValueOne")), _num(st.get("targetValueTwo"))
            kids = st.get("workoutSteps")
        else:                                                              # remote response
            typ = st.get("type")
            cond = st.get("end_condition")
            val = _num(st.get("end_condition_value"))
            if st.get("target_type") == "heart.rate.zone":
                low, high = _num(st.get("target_value_low")), _num(st.get("target_value_high"))
            kids = st.get("steps")
        out.append((typ, cond, val, low, high))
        if kids:
            out.extend(_canon(kids))
    return out


def _remote_steps(remote):
    steps = []
    for seg in (remote.get("segments") or []):
        steps.extend((seg or {}).get("steps") or [])
    return steps


def _matches_run(expect, remote):
    want_dur = _num(expect.get("duration"))
    got_dur = _num(remote.get("estimated_duration_seconds"))
    if got_dur != want_dur:
        return False, "duration %s != expected %s" % (got_dur, want_dur)

    flat = _canon(_remote_steps(remote))
    odd = [f for f in flat if f[0] in ("warmup", "cooldown") and f[2] not in (None, 0.0)]
    if odd:
        return False, "unexpected warmup/cooldown duration in %s" % (odd,)

    want_hr = tuple(_num(x) for x in (expect.get("hr") or (None, None)))
    if want_hr != (None, None):
        got_hr = [(lo, hi) for (_t, _c, _v, lo, hi) in flat if lo is not None or hi is not None]
        if got_hr != [want_hr]:
            return False, "HR target(s) %s != expected %s" % (got_hr, [want_hr])
    return True, "duration + HR target match"


def _matches_track(expect, remote):
    dto = expect.get("dto") or {}
    segs = dto.get("workoutSegments") or []
    want = _canon((segs[0].get("workoutSteps") if segs else None) or [])
    got = _canon(_remote_steps(remote))
    if want != got:
        what = []
        for i in range(max(len(want), len(got))):
            a = want[i] if i < len(want) else None
            b = got[i] if i < len(got) else None
            if a != b:
                what.append("step %d: on-watch %s vs would-be %s" % (i + 1, b, a))
        return False, "step structure differs — " + "; ".join(what[:3])
    return True, "step structure matches (%d steps)" % len(want)


def remote_matches(kind, expect, remote):
    """-> (bool, reason). Compares meaning, never server-generated descriptions."""
    if not workout_exists(remote):
        return False, "not on Garmin any more"
    if kind == KIND_TRACK:
        return _matches_track(expect, remote)
    if kind == KIND_RUN:
        return _matches_run(expect, remote)
    return False, "unknown kind %r" % (kind,)


# ---------------------------------------------------------------------------
# decision
# ---------------------------------------------------------------------------
def write_landed(res):
    """Did a write actually take effect?

    Garmin reports some failures as {"error": false, "raw": "..."} — `raw` present with no
    real payload means it did not work, whatever the error flag says.
    """
    return (isinstance(res, dict) and len(res) > 0
            and res.get("error") is not True and res.get("raw") is None)


def verify_schedule(call, expected, attempts=4, delay=1.5):
    """Read the calendar back: proof the change landed, not merely that we asked.

    expected: {date: workout_id}. Past dates cannot be verified — the calendar only lists
    upcoming entries — so they are skipped and counted rather than reported as failures.

    Garmin's calendar is **eventually consistent**: right after a create+delete pair it can
    still show the old workout id. Measured on 2026-09-19 that settled within seconds, so
    retry before calling anything a failure — otherwise the script cries wolf and exits 1.

    -> (failures, summary)
    """
    today = time.strftime("%Y-%m-%d")
    checkable = {d: wid for d, wid in expected.items() if d >= today}
    skipped = len(expected) - len(checkable)
    if not checkable:
        return [], "read-back skipped: every date is in the past"

    failures, summary = [], ""
    for attempt in range(max(1, attempts)):
        failures, summary = _read_back_once(call, checkable, skipped)
        if not failures:
            return failures, summary
        if attempt < attempts - 1:
            time.sleep(delay)
    return failures, summary + "  (after %d attempts)" % attempts


def _read_back_once(call, checkable, skipped):
    lo, hi = min(checkable), max(checkable)
    res = call("get_scheduled_workouts", {"start_date": lo, "end_date": hi})
    rows = res.get("scheduled_workouts") if isinstance(res, dict) else None
    if rows is None:
        return (["calendar read-back failed"],
                "could not read the calendar back: %s" % str(res)[:200])

    on = {}
    for r in rows:
        on.setdefault(r.get("date"), set()).add(r.get("workout_id"))
    failures = []
    for d, wid in sorted(checkable.items()):
        if wid not in on.get(d, set()):
            failures.append("%s carries %s, expected workout id %s"
                            % (d, sorted(on.get(d, set())) or "nothing", wid))
    summary = "read back: %d/%d dates confirmed on the calendar%s" % (
        len(checkable) - len(failures), len(checkable),
        "  (%d past date(s) not verifiable)" % skipped if skipped else "")
    return failures, summary


def make_remote_get(call):
    """Adapt an MCP `call(tool, args)` into the `remote_get(workout_id)` that plan_actions wants.

    A transport failure raises RemoteLookupError; a 404 comes back as a normal response with
    no `id`, which `workout_exists` recognises as missing.
    """
    def remote_get(workout_id):
        res = call("get_workout_by_id", {"workout_id": workout_id})
        if isinstance(res, dict) and res.get("error"):
            raise RemoteLookupError("could not read workout %s: %s"
                                    % (workout_id,
                                       str(res.get("raw") or res.get("detail"))[:200]))
        return res
    return remote_get


def plan_actions(sessions, reg, remote_get):
    """Classify every session without changing anything.

    sessions : [{"date", "name", "kind", "expect", "fp", "call"}]
               `call` = (tool_name, args) used to build the workout when we must.
    remote_get : callable(workout_id) -> remote workout dict (injected, so this is offline-testable)

    -> [{"date","name","kind","action","old_id","reason", "fp", "call"}]
    """
    actions = []
    for s in sessions:
        prev = reg.get(s["name"])
        act = dict(s)                      # carry date/name/kind/expect/fp/call/summary through
        act["old_id"] = None
        act["reason"] = ""

        if not prev:
            act["action"] = "create"
            act["reason"] = "not in registry"
        else:
            old_id = prev["id"]
            act["old_id"] = old_id
            remote = remote_get(old_id)
            same_fp = prev.get("fp") == s["fp"] and prev.get("kind") == s["kind"]
            ok, why = remote_matches(s["kind"], s["expect"], remote)
            if not ok:
                act["action"] = "replace"
                act["reason"] = why
            else:
                act["action"] = "reuse"
                act["reason"] = ("fingerprint matches; " if same_fp
                                 else "cached fingerprint missing/stale, but ") + why
        actions.append(act)
    return actions

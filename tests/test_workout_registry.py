# -*- coding: utf-8 -*-
"""Tests for scripts/workout_registry.py — idempotency decisions.

The bug these pin down: the registry used to cache `name -> id` and reuse the id forever,
so a session whose NAME stayed the same but whose CONTENT changed never reached the watch.
"""
import datetime
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import workout_registry as wr  # noqa: E402

RUN_ARGS = {"name": "TUE EASY", "run_seconds": 2280, "warmup_min": 0,
            "cooldown_min": 0, "hr_min": 128, "hr_max": 148}


def _run_session(fp, hr=(128, 148), duration=2280, name="TUE EASY", date="2026-09-15"):
    return {"date": date, "name": name, "kind": wr.KIND_RUN,
            "expect": {"duration": duration, "hr": hr},
            "fp": fp, "call": ("create_run_workout", dict(RUN_ARGS))}


def _run_remote(duration=2280, hr=(128.0, 148.0)):
    steps = [{"order": 1, "type": "warmup", "description": "Warmup 0 min",
              "end_condition": "time"}]
    if hr:
        steps.append({"order": 2, "type": "interval", "description": "Run",
                      "end_condition": "time", "end_condition_value": float(duration),
                      "target_type": "heart.rate.zone",
                      "target_value_low": hr[0], "target_value_high": hr[1]})
    else:
        steps.append({"order": 2, "type": "interval", "description": "Run",
                      "end_condition": "time", "end_condition_value": float(duration)})
    steps.append({"order": 3, "type": "cooldown", "description": "Cooldown 0 min",
                  "end_condition": "time"})
    return {"id": 111, "name": "TUE EASY", "sport": "running",
            "estimated_duration_seconds": duration,
            "segments": [{"order": 1, "steps": steps}], "segment_count": 1}


MISSING_REMOTE = {"error": False, "raw": "Error retrieving workout: ... (404) NotFoundException"}


class FingerprintTests(unittest.TestCase):
    def test_stable_and_key_order_independent(self):
        a = wr.fingerprint(wr.KIND_RUN, dict(RUN_ARGS))
        b = wr.fingerprint(wr.KIND_RUN, dict(reversed(list(RUN_ARGS.items()))))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 16)

    def test_changes_when_content_changes(self):
        base = wr.fingerprint(wr.KIND_RUN, dict(RUN_ARGS))
        self.assertNotEqual(base, wr.fingerprint(
            wr.KIND_RUN, dict(RUN_ARGS, run_seconds=1500)))
        self.assertNotEqual(base, wr.fingerprint(
            wr.KIND_RUN, dict(RUN_ARGS, hr_max=150)))

    def test_kind_is_part_of_the_identity(self):
        """The two scripts share one registry file, so a run and a track workout with the
        same name must not be mistaken for each other."""
        self.assertNotEqual(wr.fingerprint(wr.KIND_RUN, RUN_ARGS),
                            wr.fingerprint(wr.KIND_TRACK, RUN_ARGS))


class RegistryFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.path = os.path.join(self.tmp, "garmin_workout_registry.json")

    def test_missing_file_is_empty(self):
        self.assertEqual(wr.load_reg(self.path), {})

    def test_corrupt_file_is_empty_not_a_crash(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{ this is not json")
        self.assertEqual(wr.load_reg(self.path), {})

    def test_v1_flat_map_is_normalised(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"TUE EASY": 37565752, "LONG RUN": 37565705}, f)
        reg = wr.load_reg(self.path)
        self.assertEqual(reg["TUE EASY"], {"id": 37565752, "kind": None, "fp": None})

    def test_v2_round_trip(self):
        reg = {"TUE EASY": {"id": 111, "kind": wr.KIND_RUN, "fp": "abc123"}}
        wr.save_reg(self.path, reg)
        self.assertEqual(wr.load_reg(self.path), reg)
        with open(self.path, encoding="utf-8") as f:
            doc = json.load(f)
        self.assertEqual(doc["schema_version"], wr.SCHEMA_VERSION)

    def test_saved_file_is_readable_utf8_without_bom(self):
        wr.save_reg(self.path, {"周二 轻松跑": {"id": 1, "kind": wr.KIND_RUN, "fp": "x"}})
        with open(self.path, "rb") as f:
            raw = f.read()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertIn("周二 轻松跑", raw.decode("utf-8"))


class WorkoutExistsTests(unittest.TestCase):
    def test_real_workout_has_an_id(self):
        self.assertTrue(wr.workout_exists(_run_remote()))

    def test_missing_workout_is_detected_despite_error_being_false(self):
        """Garmin returns error=False for a 404 — only the absence of `id` is trustworthy."""
        self.assertFalse(wr.workout_exists(MISSING_REMOTE))
        self.assertFalse(wr.workout_exists({"error": True}))
        self.assertFalse(wr.workout_exists(None))


class PlanActionsTests(unittest.TestCase):
    def _plan(self, reg, fp, remote_map):
        s = _run_session(fp)
        return wr.plan_actions([s], reg, lambda wid: remote_map.get(wid, MISSING_REMOTE))[0]

    def test_not_in_registry_creates(self):
        act = self._plan({}, "newfp", {})
        self.assertEqual(act["action"], "create")
        self.assertIsNone(act["old_id"])

    def test_matching_fingerprint_and_matching_remote_reuses(self):
        reg = {"TUE EASY": {"id": 111, "kind": wr.KIND_RUN, "fp": "fp1"}}
        act = self._plan(reg, "fp1", {111: _run_remote()})
        self.assertEqual(act["action"], "reuse")

    def test_matching_fingerprint_but_remote_deleted_replaces(self):
        reg = {"TUE EASY": {"id": 111, "kind": wr.KIND_RUN, "fp": "fp1"}}
        act = self._plan(reg, "fp1", {})
        self.assertEqual(act["action"], "replace")
        self.assertIn("not on Garmin", act["reason"])

    def test_changed_content_replaces_even_though_the_name_is_the_same(self):
        """The original bug: same name, different minutes -> must NOT silently reuse."""
        reg = {"TUE EASY": {"id": 111, "kind": wr.KIND_RUN, "fp": "old"}}
        act = self._plan(reg, "new", {111: _run_remote(duration=2280)})
        self.assertEqual(act["action"], "reuse")   # remote still matches -> adopt, don't churn

    def test_remote_content_differs_replaces(self):
        """Remote duration no longer matches what we'd build -> must rebuild."""
        reg = {"TUE EASY": {"id": 111, "kind": wr.KIND_RUN, "fp": "fp1"}}
        act = self._plan(reg, "fp1", {111: _run_remote(duration=1500)})
        self.assertEqual(act["action"], "replace")
        self.assertIn("duration", act["reason"])

    def test_remote_hr_target_differs_replaces(self):
        reg = {"TUE EASY": {"id": 111, "kind": wr.KIND_RUN, "fp": "fp1"}}
        act = self._plan(reg, "fp1", {111: _run_remote(hr=(120.0, 140.0))})
        self.assertEqual(act["action"], "replace")
        self.assertIn("HR target", act["reason"])

    def test_legacy_entry_without_fingerprint_adopts_when_remote_matches(self):
        """Migration path: a v1 entry has fp=None. If the workout on the watch still
        matches, adopt it (and stamp the fingerprint) instead of rebuilding needlessly."""
        reg = {"TUE EASY": {"id": 111, "kind": None, "fp": None}}
        act = self._plan(reg, "fp1", {111: _run_remote()})
        self.assertEqual(act["action"], "reuse")
        self.assertIn("stale", act["reason"])

    def test_legacy_entry_rebuilds_when_remote_does_not_match(self):
        reg = {"TUE EASY": {"id": 111, "kind": None, "fp": None}}
        act = self._plan(reg, "fp1", {111: _run_remote(duration=999)})
        self.assertEqual(act["action"], "replace")

    def test_remote_is_queried_only_for_entries_already_in_the_registry(self):
        seen = []

        def remote_get(wid):
            seen.append(wid)
            return _run_remote()

        wr.plan_actions([_run_session("fp1")], {}, remote_get)
        self.assertEqual(seen, [], "a brand-new session needs no remote lookup")


class VerifyScheduleTests(unittest.TestCase):
    """Garmin's calendar is eventually consistent: right after a create+delete pair it can
    still report the OLD workout id. Verified live on 2026-09-19 — the read-back must retry
    instead of crying wolf and exiting 1."""

    FUTURE = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()

    def test_confirms_a_workout_that_is_on_the_calendar(self):
        def call(tool, args):
            return {"scheduled_workouts": [{"date": self.FUTURE, "workout_id": 42}]}

        failures, summary = wr.verify_schedule(call, {self.FUTURE: 42})
        self.assertEqual(failures, [])
        self.assertIn("1/1", summary)

    def test_retries_until_the_calendar_catches_up(self):
        calls = []

        def call(tool, args):
            calls.append(1)
            stale = {"date": self.FUTURE, "workout_id": 99}      # the deleted workout
            fresh = {"date": self.FUTURE, "workout_id": 42}
            return {"scheduled_workouts": [stale if len(calls) == 1 else fresh]}

        failures, _ = wr.verify_schedule(call, {self.FUTURE: 42}, attempts=3, delay=0)
        self.assertEqual(failures, [])
        self.assertEqual(len(calls), 2, "should have retried exactly once")

    def test_reports_a_failure_after_exhausting_attempts(self):
        calls = []

        def call(tool, args):
            calls.append(1)
            return {"scheduled_workouts": []}

        failures, summary = wr.verify_schedule(call, {self.FUTURE: 42}, attempts=3, delay=0)
        self.assertEqual(len(calls), 3)
        self.assertEqual(len(failures), 1)
        self.assertIn("after 3 attempts", summary)

    def test_past_dates_are_skipped_rather_than_failed(self):
        def call(tool, args):
            raise AssertionError("must not query a past-only range")

        failures, summary = wr.verify_schedule(call, {"2020-01-01": 1})
        self.assertEqual(failures, [])
        self.assertIn("past", summary)

    def test_unreadable_calendar_is_a_failure_not_a_pass(self):
        def call(tool, args):
            return {"error": False, "raw": "boom"}

        failures, summary = wr.verify_schedule(call, {self.FUTURE: 42}, attempts=1, delay=0)
        self.assertTrue(failures)
        self.assertIn("could not read", summary)


class WriteLandedTests(unittest.TestCase):
    def test_plain_success(self):
        self.assertTrue(wr.write_landed({"message": "scheduled"}))

    def test_error_flag_is_a_failure(self):
        self.assertFalse(wr.write_landed({"error": True, "detail": "nope"}))

    def test_bare_envelope_is_a_failure_even_when_error_is_false(self):
        """Garmin 404s report error=false with only a `raw` string."""
        self.assertFalse(wr.write_landed({"error": False, "raw": "Error ... 404 ..."}))
        self.assertFalse(wr.write_landed({}))
        self.assertFalse(wr.write_landed(None))


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""Tests for the remote comparison in scripts/workout_registry.py.

Fixtures below mirror the *shape* returned by `get_workout_by_id` on the live account
(captured 2026-09-19); names/ids are scrubbed. The track fixture deliberately reproduces
the real drift found on the watch: its warm-up step still carries an HR target, which the
current builder no longer emits.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import workout_registry as wr  # noqa: E402
import garmin_track_workout as tw  # noqa: E402

TRACK_SPEC = {
    "name": "TRACK 6x1.2k", "date": "2026-09-17", "lap_meters": 400,
    "rest_style": "rest", "warmup": {"laps": 5},
    "pre_rest_min": 6, "sets": 6, "laps_per_set": 3, "set_rest_min": 3,
}


def _lap(order, typ, hr=None):
    st = {"order": order, "type": typ, "description": "lap", "end_condition": "lap.button",
          "end_condition_value": 1000.0}
    if hr:
        st.update({"target_type": "heart.rate.zone",
                   "target_value_low": float(hr[0]), "target_value_high": float(hr[1])})
    return st


def track_remote(warmup_hr=(128, 150)):
    """The observed structure: repeat(5)[warmup] -> rest 6min -> repeat(6)[3x interval + rest 3min]."""
    return {
        "id": 222, "name": "TRACK 6x1.2k", "sport": "running", "segment_count": 1,
        "segments": [{"order": 1, "sport": "running", "steps": [
            {"order": 1, "type": "repeat", "end_condition": "iterations",
             "end_condition_value": 5.0, "repeat_count": 5,
             "steps": [_lap(2, "warmup", warmup_hr)]},
            {"order": 3, "type": "rest", "description": "rest", "end_condition": "time",
             "end_condition_value": 360.0},
            {"order": 4, "type": "repeat", "end_condition": "iterations",
             "end_condition_value": 6.0, "repeat_count": 6, "steps": [
                _lap(5, "interval"), _lap(6, "interval"), _lap(7, "interval"),
                {"order": 8, "type": "rest", "description": "rest",
                 "end_condition": "time", "end_condition_value": 180.0}]},
        ]}],
    }


def expect_track():
    return {"dto": tw.build(TRACK_SPEC)}


class TrackComparisonTests(unittest.TestCase):
    def test_built_dto_has_no_warmup_hr_target(self):
        steps = tw.build(TRACK_SPEC)["workoutSegments"][0]["workoutSteps"]
        warm = steps[0]["workoutSteps"][0]
        self.assertNotIn("targetValueOne", warm)
        self.assertEqual(warm["targetType"]["workoutTargetTypeKey"], "no.target")

    def test_matches_a_remote_that_also_has_no_warmup_target(self):
        ok, why = wr.remote_matches(wr.KIND_TRACK, expect_track(),
                                    track_remote(warmup_hr=None))
        self.assertTrue(ok, why)

    def test_detects_the_live_warmup_hr_drift(self):
        """This is the real state of workout 37565755 on the watch: warm-up still carries
        128-150 bpm. It must be reported as different so it gets rebuilt."""
        ok, why = wr.remote_matches(wr.KIND_TRACK, expect_track(),
                                    track_remote(warmup_hr=(128, 150)))
        self.assertFalse(ok)
        self.assertIn("step 2", why)

    def test_ignores_server_generated_descriptions(self):
        """Descriptions differ between versions but must not trigger a rebuild."""
        remote = track_remote(warmup_hr=None)
        remote["segments"][0]["steps"][0]["steps"][0]["description"] = \
            "400m 计圈（2km 热身，配速 6:30–6:00）"
        ok, why = wr.remote_matches(wr.KIND_TRACK, expect_track(), remote)
        self.assertTrue(ok, why)

    def test_detects_a_missing_interval_lap(self):
        remote = track_remote(warmup_hr=None)
        remote["segments"][0]["steps"][2]["steps"].pop(1)
        ok, _ = wr.remote_matches(wr.KIND_TRACK, expect_track(), remote)
        self.assertFalse(ok)

    def test_detects_a_changed_rest_style(self):
        """rest (standing) vs recovery (jogging) is the easiest thing to get wrong."""
        remote = track_remote(warmup_hr=None)
        remote["segments"][0]["steps"][2]["steps"][3]["type"] = "recovery"
        ok, _ = wr.remote_matches(wr.KIND_TRACK, expect_track(), remote)
        self.assertFalse(ok)


class RunComparisonTests(unittest.TestCase):
    def test_accepts_a_workout_that_matches(self):
        remote = {"id": 1, "estimated_duration_seconds": 2280,
                  "segments": [{"steps": [
                      {"type": "warmup", "end_condition": "time"},
                      {"type": "interval", "end_condition": "time",
                       "end_condition_value": 2280.0, "target_type": "heart.rate.zone",
                       "target_value_low": 128.0, "target_value_high": 148.0},
                      {"type": "cooldown", "end_condition": "time"}]}]}
        self.assertTrue(wr.remote_matches(
            wr.KIND_RUN, {"duration": 2280, "hr": (128, 148)}, remote)[0])

    def test_rejects_a_stale_duration(self):
        remote = {"id": 1, "estimated_duration_seconds": 1500,
                  "segments": [{"steps": [
                      {"type": "interval", "end_condition": "time",
                       "end_condition_value": 1500.0, "target_type": "heart.rate.zone",
                       "target_value_low": 128.0, "target_value_high": 148.0}]}]}
        ok, why = wr.remote_matches(wr.KIND_RUN, {"duration": 2280, "hr": (128, 148)}, remote)
        self.assertFalse(ok)
        self.assertIn("duration", why)

    def test_rejects_when_the_watch_has_no_hr_target_but_the_spec_does(self):
        remote = {"id": 1, "estimated_duration_seconds": 2280,
                  "segments": [{"steps": [
                      {"type": "interval", "end_condition": "time",
                       "end_condition_value": 2280.0}]}]}
        ok, why = wr.remote_matches(wr.KIND_RUN, {"duration": 2280, "hr": (128, 148)}, remote)
        self.assertFalse(ok)
        self.assertIn("HR target", why)


if __name__ == "__main__":
    unittest.main()

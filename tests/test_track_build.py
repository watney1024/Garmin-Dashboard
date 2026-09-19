# -*- coding: utf-8 -*-
"""Tests for scripts/garmin_track_workout.py's DTO builder.

The rule pinned here (runner's instruction, 2026-09-19): **the warm-up of a track session
must carry no heart-rate target.** During a warm-up the heart rate climbs from resting, so
an HR band on that step just fires low-HR alerts the whole way. Cooldown already had none;
warm-up did not.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import garmin_track_workout as tw  # noqa: E402

BASE_SPEC = {
    "name": "TRACK 6x1.2k", "date": "2026-09-17", "lap_meters": 400,
    "rest_style": "rest", "warmup": {"laps": 5},
    "pre_rest_min": 6, "sets": 6, "laps_per_set": 3, "set_rest_min": 3,
}


def steps_of(dto):
    return dto["workoutSegments"][0]["workoutSteps"]


def all_steps(steps):
    out = []
    for st in steps:
        out.append(st)
        out.extend(all_steps(st.get("workoutSteps") or []))
    return out


class WarmupTargetTests(unittest.TestCase):
    def test_warmup_has_no_hr_target(self):
        dto = tw.build(BASE_SPEC)
        warm = steps_of(dto)[0]["workoutSteps"][0]
        self.assertEqual(warm["type"], "ExecutableStepDTO")
        self.assertEqual(warm["stepType"]["stepTypeKey"], "warmup")
        self.assertEqual(warm["targetType"]["workoutTargetTypeKey"], "no.target")
        self.assertNotIn("targetValueOne", warm)
        self.assertNotIn("targetValueTwo", warm)

    def test_warmup_hr_in_the_spec_is_ignored_not_applied(self):
        """Older specs (including the runner's W2 one) carried warmup.hr_min/hr_max.
        They must not resurrect the target — the builder ignores them."""
        spec = dict(BASE_SPEC, warmup={"laps": 5, "hr_min": 128, "hr_max": 150})
        warm = steps_of(tw.build(spec))[0]["workoutSteps"][0]
        self.assertEqual(warm["targetType"]["workoutTargetTypeKey"], "no.target")
        self.assertNotIn("targetValueOne", warm)

    def test_no_step_in_a_track_session_carries_an_hr_target(self):
        for st in all_steps(steps_of(tw.build(BASE_SPEC))):
            if "targetType" in st:
                self.assertEqual(st["targetType"]["workoutTargetTypeKey"], "no.target",
                                 "unexpected target on %s" % st.get("stepType"))

    def test_cooldown_still_has_no_target(self):
        spec = dict(BASE_SPEC, cooldown={"laps": 2})
        cool = steps_of(tw.build(spec))[-1]["workoutSteps"][0]
        self.assertEqual(cool["stepType"]["stepTypeKey"], "cooldown")
        self.assertEqual(cool["targetType"]["workoutTargetTypeKey"], "no.target")


class StructureTests(unittest.TestCase):
    def test_step_order_is_strictly_increasing(self):
        orders = [st["stepOrder"] for st in all_steps(steps_of(tw.build(BASE_SPEC)))]
        self.assertEqual(orders, sorted(orders))
        self.assertEqual(len(orders), len(set(orders)), "stepOrder must be unique")

    def test_rest_style_rest_is_a_standing_rest(self):
        dto = tw.build(dict(BASE_SPEC, rest_style="rest"))
        rests = [s for s in all_steps(steps_of(dto))
                 if s["stepType"]["stepTypeKey"] in ("rest", "recovery")]
        self.assertTrue(rests)
        for r in rests:
            self.assertEqual(r["stepType"]["stepTypeKey"], "rest")

    def test_rest_style_recovery_is_a_jog(self):
        dto = tw.build(dict(BASE_SPEC, rest_style="recovery"))
        inside = steps_of(dto)[2]["workoutSteps"]
        self.assertEqual(inside[-1]["stepType"]["stepTypeKey"], "recovery")

    def test_bad_rest_style_is_rejected(self):
        with self.assertRaises(SystemExit):
            tw.build(dict(BASE_SPEC, rest_style="walk"))

    def test_warmup_is_omitted_when_not_requested(self):
        spec = dict(BASE_SPEC)
        spec.pop("warmup")
        kinds = [s["stepType"]["stepTypeKey"] for s in all_steps(steps_of(tw.build(spec)))]
        self.assertNotIn("warmup", kinds)
        self.assertIn("interval", kinds)

    def test_lap_distance_is_decoupled_from_the_watch_lap(self):
        """Each press records a nominal 400 m regardless of the real track lap."""
        warm = steps_of(tw.build(BASE_SPEC))[0]["workoutSteps"][0]
        self.assertEqual(warm["endCondition"]["conditionTypeKey"], "lap.button")
        self.assertEqual(warm["endConditionValue"], 1000.0)


if __name__ == "__main__":
    unittest.main()

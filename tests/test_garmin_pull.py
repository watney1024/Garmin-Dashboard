# -*- coding: utf-8 -*-
"""Tests for scripts/garmin_pull.py — the master-CSV data-loss paths.

Run:  python -m unittest discover -s tests -v

Why these exist: `fetch_all` used to turn any error response into an empty list, and
`rebuild_master` truncates the master CSV in place — so one flaky call (expired token,
network blip) could rewrite months of history down to a header-only file and still exit 0.
"""
import argparse
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import garmin_pull as gp  # noqa: E402


def _act(i, day="2026-09-01"):
    return {
        "id": 1000 + i, "type": "running",
        "start_time": "%sT%02d:00:00.0" % (day, i % 24),
        "name": "run %d" % i, "distance_meters": 5000, "duration_seconds": 1800,
        "moving_duration_seconds": 1700, "calories": 300, "avg_hr_bpm": 140,
        "max_hr_bpm": 160, "steps": 5000, "elevation_gain_meters": 10,
        "elevation_loss_meters": 10, "event_type": "uncategorized",
    }


class FakeMCP:
    """Stands in for garmin_pull.MCP. `pages` are returned in order, one per call."""

    def __init__(self, pages):
        self.pages = list(pages)
        self.calls = []
        self.closed = False
        self.repeat_last = False

    def connect(self):
        pass

    def call(self, name, args, timeout=150):
        self.calls.append((name, args))
        if self.pages:
            return self.pages.pop(0)
        if self.repeat_last:
            return self.last if hasattr(self, "last") else []
        return []

    def close(self):
        self.closed = True


class MasterTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cfg = argparse.Namespace(data_dir=self.tmp, src="x", uvx="uvx", pyver="3.12")
        self.master = os.path.join(self.tmp, "Activities.csv")

    def read_master(self):
        with open(self.master, "rb") as f:
            return f.read()


class RebuildMasterTests(MasterTestCase):
    def test_writes_bom_header_and_one_row_per_activity(self):
        n = gp.rebuild_master(self.cfg, [_act(i) for i in range(3)])
        self.assertEqual(n, 3)
        raw = self.read_master()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"), "master must keep its utf-8-sig BOM")
        lines = raw.decode("utf-8-sig").rstrip("\n").split("\n")
        self.assertEqual(len(lines), 4)                       # header + 3
        self.assertEqual(lines[0], ",".join(gp.HDR))
        self.assertEqual(len(lines[0].split(",")), 16)        # 16-column schema preserved

    def test_sorted_newest_first(self):
        gp.rebuild_master(self.cfg, [_act(1, "2026-01-01"), _act(2, "2026-05-05")])
        body = self.read_master().decode("utf-8-sig").split("\n")[1:]
        self.assertIn("2026-05-05", body[0])

    def test_empty_fetch_refuses_to_clobber_an_existing_master(self):
        gp.rebuild_master(self.cfg, [_act(i) for i in range(5)])
        before = self.read_master()
        with self.assertRaises(gp.GarminFetchError):
            gp.rebuild_master(self.cfg, [])
        self.assertEqual(self.read_master(), before,
                         "an empty fetch must never truncate the existing master")

    def test_empty_fetch_is_allowed_when_no_master_exists_yet(self):
        n = gp.rebuild_master(self.cfg, [])
        self.assertEqual(n, 0)
        self.assertTrue(os.path.exists(self.master))

    def test_write_failure_leaves_the_original_intact_and_no_temp_files(self):
        gp.rebuild_master(self.cfg, [_act(i) for i in range(5)])
        before = self.read_master()

        def boom(*a, **k):
            raise OSError("disk full")

        real_replace = os.replace
        os.replace = boom
        try:
            with self.assertRaises(OSError):
                gp.rebuild_master(self.cfg, [_act(i) for i in range(50)])
        finally:
            os.replace = real_replace

        self.assertEqual(self.read_master(), before)
        leftovers = [f for f in os.listdir(self.tmp) if f != "Activities.csv"]
        self.assertEqual(leftovers, [], "temp file must be cleaned up on failure")


class FetchAllTests(MasterTestCase):
    def _fetch(self, pages, **fake_kw):
        fake = FakeMCP(pages)
        fake.__dict__.update(fake_kw)
        real = gp.MCP
        gp.MCP = lambda *a, **k: fake
        try:
            return gp.fetch_all(self.cfg), fake
        finally:
            gp.MCP = real

    def test_single_short_page(self):
        acts, _ = self._fetch([[_act(i) for i in range(50)]])
        self.assertEqual(len(acts), 50)

    def test_paginates_until_a_short_page(self):
        pages = [[_act(i) for i in range(100)],
                 [_act(i) for i in range(100, 200)],
                 [_act(i) for i in range(200, 230)]]
        acts, fake = self._fetch(pages)
        self.assertEqual(len(acts), 230)
        self.assertEqual([c[1]["start"] for c in fake.calls], [0, 100, 200])

    def test_error_response_raises_instead_of_looking_empty(self):
        with self.assertRaises(gp.GarminFetchError):
            self._fetch([{"error": True, "raw": "token expired"}])

    def test_error_partway_through_raises_instead_of_silently_truncating(self):
        pages = [[_act(i) for i in range(100)], {"error": True, "raw": "boom"}]
        with self.assertRaises(gp.GarminFetchError):
            self._fetch(pages)

    def test_unexpected_response_shape_raises(self):
        with self.assertRaises(gp.GarminFetchError):
            self._fetch([{"unexpected": 1}])

    def test_repeated_page_raises_instead_of_looping_forever(self):
        same = [_act(i) for i in range(100)]
        with self.assertRaises(gp.GarminFetchError):
            self._fetch([same, same, same])

    def test_page_cap_raises_instead_of_running_forever(self):
        real_cap = gp.MAX_PAGES
        gp.MAX_PAGES = 3
        try:
            pages = [[_act(i) for i in range(0, 100)],
                     [_act(i) for i in range(100, 200)],
                     [_act(i) for i in range(200, 300)],
                     [_act(i) for i in range(300, 400)]]
            with self.assertRaises(gp.GarminFetchError):
                self._fetch(pages)
        finally:
            gp.MAX_PAGES = real_cap


if __name__ == "__main__":
    unittest.main()

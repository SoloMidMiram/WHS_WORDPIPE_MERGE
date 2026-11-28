import json
import tempfile
import unittest
from pathlib import Path
from collect import attempts, digest, distribution, load, replay_sanitized

class CollectorTests(unittest.TestCase):
    def test_committed_receipts_and_frozen_cohort(self):
        root = Path(__file__).resolve().parent
        evidence = root / "evidence"
        summary = replay_sanitized(evidence)
        self.assertEqual({mode: (r["attempts"], r["failure_rate"])
                          for mode, r in summary.items()}, {"legacy": (3, 0), "structural": (3, 0)})
        reg = load(evidence / "registration.json")
        self.assertEqual(digest(evidence / "fixture.json"), reg["fixture_sha256"])
        fixture = load(evidence / "fixture.json")
        self.assertEqual(len(fixture["files"]), 5)
        for item in fixture["files"]:
            path = root / "fixture" / item["file"]
            self.assertEqual(digest(path), item["sha256"])
            self.assertEqual(path.stat().st_size, item["bytes"])
        for mode, expected in reg["manifests"].items():
            self.assertEqual(digest(evidence / f"{mode}.json"), expected)

    def test_repeatable_inclusive_distribution_and_tail_omission(self):
        self.assertEqual(distribution([1, 3, 7]), distribution([7, 1, 3]))
        self.assertEqual(distribution([1, 3, 7]), dict(n=3, minimum=1, maximum=7, median=3, iqr=3, mad=2))

    def test_failed_and_timeout_terminals_are_retained(self):
        rows = [
            dict(mode="legacy", id="success", exit=0, elapsed=1),
            dict(mode="legacy", id="error", exit=1, elapsed=2),
            dict(mode="legacy", id="timeout", exit=124, elapsed=3),
        ]
        for i, row in enumerate(rows, 1):
            row.update(attempt=i, utc="2026-11-27T00:00:00Z")
        expected={(row["mode"], row["id"]) for row in rows}
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "run.jsonl"
            p.write_text("\n".join(map(json.dumps, rows)), encoding="utf-8")
            self.assertEqual(list(attempts(p, expected)), rows)
            for invalid in (True, float("nan"), float("inf"), -1, "1"):
                p.write_text(json.dumps(dict(rows[0], elapsed=invalid)), encoding="utf-8")
                with self.assertRaises(ValueError):
                    list(attempts(p, expected))
            for invalid in (dict(rows[0], exit=True), dict(rows[0], attempt=True), {}):
                p.write_text(json.dumps(invalid), encoding="utf-8")
                with self.assertRaises(ValueError):
                    list(attempts(p, expected))
            p.write_text(json.dumps(rows[0]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing registered"):
                list(attempts(p, expected))
            p.write_text(json.dumps(rows[0])+"\n"+json.dumps(rows[0]), encoding="utf-8")
            with self.assertRaises(ValueError):
                list(attempts(p, expected))
            p.write_text('{"mode":', encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                list(attempts(p, expected))

if __name__ == "__main__":
    unittest.main()

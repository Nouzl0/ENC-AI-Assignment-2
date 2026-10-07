import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from selection import check_validation_metrics, choose_candidate, validation_selection


class SelectionTests(unittest.TestCase):
    def test_full_precision_threshold_lengths_and_tie(self):
        lengths = {"P3A": 200, "P3B": 100}
        self.assertEqual(choose_candidate({"P3A": .6, "P3B": .580001}, lengths), "P3B")
        self.assertEqual(choose_candidate({"P3A": .6, "P3B": .5800000000005}, lengths), "P3B")
        self.assertEqual(choose_candidate({"P3A": .6, "P3B": .58}, lengths), "P3A")
        self.assertEqual(choose_candidate({"P3A": .7, "P3B": .68}, lengths), "P3A")
        self.assertEqual(choose_candidate({"P3A": .5, "P3B": .5}, dict(P3A=100, P3B=100)), "P3A")
        self.assertEqual(choose_candidate({"P3B": 0}, {"P3B": 100}), "P3B")
        for bad in (float("nan"), float("inf"), -1, 1.1, None, "0.5", True):
            with self.assertRaises(ValueError):
                choose_candidate({"P3A": bad}, {"P3A": 100})

    def test_malformed_or_empty_snapshot_fails_closed(self):
        good = dict(schema_version=1, kind="scoring_input_snapshot",
                    tables={name: [] for name in ("runs", "key", "pairs", "answers", "meta")})
        malformed = [None, [], dict(good, tables=[])]
        for name in good["tables"]:
            for value in (None, {}, ["not a row"]):
                bad = copy.deepcopy(good); bad["tables"][name] = value
                malformed.append(bad)
        for snapshot in malformed + [good]:
            with self.subTest(snapshot=snapshot), self.assertRaises(ValueError):
                validation_selection(snapshot, [], {}, dict(systems=["sys"], val_candidates=["P3A"]), Path("/unused"))

    def test_metrics_are_unique_finite_and_recomputed(self):
        cells = {("sys", "P2"): dict(precision=1 / 3, n_cases=10, n_answers=10),
                 ("sys", "P3A"): dict(precision=.8, n_cases=10, n_answers=10)}
        rows = [dict(split="val", system=s, condition=c, precision=".3333" if c == "P2" else ".8", n_cases="10", n_answers="10") for s, c in cells]
        check_validation_metrics(rows, cells)
        for bad in (rows[:-1], rows + [rows[0]], [dict(rows[0], condition="unknown"), rows[1]]):
            with self.assertRaises(ValueError):
                check_validation_metrics(bad, cells)
        for field, value in (("precision", "NaN"), ("precision", ""), ("precision", ".5"), ("n_answers", "9"), ("n_cases", "10.1")):
            bad = copy.deepcopy(rows); bad[0][field] = value
            with self.assertRaises(ValueError):
                check_validation_metrics(bad, cells)


if __name__ == "__main__":
    unittest.main()

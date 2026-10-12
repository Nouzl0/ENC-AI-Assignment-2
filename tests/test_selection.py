import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from selection import check_validation_metrics, choose_candidate, validation_selection
from test_scoring import fixture


class SelectionTests(unittest.TestCase):
    def test_recomputed_full_precision_means_preserve_point02_boundary(self):
        snapshot = dict(schema_version=1, kind="scoring_input_snapshot",
                        tables={name: [] for name in ("runs", "key", "pairs", "answers", "meta")})
        tables = snapshot["tables"]
        cases = {}
        systems = [f"sys_{i}" for i in range(5)]
        for task in range(10):
            for system in systems:
                for condition, n_supported in (("P2", 5), ("P3A", 8), ("P3B", 6)):
                    run, key, pair, answer, source_cases = fixture()
                    bid = f"A-{task}-{system}-{condition}"
                    tid = f"DEMO-{task}"
                    run.update(run_id=bid, task_id=tid, phase="val", split="val", system=system, condition=condition)
                    key.update(blind_answer_id=bid, run_id=bid)
                    answer.update(blind_answer_id=bid, n_claims="100", key_fact_evidence='{"RF1":["' + bid + '-T1-1"]}')
                    tables["runs"].append(run); tables["key"].append(key); tables["answers"].append(answer)
                    tables["pairs"].extend(dict(pair, pair_id=f"{bid}-T{i}-1", blind_answer_id=bid,
                                                 claim_id=f"T{i}", rating="S2" if i <= n_supported else "S0")
                                            for i in range(1, 101))
                    cases[tid] = dict(source_cases["TEST"], development_validation_test_split="val")
        config = dict(systems=systems, val_candidates=["P3A", "P3B"])
        with tempfile.TemporaryDirectory() as directory:
            prompts = Path(directory)
            for candidate, length in (("P3A", 200), ("P3B", 100)):
                for lang in ("cs", "en"):
                    (prompts / f"{candidate}_candidate_{lang}.txt").write_text("x" * length, encoding="utf-8")
            summary, _ = validation_selection(snapshot, tables["runs"], cases, config, prompts)
            self.assertEqual(summary["precision_means"], {"P3A": .08, "P3B": .06})
            self.assertEqual(summary["selected_candidate"], "P3A")
            # G2 uses the same fail-closed RF evidence guard as scoring.
            tables["answers"][0]["key_fact_evidence"] = '{"RF1":[],"RF1":[]}'
            with self.assertRaisesRegex(ValueError, "required-fact"):
                validation_selection(snapshot, tables["runs"], cases, config, prompts)

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

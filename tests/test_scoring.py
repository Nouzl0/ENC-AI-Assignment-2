"""Offline regression tests; no product calls and no benchmark measurements."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))
from common import finite_number, run_problems, validate_pair_rows
from score import attribution_summary, bootstrap_ci, bootstrap_diagnostic, case_values, cohen_kappa, load_answers, mean, repeat_summary, test_matrix_problems, wilson


def fixture():
    run = dict(run_id="r1", task_id="TEST", system="chatgpt", condition="P2", split="test",
               language="en", run_index="1", run_status="completed", failure_type="none",
               answer_file="answer.txt", retries="0", first_attempt_ok="yes", final_attempt_ok="yes",
               latency_s="2", first_attempt_latency_s="2")
    key = dict(blind_answer_id="A1", run_id="r1")
    pair = dict(pair_id="A1-T1-1", blind_answer_id="A1", claim_id="T1", citation_n="1", rating="S2", source_tier="1", time_ok="na")
    answer = dict(blind_answer_id="A1", correctness="2", n_key_facts="1",
                  key_facts_supported="1", key_fact_evidence='{"RF1": ["A1-T1-1"]}', check_minutes="1", n_claims="1", segmentation_reviewed="yes", acknowledges_uncertainty="na")
    cases = {"TEST": dict(development_validation_test_split="test", language="en",
                         reference_answer_or_tests={"key_facts": ["required"]})}
    return run, key, pair, answer, cases


class ScoringIntegrityTests(unittest.TestCase):
    def test_float_means_preserve_the_exact_hypothesis_boundary(self):
        values = {f"DEMO-{i}": .2 - .1 for i in range(10)}
        point, lo, hi = bootstrap_ci(values, 200, 2026)
        self.assertEqual(point, .1)
        self.assertGreater(lo, 0)
        self.assertTrue(point >= .1)  # H1 must not depend on the Python sum implementation.
        self.assertEqual(mean([.08] * 10), .08)
        rows = [dict(task_id="DEMO-1", precision=.08) for _ in range(10)]
        self.assertEqual(case_values(rows, "precision"), {"DEMO-1": .08})

    def test_diagnostics_are_explicit_and_unknown_does_not_improve_coverage(self):
        run, key, pair, answer, cases = fixture()
        cases["TEST"]["edge_case_type"] = "time_constraint"
        pair["source_tier"] = "unknown"; pair["time_ok"] = "unknown"
        scored, problems = load_answers([run], [key], [pair], [answer], cases, False)
        self.assertEqual(problems, [])
        self.assertEqual((scored[0]["n_tier_checked"], scored[0]["n_time_checked"], scored[0]["n_time_expected"]), (0, 0, 1))
        for field in ("source_tier", "time_ok"):
            bad = dict(pair); bad[field] = ""
            self.assertTrue(load_answers([run], [key], [bad], [answer], cases, False)[1])
        cases["TEST"]["edge_case_type"] = "ambiguous"; pair["time_ok"] = "na"
        for ack in ("", "na", "maybe"):
            answer["acknowledges_uncertainty"] = ack
            self.assertTrue(load_answers([run], [key], [pair], [answer], cases, False)[1])
        answer["acknowledges_uncertainty"] = "unknown"
        self.assertEqual(load_answers([run], [key], [pair], [answer], cases, False)[1], [])

    def test_h2_decomposition_and_constant_bootstrap_warning(self):
        items = [dict(n_pairs=1, precision=1), dict(n_pairs=0, precision=0)]
        summary = attribution_summary(items)
        self.assertEqual(summary["explicit_answer_share"], .5)
        self.assertEqual(summary["precision_given_explicit"], 1)
        self.assertEqual(summary["precision_given_explicit_n"], 1)
        self.assertIsNone(attribution_summary([items[1]])["precision_given_explicit"])
        values = {i: 1 for i in range(10)}
        self.assertEqual(bootstrap_ci(values, 200, 2026), (1, 1, 1))
        self.assertEqual(bootstrap_diagnostic(values), "constant_empirical_sample")
        self.assertLess(wilson(10, 10)[1], 1)

    def test_failed_run_without_answer_is_zero_not_dropped(self):
        run, key, pair, answer, cases = fixture()
        failed = dict(run, run_id="r2", task_id="FAIL", run_status="failed", failure_type="product_outage",
                      first_attempt_ok="no", final_attempt_ok="no", answer_file="")
        cases["FAIL"] = dict(cases["TEST"])
        scored, problems = load_answers([run, failed], [key], [pair], [answer], cases, False)
        self.assertEqual(problems, [])
        self.assertEqual(len(scored), 2)
        self.assertEqual(sum(a["precision"] for a in scored) / 2, 0.5)
        self.assertEqual(scored[1]["correct"], 0)

    def test_missing_completed_rating_is_reported(self):
        run, key, pair, answer, cases = fixture()
        scored, problems = load_answers([run], [], [], [], cases, False)
        self.assertEqual(scored, [])
        self.assertTrue(any("missing key or answer" in p for p in problems))

    def test_allow_missing_excludes_whole_answer(self):
        run, key, pair, answer, cases = fixture()
        unrated = dict(pair, pair_id="A1-T2-1", claim_id="T2", rating="")
        answer["n_claims"] = "2"
        scored, problems = load_answers([run], [key], [pair, unrated], [answer], cases, True)
        self.assertEqual(scored, [])
        self.assertTrue(problems)

    def test_duplicate_ids_never_overwrite_even_in_partial_mode(self):
        run, key, pair, answer, cases = fixture()
        for position in range(4):
            inputs = [[run], [key], [pair], [answer]]
            inputs[position] *= 2
            with self.subTest(position=position), self.assertRaises(ValueError):
                load_answers(*inputs, cases, True)

    def test_duplicate_pair_identity_with_new_id_is_rejected(self):
        run, key, pair, answer, cases = fixture()
        with self.assertRaises(ValueError):
            load_answers([run], [key], [pair, dict(pair, pair_id="different")], [answer], cases, False)
        with self.assertRaises(ValueError):
            validate_pair_rows([pair, dict(pair, pair_id="copy", citation_n="01")], "raw rater")

    def test_na_and_fab_remain_in_denominator(self):
        run, key, pair, answer, cases = fixture()
        pairs = [dict(pair, pair_id=f"A1-T{i}-1", claim_id=f"T{i}", rating=rating)
                 for i, rating in enumerate(("S2", "NA", "FAB"), 1)]
        answer["n_claims"] = "3"
        scored, problems = load_answers([run], [key], pairs, [answer], cases, False)
        self.assertEqual(problems, [])
        self.assertAlmostEqual(scored[0]["precision"], 1 / 3)
        self.assertEqual(scored[0]["precision_noNA"], 0.5)

    def test_unlinked_source_list_cannot_repair_main_attribution(self):
        run, key, pair, answer, cases = fixture()
        pair.update(pair_id="A1-T1-*", citation_n="*")
        answer.update(key_facts_supported="0", key_fact_evidence="{}")
        scored, problems = load_answers([run], [key], [pair], [answer], cases, False)
        self.assertEqual(problems, [])
        self.assertEqual(scored[0]["precision"], 0)
        self.assertEqual(scored[0]["recall"], 0)
        self.assertEqual(scored[0]["kf_cov"], 0)
        self.assertEqual(scored[0]["unlinked_support"], 1)
        answer.update(key_facts_supported="1", key_fact_evidence='{"RF1": ["A1-T1-*"]}')
        scored, problems = load_answers([run], [key], [pair], [answer], cases, False)
        self.assertEqual(scored, [])
        self.assertTrue(problems)

    def test_required_fact_denominator_is_not_editable_by_rater(self):
        run, key, pair, answer, cases = fixture()
        answer["n_key_facts"] = "2"
        scored, problems = load_answers([run], [key], [pair], [answer], cases, False)
        self.assertEqual(scored, [])
        self.assertTrue(problems)

    def test_required_fact_guard_preserves_score_rating_normalization(self):
        run, key, pair, answer, cases = fixture()
        pair["rating"] = " s2 "
        scored, problems = load_answers([run], [key], [pair], [answer], cases, False)
        self.assertEqual(problems, [])
        self.assertEqual(scored[0]["kf_cov"], 1)

    def test_duplicate_required_fact_evidence_never_overwrites(self):
        for evidence in ('{"RF1":["bogus"],"RF1":["A1-T1-1"]}',
                         '{"RF1":["A1-T1-1"],"RF1":["bogus"]}',
                         '{"RF1":["A1-T1-1"],"RF1":["A1-T1-1"]}'):
            for partial in (False, True):
                with self.subTest(evidence=evidence, partial=partial):
                    run, key, pair, answer, cases = fixture()
                    answer["key_fact_evidence"] = evidence
                    scored, problems = load_answers([run], [key], [pair], [answer], cases, partial)
                    self.assertEqual(scored, [])
                    self.assertTrue(any("required-fact" in p for p in problems))

    def test_uncited_e9_and_duplicate_citation_error_count(self):
        run, key, pair, answer, cases = fixture()
        pairs = [dict(pair, error_code="E2"), dict(pair, pair_id="A1-T1-2", citation_n="2", error_code="E2"),
                 dict(pair, pair_id="A1-T2-none", claim_id="T2", citation_n="", rating="", error_code="E9")]
        answer["n_claims"] = "2"
        scored, problems = load_answers([run], [key], pairs, [answer], cases, False)
        self.assertEqual(problems, [])
        self.assertEqual(scored[0]["errors"], ["E2", "E9"])

    def test_nonfinite_and_invalid_counts_rejected(self):
        for value in ("NaN", "inf", "-inf", "oops", None):
            self.assertIsNone(finite_number(value))
        run, key, pair, answer, cases = fixture()
        answer["key_facts_supported"] = "2"
        scored, problems = load_answers([run], [key], [pair], [answer], cases, False)
        self.assertEqual(scored, [])
        self.assertTrue(problems)
        self.assertTrue(run_problems(dict(run, latency_s="NaN")))

    def test_missing_or_nonfinite_claim_count_cannot_hide_deleted_claims(self):
        run, key, pair, answer, cases = fixture()
        for value in ("", "NaN", "not-a-number", "2"):
            with self.subTest(value=value):
                scored, problems = load_answers([run], [key], [pair], [dict(answer, n_claims=value)], cases, False)
                self.assertEqual(scored, [])
                self.assertTrue(problems)

    def test_retry_outcome_and_matrix_identity_are_canonical(self):
        run, key, pair, answer, cases = fixture()
        self.assertTrue(run_problems(dict(run, retries="0.0", first_attempt_ok="no")))
        self.assertTrue(run_problems(dict(run, retries="1", attempt1_file="log.txt")))
        with self.assertRaises(ValueError):
            load_answers([run, dict(run, run_id="r2", run_index="01")], [key], [pair], [answer], cases, False)
        scored, problems = load_answers([dict(run, run_index="1,0")], [key], [pair], [answer], cases, False)
        self.assertEqual(problems, [])
        self.assertEqual(scored[0]["run_index"], 1)

    def test_one_system_cannot_confirm_hypotheses(self):
        cases = {str(i): {"development_validation_test_split": "test" if i < 10 else "dev"} for i in range(40)}
        answers = [dict(task_id=str(i), system="chatgpt", condition=c, split="test", run_index=1)
                   for i in range(10) for c in ("P1", "P2", "P3")]
        self.assertTrue(test_matrix_problems(answers, cases, ["chatgpt"]))
        self.assertTrue(test_matrix_problems(answers, cases, ["chatgpt", "gemini", "claude", "perplexity"]))
        full = [dict(a, system=s) for a in answers for s in ("chatgpt", "gemini", "claude", "perplexity")]
        self.assertEqual(test_matrix_problems(full, cases, ["chatgpt", "gemini", "claude", "perplexity"]), [])

    def test_repeat_subset_is_matched_including_flip_denominator(self):
        items = [dict(task_id=str(i), run_index=1, precision=0 if i < 5 else 1, correct=0) for i in range(10)]
        items += [dict(task_id=str(i), run_index=r, precision=0, correct=1) for i in range(5) for r in (2, 3)]
        values, sd, flips, n = repeat_summary(items)
        self.assertEqual(values, [0, 0, 0])
        self.assertEqual(sd, 0)
        self.assertEqual(flips, 1)
        self.assertEqual(n, 5)

    def test_degenerate_kappa_is_undefined_not_perfect(self):
        self.assertEqual(cohen_kappa(["S2", "S2"], ["S2", "S2"]), (None, 1))
        kappa, agreement = cohen_kappa(["S2", "S0"], ["S0", "S0"])
        self.assertEqual(kappa, 0)
        self.assertEqual(agreement, 0.5)


if __name__ == "__main__":
    unittest.main()

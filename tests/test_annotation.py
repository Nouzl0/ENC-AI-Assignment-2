import json
import random
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_citations import parse_answer, stratified_sample
from common import required_facts, validate_pair_rows
from validate_cases import validate_case


class AnnotationTests(unittest.TestCase):
    def test_more_than_eight_claims_not_truncated(self):
        text = " ".join(f"Fact number {i} is present [1]." for i in range(12)) + "\nSOURCES:\n[1] https://example.org/facts"
        claims, _, _, _ = parse_answer(text)
        self.assertEqual(len(claims), 12)

    def test_answer_only_claim_and_quote_not_hidden(self):
        text = ('ANSWER: Another unsupported factual claim exists.\nCLAIMS:\n'
                'C1: The measured value is 95 percent [1] "Source says 95 percent and an extra fact."\n'
                'SOURCES:\n[1] https://example.org/trial\nCONFIDENCE: high')
        claims, _, _, _ = parse_answer(text)
        self.assertEqual(len(claims), 2)
        self.assertIn("unsupported", claims[0])
        self.assertNotIn("Source says", claims[1])

    def test_exact_repeated_claim_merges_markers_not_new_unit(self):
        claims, _, _, _ = parse_answer('ANSWER: The measured value is 95 percent.\nCLAIMS:\n'
                                       'C1: The measured value is 95 percent [1]\nSOURCES:\n[1] https://example.org/trial')
        self.assertEqual(len(claims), 1)
        self.assertIn("[1]", claims[0])

    def test_multiple_support_quotes_preserve_each_explicit_source(self):
        claims, _, _, _ = parse_answer('CLAIMS:\nC1: The measured value is 95 percent [1] "first evidence" [2] „second evidence“\n'
                                       'SOURCES:\n[1] https://example.org/one\n[2] https://example.org/two')
        self.assertEqual(len(claims), 1)
        self.assertIn("[1]", claims[0])
        self.assertIn("[2]", claims[0])
        self.assertNotIn("evidence", claims[0])

    def test_answer_and_claims_support_quotes_not_extra_claims(self):
        fact = 'The measured value is 95 percent [1] "First evidence sentence. Second evidence sentence."'
        claims, _, _, fmt = parse_answer(f'ANSWER: {fact}\nCLAIMS:\nC1: {fact}\nSOURCES:\n[1] https://example.org/trial')
        self.assertEqual(len(claims), 1)
        self.assertNotIn("evidence", claims[0])
        self.assertTrue(fmt["all_claims_cited"])

    def test_dedup_preserves_semantic_symbols(self):
        for a, b in (("-5 C", "+5 C"), ("5%", "5"), ("1/2", "1:2")):
            claims, _, _, _ = parse_answer(f'The value was {a} [1]. The value was {b} [2].')
            self.assertEqual(len(claims), 2, (a, b))
            self.assertNotIn("[2]", claims[0])

    def test_double_rating_share_rounds_up(self):
        for n in range(1, 41):
            rows = [dict(blind_answer_id=f'A{i}', _system="sys", _condition="P2") for i in range(n)]
            chosen = stratified_sample(rows, .25, random.Random(2026))
            self.assertGreaterEqual(len(chosen) / n, .25)

    def test_split_requires_new_pair_ids(self):
        row = dict(pair_id="A1-T2-1", blind_answer_id="A1", claim_id="T2a", citation_n="1")
        with self.assertRaises(ValueError):
            validate_pair_rows([row], "split")
        validate_pair_rows([dict(row, pair_id="A1-T2a-1")], "split")

    def test_bonus_not_in_required_denominator(self):
        cases = [json.loads(l) for l in (ROOT / "data/cases_dev.jsonl").read_text().splitlines()]
        by_id = {c["task_id"]: c for c in cases}
        self.assertEqual(required_facts(by_id["CIT-007"]), ["12 % od 1. 1. 2024"])
        self.assertFalse(any("NTIA" in f for f in required_facts(by_id["CIT-012"])))
        self.assertEqual(len(required_facts(by_id["CIT-019"])), 1)
        self.assertEqual(validate_case(by_id["CIT-007"], "dev"), [])

    def test_malformed_cases_return_errors_not_tracebacks(self):
        for case in (None, [], {}, {"language": []}, {"reference_answer_or_tests": []}):
            self.assertTrue(validate_case(case, "dev"))


if __name__ == "__main__":
    unittest.main()

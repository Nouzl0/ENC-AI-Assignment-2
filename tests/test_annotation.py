import json
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_citations import clean_text_urls, parse_answer, stratified_sample
from common import required_facts, validate_pair_rows
from validate_cases import validate_case

ROOT = Path(__file__).resolve().parents[1]


class AnnotationTests(unittest.TestCase):
    def test_urls_preserve_markdown_destinations_and_original_response(self):
        urls = [
            "https://example.org/resource_",
            "https://example.org/resource__",
            "https://example.org/path!",
            "https://example.org/x?a=%2f&b=one%20two&utm_id=test&b=second",
            "https://example.org/a_(b)",
            "https://example.org/a(b).pdf",
            "https://example.org/a(b(c)).pdf",
        ]
        for url in urls:
            text = f"ANSWER: The value is [document]({url}).\nSOURCES:\n[1] [document]({url})"
            _, sources, _, _ = parse_answer(text)
            self.assertEqual(sources[1]["url"], url)
            self.assertEqual(clean_text_urls(text), text)
        _, sources, _, _ = parse_answer(
            "The value is supported [1].\nSOURCES:\n[1] https://example.org/resource__"
        )
        self.assertEqual(sources[1]["url"], urls[1])

    def test_zero_marker_is_retained_and_flagged_not_renumbered(self):
        claims, sources, _, fmt = parse_answer(
            "ANSWER: The value is 31 [0].\nSOURCES:\n[0] https://example.org/value"
        )
        self.assertIn("[0]", claims[0])
        self.assertIn(0, sources)
        self.assertFalse(fmt["valid_citation_numbers"])
        validate_pair_rows(
            [
                {
                    "blind_answer_id": "A1",
                    "pair_id": "A1-T1-0",
                    "claim_id": "T1",
                    "citation_n": "0",
                }
            ],
            "zero output",
        )

    def test_bold_heading_with_inline_value_preserves_source_url(self):
        claims, sources, _, _ = parse_answer(
            "**ANSWER:** The value is 31 [1].\n__SOURCES:__\n**[1]** https://example.org/value__"
        )
        self.assertEqual(claims, ["The value is 31 [1]."])
        self.assertEqual(sources[1]["url"], "https://example.org/value__")
        _, sources, _, _ = parse_answer(
            "The value is 31 [1].\nSOURCES:\n__[1]__ https://example.org/value__"
        )
        self.assertEqual(sources[1]["url"], "https://example.org/value__")

    def test_source_line_keeps_primary_url_before_markdown_mirror(self):
        _, sources, _, _ = parse_answer(
            "The value is 31 [1].\nSOURCES:\n[1] https://example.org/primary_ (mirror [copy](https://example.org/secondary_))"
        )
        self.assertEqual(sources[1]["url"], "https://example.org/primary_")

    def test_whole_bold_source_keeps_number_and_url(self):
        for marker in ("**", "__"):
            for url in (
                "https://example.org/resource_",
                "https://example.org/resource__",
            ):
                for source in (f"[2] [source]({url})", f"[2] {url}"):
                    _, sources, _, _ = parse_answer(
                        f"The value is 31 [2].\nSOURCES:\n{marker}{source}{marker}"
                    )
                    self.assertEqual(list(sources), [2])
                    self.assertEqual(sources[2]["url"], url)

    def test_more_than_eight_claims_not_truncated(self):
        text = (
            " ".join(f"Fact number {i} is present [1]." for i in range(12))
            + "\nSOURCES:\n[1] https://example.org/facts"
        )
        claims, _, _, _ = parse_answer(text)
        self.assertEqual(len(claims), 12)

    def test_answer_only_claim_and_quote_not_hidden(self):
        text = (
            "ANSWER: Another unsupported factual claim exists.\nCLAIMS:\n"
            'C1: The measured value is 95 percent [1] "Source says 95 percent and an extra fact."\n'
            "SOURCES:\n[1] https://example.org/trial\nCONFIDENCE: high"
        )
        claims, _, _, _ = parse_answer(text)
        self.assertEqual(len(claims), 2)
        self.assertIn("unsupported", claims[0])
        self.assertNotIn("Source says", claims[1])

    def test_exact_repeated_claim_merges_markers_not_new_unit(self):
        claims, _, _, _ = parse_answer(
            "ANSWER: The measured value is 95 percent.\nCLAIMS:\n"
            "C1: The measured value is 95 percent [1]\nSOURCES:\n[1] https://example.org/trial"
        )
        self.assertEqual(len(claims), 1)
        self.assertIn("[1]", claims[0])

    def test_multiple_support_quotes_preserve_each_explicit_source(self):
        claims, _, _, _ = parse_answer(
            'CLAIMS:\nC1: The measured value is 95 percent [1] "first evidence" [2] „second evidence“\n'
            "SOURCES:\n[1] https://example.org/one\n[2] https://example.org/two"
        )
        self.assertEqual(len(claims), 1)
        self.assertIn("[1]", claims[0])
        self.assertIn("[2]", claims[0])
        self.assertNotIn("evidence", claims[0])

    def test_answer_and_claims_support_quotes_not_extra_claims(self):
        fact = 'The measured value is 95 percent [1] "First evidence sentence. Second evidence sentence."'
        claims, _, _, fmt = parse_answer(
            f"ANSWER: {fact}\nCLAIMS:\nC1: {fact}\nSOURCES:\n[1] https://example.org/trial"
        )
        self.assertEqual(len(claims), 1)
        self.assertNotIn("evidence", claims[0])
        self.assertTrue(fmt["all_claims_cited"])

    def test_dedup_preserves_semantic_symbols(self):
        for a, b in (("-5 C", "+5 C"), ("5%", "5"), ("1/2", "1:2")):
            claims, _, _, _ = parse_answer(
                f"The value was {a} [1]. The value was {b} [2]."
            )
            self.assertEqual(len(claims), 2, (a, b))
            self.assertNotIn("[2]", claims[0])

    def test_double_rating_share_rounds_up(self):
        for n in range(1, 41):
            rows = [
                {
                    "blind_answer_id": f"A{i}",
                    "_phase": "dev",
                    "_system": "sys",
                    "_condition": "P2",
                }
                for i in range(n)
            ]
            chosen = stratified_sample(rows, 0.25, random.Random(2026))
            self.assertGreaterEqual(len(chosen) / n, 0.25)

    def test_combined_export_samples_each_phase_separately(self):
        rows = [
            {
                "blind_answer_id": f"A{phase}{i}",
                "_phase": phase,
                "_system": "sys",
                "_condition": "P2",
            }
            for phase, n in (("dev", 20), ("val", 10), ("test", 10), ("repeat", 20))
            for i in range(n)
        ]
        chosen = stratified_sample(rows, 0.25, random.Random(2026))
        self.assertEqual(len(chosen), 16)
        for phase in ("dev", "val", "test", "repeat"):
            ids = {r["blind_answer_id"] for r in rows if r["_phase"] == phase}
            self.assertGreaterEqual(len(chosen & ids) / len(ids), 0.25)

    def test_split_requires_new_pair_ids(self):
        row = {
            "pair_id": "A1-T2-1",
            "blind_answer_id": "A1",
            "claim_id": "T2a",
            "citation_n": "1",
        }
        with self.assertRaises(ValueError):
            validate_pair_rows([row], "split")
        validate_pair_rows([dict(row, pair_id="A1-T2a-1")], "split")

    def test_bonus_not_in_required_denominator(self):
        cases = [
            json.loads(line)
            for line in (ROOT / "data/cases_dev.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
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

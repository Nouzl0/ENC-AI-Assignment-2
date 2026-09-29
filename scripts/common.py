"""Shared helpers for the CZAI citation benchmark scripts (standard library only)."""
import csv
import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PROMPTS = os.path.join(ROOT, "prompts")

SYSTEMS = ["chatgpt", "gemini", "claude", "perplexity", "grok"]

INTERFACE = {
    "chatgpt": "chatgpt.com (web)",
    "gemini": "gemini.google.com (web)",
    "claude": "claude.ai (web)",
    "perplexity": "perplexity.ai (web)",
    "grok": "grok.com (web)",
}
TOOL_PERMISSIONS = {
    "chatgpt": "Search vynucen; Deep research vypnut; Temporary chat (Unpersonalized)",
    "gemini": "vyhledávání automatické; Deep Research vypnut; Temporary chat",
    "claude": "Web search zapnut/automatický; Research vypnut; Incognito chat",
    "perplexity": "režim Search; Research/Labs vypnuto; Incognito",
    "grok": "vyhledávání automatické (web + X); DeepSearch vypnut; Private Chat",
}

# phase -> (split, conditions, run indices)
PHASES = {
    "dev": ("dev", ["P2"], [1]),
    "val": ("val", ["P2", "P3A", "P3B"], [1]),
    "test": ("test", ["P1", "P2", "P3"], [1]),
    "repeat": ("test", ["P2"], [2, 3]),
}

PROMPT_FILES = {
    "P1": "P1_baseline_{lang}.txt",
    "P2": "P2_structured_{lang}.txt",
    "P3A": "P3A_candidate_{lang}.txt",
    "P3B": "P3B_candidate_{lang}.txt",
    "P3": "P3_final_{lang}.txt",
}

EDGE_TYPES = {"none", "false_premise", "conflicting_evidence", "missing_info", "ambiguous",
              "time_constraint", "recent_change", "cz_en_mix"}
RATINGS = {"S2", "S1", "S0", "NA", "FAB"}

META_FILL_COLUMNS = [
    "model_visible", "plan_tier", "datetime_start", "datetime_end", "latency_s",
    "search_used", "n_sources_shown", "turns", "tool_calls_visible", "retries",
    "failure_type", "first_attempt_ok", "manual_intervention", "share_link",
    "screenshot_file", "operator", "cost_note", "notes",
]
FAILURE_TYPES = {"", "none", "model_output", "invalid_format", "tool_error", "rate_limit",
                 "timeout", "product_outage", "student_error", "student_error_rerun", "evaluation_error"}


def prompt_lang(case_language):
    """Czech prompt for 'cs' and mixed 'cs+en' cases, English prompt for 'en'."""
    return "en" if case_language == "en" else "cs"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cases(split, data_dir=DATA):
    path = os.path.join(data_dir, f"cases_{split}.jsonl")
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_all_cases(data_dir=DATA):
    out = {}
    for split in ("dev", "val", "test"):
        p = os.path.join(data_dir, f"cases_{split}.jsonl")
        if os.path.exists(p):
            for c in load_cases(split, data_dir):
                out[c["task_id"]] = c
    return out


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_csv_glob(pattern):
    rows = []
    for p in sorted(glob.glob(pattern)):
        rows.extend(read_csv(p))
    return rows


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

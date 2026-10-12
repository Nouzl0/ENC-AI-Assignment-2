#!/usr/bin/env python3
"""Parse recorded answers, run automated citation checks and build the blinded
annotation sheets for human raters.

Input: filled private run plans and recorded answer/artifact files outside Git.
The parser accepts P2/P3 output as produced and common P1 formats: inline [n] markers,
superscripts (¹²), markdown links [text](url), bold/markdown headings, bulleted or
numbered source lists and bare URL lists (see runs/README.md).

Output for raters (--out-dir, e.g. "$WORK/annotation/dev"):
    answers_to_rate.csv, pairs_to_rate.csv                 rater 1 (all answers)
    answers_to_rate_rater2.csv, pairs_to_rate_rater2.csv   rater 2 (25 % stratified subset)
Output for the data steward only (--key-dir, e.g. "$WORK/key"):
    blind_key.csv      blind_answer_id -> run_id
    answers_meta.csv   format validity etc. (kept out of the raters' sheets)
    pairs_auto_checks.csv  automated hints; neither independent rater receives them
    salt.txt           random salt for the blind IDs (created on first run, reused afterwards)

Production requires the plan's G1/G2, private output/key directories and original
artifacts. Keys accumulate; exports cannot overwrite prior sheets or repeat run IDs.
Usage (see HANDOFF.md for human rating/evidence steps):
    python3 scripts/check_citations.py --freeze "$WORK/G1.json" --runs "$WORK/runs/run_plan_dev.csv" --out-dir "$WORK/annotation/dev" --key-dir "$WORK/key"
--offline skips HTTP (not a completed automated content check). --pilot and
--synthetic are explicit calibration/test modes, never confirmatory experiments.
"""

import argparse
import collections
import csv
import datetime as dt
import hashlib
import html
import math
import os
import random
import re
import secrets
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    ROOT,
    load_all_cases,
    read_csv,
    read_csv_glob,
    required_facts,
    run_problems,
    sha256_file,
    unique_index,
    write_csv,
)
from integrity import (
    private_path,
    run_artifact_problems,
    verify_freeze,
    verify_plans,
    write_json_new,
)

STRUCTURED = {"P2", "P3", "P3A", "P3B"}
UA = "Mozilla/5.0 (X11; Linux x86_64) CZAI-citation-benchmark/1.0 (student project)"

URL_RE = re.compile(r"https?://[^\s<>\"'\]\[]+")
MD_START_RE = re.compile(r"\[([^\]\n]{1,200})\]\((https?://)")
MARK_RE = re.compile(r"\[(\d+(?:\s*[,;–-]\s*\d+)*)\]")
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
SUP_RUN_RE = re.compile(r"([⁰¹²³⁴⁵⁶⁷⁸⁹]+(?:\s*,\s*[⁰¹²³⁴⁵⁶⁷⁸⁹]+)*)")
HEADINGS = {
    "answer": r"ODPOVĚĎ|ODPOVED|ANSWER|SHRNUTÍ|SUMMARY",
    "claims": r"TVRZENÍ|TVRZENI|CLAIMS",
    "sources": r"ZDROJE|SOURCES|POUŽITÉ ZDROJE|REFERENCES|REFERENCE|CITATIONS|CITACE|ODKAZY",
    "confidence": r"JISTOTA|CONFIDENCE",
}
HEAD_RE = {
    k: re.compile(rf"^(?:{v})\s*(?::\s*(.*))?$", re.I) for k, v in HEADINGS.items()
}
CLAIM_LABEL_RE = re.compile(r"^[TC]\d+\s*[:.)]\s*(.+)$")
SRC_NUM_RE = re.compile(
    r"^(?:\[(\d+)\]:?|\[(\d+)\]\(|(\d+)[.):]\s|\^(\d+)\^?:?|([⁰¹²³⁴⁵⁶⁷⁸⁹]+))\s*(.*)$"
)
ABBR = {
    "č",
    "čl",
    "odst",
    "písm",
    "sb",
    "tj",
    "např",
    "mj",
    "resp",
    "atd",
    "tzv",
    "st",
    "stol",
    "r",
    "mil",
    "mld",
    "tis",
    "s",
    "n",
    "m",
    "dr",
    "ing",
    "mgr",
    "prof",
    "doc",
    "vs",
    "apod",
    "aj",
    "př",
    "kap",
    "str",
    "obr",
    "tab",
    "e.g",
    "i.e",
    "etc",
    "mr",
    "mrs",
    "ms",
    "no",
    "vol",
    "pp",
    "fig",
    "jr",
    "sr",
    "inc",
    "ltd",
    "co",
    "cca",
    "min",
    "max",
    "kč",
    "hod",
    "tel",
    "ul",
    "nám",
}
ROMAN_RE = re.compile(r"^[IVXLCDM]+$")


# ----------------------------------------------------------------- text helpers
def clean_url(url, markdown=False):
    """Extract a URL, not a canonicalized replacement of the recorded address.

    Markdown destinations are exact; bare links may carry sentence punctuation.
    In particular trailing underscores and query ordering/encoding are meaningful.
    """
    if markdown:
        return url
    url = url.rstrip(".,;:!?")
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url


def markdown_links(text):
    """Markdown links with balanced URL parentheses (including nested paths)."""
    end_previous = 0
    for m in MD_START_RE.finditer(text):
        if m.start() < end_previous:
            continue
        depth, end = 1, m.start(2)
        while end < len(text) and not text[end].isspace():
            if text[end] == "(":
                depth += 1
            elif text[end] == ")":
                depth -= 1
                if depth == 0:
                    end_previous = end + 1
                    yield (
                        m.start(),
                        end + 1,
                        m.group(1),
                        text[m.start(2) : end],
                        m.start(2),
                    )
                    break
            end += 1


def replace_markdown_links(text, replace):
    chunks, previous = [], 0
    for start, end, label, url, _ in markdown_links(text):
        chunks.extend((text[previous:start], replace(label, url)))
        previous = end
    return "".join(chunks) + text[previous:]


def strip_md(line):
    """Remove markdown decoration used for headings and lists."""
    s = line.strip()
    s = re.sub(r"^>+\s*", "", s)
    s = re.sub(r"^#{1,6}\s*", "", s)
    s = re.sub(r"^[-*+•]\s+", "", s)
    # Only unwrap whole-line decoration: global replacements corrupt URL paths.
    for marker in ("**", "__"):
        if s.startswith(marker):
            end = s.find(marker, len(marker))
            destinations = [
                (start, stop - 1) for _, stop, _, _, start in markdown_links(s)
            ]
            while end >= 0 and any(start <= end < stop for start, stop in destinations):
                end = s.find(marker, end + len(marker))
            if end >= 0 and not s[end:].strip(marker[0]):
                s = s[len(marker) : -len(marker)]
                continue
            label = s[len(marker) : end].strip() if end >= 0 else ""
            if label and (
                any(rx.match(label) for rx in HEAD_RE.values())
                or re.fullmatch(r"\[\d+\]", label)
            ):
                s = label + s[end + len(marker) :]
    return s.strip()


def parse_markers(text):
    nums = []
    for m in MARK_RE.finditer(text):
        for part in re.split(r"\s*[,;]\s*", m.group(1)):
            if re.match(r"^\d+\s*[–-]\s*\d+$", part):
                a, b = [int(x) for x in re.split(r"\s*[–-]\s*", part)]
                nums.extend(range(a, b + 1) if 0 < b - a < 10 else [a, b])
            elif part.strip().isdigit():
                nums.append(int(part))
    out = []
    for n in nums:
        if n not in out:
            out.append(n)
    return out


def sup_to_markers(text, known):
    def repl(m):
        out = []
        for p in [p.strip().translate(SUP) for p in m.group(1).split(",")]:
            if p.isdigit() and (int(p) in known or len(p) == 1):
                out.append(int(p))
            else:
                out.extend(int(ch) for ch in p)
        return "".join(f"[{n}]" for n in out)

    return SUP_RUN_RE.sub(repl, text)


def split_sentences(text):
    """Sentence split that respects Czech/English abbreviations, ordinals and dates."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    out, start = [], 0
    rx = r"[.!?](?:[\"“”»)]*)((?:\s*\[\d+(?:\s*[,;–-]\s*\d+)*\])*)\s+(?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ„\"“(])"
    for m in re.finditer(rx, text):
        before = text[start : m.start()]
        last = re.findall(r"[\w.]+$", before)
        tok = last[0].split(".")[-1] if last else ""
        ordinal = tok.isdigit() and len(tok) <= 2  # "1. 7. 2024", "19. století"
        if (
            text[m.start()] == "."
            and not m.group(1)
            and (
                tok.lower() in ABBR
                or ordinal
                or ROMAN_RE.match(tok)
                or (len(tok) == 1 and tok.isalpha())
            )
        ):
            continue
        end = m.end(1) if m.group(1) else m.start() + 1
        out.append(text[start:end].strip())
        start = m.end()
    out.append(text[start:].strip())
    return [s for s in out if s]


def strip_support_quotes(text):
    """Remove P3 evidence quotations, not the original recorded answer."""
    return re.sub(r'(\[[\d\s,;–-]+\])\s*(?:"[^"]*"|„[^“]*“|“[^”]*”)', r"\1", text)


# ----------------------------------------------------------------- parsing
def parse_answer(text):
    lines = text.splitlines()
    sections = collections.OrderedDict(body=[])
    current = "body"
    for raw in lines:
        s = strip_md(raw)
        matched, m = None, None
        for name, rx in HEAD_RE.items():
            m = rx.match(s)
            if m:
                matched = name
                break
        if matched:
            current = matched
            sections.setdefault(current, [])
            if m.group(1):
                sections[current].append(m.group(1))
        else:
            sections.setdefault(current, []).append(raw)

    # ---- sources
    sources, next_n = {}, 1
    src_lines = sections.get("sources", [])
    if not src_lines:  # fallback: numbered '[n] ... URL' lines anywhere
        src_lines = [
            line
            for line in lines
            if re.match(r"^\s*(?:[-*+•]\s*)?\[\d+\]", line) and URL_RE.search(line)
        ]
        for line in src_lines:
            for name in ("body", "answer"):
                if line in sections.get(name, []):
                    sections[name].remove(line)
    for line in src_lines:
        s = strip_md(line)
        if not s:
            continue
        m = SRC_NUM_RE.match(s)
        num, rest = None, s
        if m:
            g = [x for x in m.groups()[:5] if x]
            if g:
                num = int(g[0].translate(SUP))
            rest = m.group(6) if m.group(6) is not None else s
            if m.group(2):  # [1](url) form: the '(' was consumed
                rest = "(" + rest
        url_m = URL_RE.search(rest)
        if not url_m:
            continue
        if num is None:
            while next_n in sources:
                next_n += 1
            num = next_n
        next_n = max(next_n, num + 1)
        first_url = URL_RE.search(s)
        md_url = next(
            (
                url
                for _, _, _, url, start in markdown_links(s)
                if first_url and start == first_url.start()
            ),
            None,
        )
        sources[num] = {
            "line": re.sub(r"\s+", " ", rest).strip()[:300],
            "url": md_url if md_url is not None else clean_url(url_m.group(0)),
        }

    body_lines = sections.get("body", []) + sections.get("answer", [])
    claim_lines = sections.get("claims", [])

    def add_source(url, label):
        for n, src in sources.items():
            if src["url"] == url:
                return n
        n = max(sources) + 1 if sources else 1
        sources[n] = {"line": label[:300], "url": url}
        return n

    # inline markdown links and bare URLs in the text -> [n] markers
    def link_repl(label, url):
        return f"{label} [{add_source(url, label)}]"

    def bare_repl(m):
        url = clean_url(m.group(0))
        return f"[{add_source(url, url)}]"

    body_lines = [
        URL_RE.sub(bare_repl, replace_markdown_links(line, link_repl))
        for line in body_lines
    ]
    claim_lines = [
        URL_RE.sub(bare_repl, replace_markdown_links(line, link_repl))
        for line in claim_lines
    ]
    known = set(sources)
    body_lines = [sup_to_markers(line, known) for line in body_lines]
    claim_lines = [sup_to_markers(line, known) for line in claim_lines]

    # ---- claims
    listed, segmentation = [], "system"
    for line in claim_lines:
        s = re.sub(r"^\d+[.)]\s+", "", strip_md(line))
        if not s:
            continue
        m = CLAIM_LABEL_RE.match(s)
        # P3 support quotations are evidence, not an extra generated factual claim.
        claim = (m.group(1) if m else s).strip()
        claim = strip_support_quotes(claim)
        listed.append(claim)
    if not listed:
        segmentation = "auto_sentence"
    elif body_lines:
        segmentation = "mixed_review"
    paragraph = strip_support_quotes(" ".join(strip_md(line) for line in body_lines))
    candidates = split_sentences(paragraph) + listed
    claims, seen = [], {}
    for claim in candidates:
        # Only whitespace, citation markers and terminal sentence punctuation
        # differ automatically. Signs, units and internal punctuation are semantic.
        key = (
            re.sub(r"\s+", " ", MARK_RE.sub("", claim))
            .strip()
            .rstrip(".!?")
            .strip()
            .casefold()
        )
        if not key:
            continue
        if key in seen:
            i = seen[key]
            old_marks = set(parse_markers(claims[i]))
            new = [n for n in parse_markers(claim) if n not in old_marks]
            claims[i] += "".join(f" [{n}]" for n in new)
        else:
            seen[key] = len(claims)
            claims.append(claim)

    fmt = {
        "has_answer": bool(sections.get("answer")),
        "has_claims": bool(sections.get("claims")),
        "has_sources": bool(sections.get("sources")),
        "has_confidence": bool(sections.get("confidence")),
    }
    marks = [n for c in claims for n in parse_markers(c)]
    fmt["all_claims_cited"] = bool(claims) and all(parse_markers(c) for c in claims)
    fmt["all_marks_resolved"] = all(n in sources for n in marks)
    fmt["valid_citation_numbers"] = all(n >= 1 for n in marks) and all(
        n >= 1 for n in sources
    )
    return claims, sources, segmentation, fmt


def clean_text_urls(text):
    # Raters must see the original response, not rewritten URLs.
    return text


# ----------------------------------------------------------------- web checks
def strip_html(raw):
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw))


def published_date(raw):
    pats = [
        r'property=["\']article:published_time["\'][^>]*content=["\']([^"\']+)',
        r'content=["\']([^"\']+)["\'][^>]*property=["\']article:published_time',
        r'"datePublished"\s*:\s*"([^"]+)"',
        r'name=["\'](?:date|dc\.date|citation_publication_date|DC\.date\.issued)["\'][^>]*content=["\']([^"\']+)',
    ]
    for p in pats:
        m = re.search(p, raw, re.I)
        if m:
            return m.group(1)[:25]
    return ""


def iri_to_uri(url):
    p = urllib.parse.urlsplit(url)
    try:
        host = p.hostname.encode("idna").decode("ascii") if p.hostname else ""
    except UnicodeError:
        host = p.hostname or ""
    netloc = host + (f":{p.port}" if p.port else "")
    safe = "/%:@!$&'()*+,;=~-._"
    return urllib.parse.urlunsplit(
        (
            p.scheme,
            netloc,
            urllib.parse.quote(p.path, safe=safe),
            urllib.parse.quote(p.query, safe=safe + "?"),
            urllib.parse.quote(p.fragment, safe=safe),
        )
    )


def fetch(url, timeout):
    empty = {
        "status": 0,
        "final_url": url,
        "ctype": "",
        "text": "",
        "published": "",
        "error": "",
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "body": b"",
        "truncated": False,
    }
    try:
        req = urllib.request.Request(
            iri_to_uri(url),
            headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            ctype = r.headers.get("Content-Type", "")
            body = r.read(3_000_001)
            truncated = len(body) > 3_000_000
            body = body[:3_000_000]
            charset = r.headers.get_content_charset() or "utf-8"
            try:
                raw = body.decode(charset, errors="replace")
            except LookupError:
                raw = body.decode("utf-8", errors="replace")
            text = (
                strip_html(raw)
                if "html" in ctype
                else (raw if ("text" in ctype or "json" in ctype) else "")
            )
            return {
                **empty,
                "status": r.status,
                "final_url": r.geturl(),
                "ctype": ctype,
                "text": text,
                "body": body,
                "truncated": truncated,
                "published": published_date(raw) if "html" in ctype else "",
                "error": "",
            }
    except urllib.error.HTTPError as e:
        try:
            body = e.read(3_000_001)
        except Exception:
            body = b""
        finally:
            e.close()
        return {
            **empty,
            "status": e.code,
            "final_url": e.geturl(),
            "error": f"HTTP {e.code}",
            "body": body[:3_000_000],
            "truncated": len(body) > 3_000_000,
        }
    except (
        Exception
    ) as e:  # network errors, bad URLs, http.client errors: never crash the batch
        return {
            **empty,
            "error": f"{type(e).__name__}: {str(getattr(e, 'reason', e))[:120]}",
        }


def is_generic(url):
    try:
        p = urllib.parse.urlparse(url)
    except ValueError:
        return True
    path = p.path.rstrip("/")
    return path == "" or (
        "search" in path.lower() and ("q=" in p.query or "query=" in p.query)
    )


def suggestion(res):
    if res is None:
        return ""
    st, err = res["status"], res["error"]
    if st in (404, 410) or (
        st == 0
        and any(
            k in err
            for k in ("Name or service", "nodename", "getaddrinfo", "No address")
        )
    ):
        return "FAB? (ověřit ručně, i v archivu)"
    if st in (401, 402, 403, 451):
        return "NA? (přístup odepřen / paywall – ověřit v prohlížeči)"
    if st == 0:
        return "NA? (síťová chyba – ověřit v prohlížeči)"
    if st >= 500:
        return "NA? (chyba serveru)"
    return ""


def save_source_check(directory, url, result, attempt):
    """Preserve each HTTP attempt, including error logs; never imply full support."""
    stem = hashlib.sha256(url.encode()).hexdigest() + f"-attempt{attempt}"
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, stem + ".snapshot")
    payload = result.pop("body", b"")
    if not payload:
        payload = (result.get("error", "empty response") + "\n").encode()
    with open(path, "xb") as f:
        f.write(payload)
    result["snapshot_file"] = path
    result["snapshot_sha256"] = sha256_file(path)
    write_json_new(
        os.path.join(directory, stem + ".json"),
        dict({k: v for k, v in result.items() if k != "text"}, requested_url=url),
    )


# ----------------------------------------------------------------- entity match
STOP = {
    "the",
    "and",
    "this",
    "that",
    "with",
    "from",
    "which",
    "podle",
    "který",
    "která",
    "které",
    "jako",
    "roku",
    "byla",
    "bylo",
    "jsou",
    "česká",
    "české",
    "český",
}


def norm_forms(text):
    """Two normalisations: decimal comma -> dot, and thousands separators removed."""
    t = (
        unicodedata.normalize("NFKC", text)
        .lower()
        .replace("\u00a0", " ")
        .replace("\u202f", " ")
    )
    t = re.sub(r"(?<=\d) (?=\d{3}\b)", "", t)  # 12 345 678 -> 12345678
    a = re.sub(r"(?<=\d),(?=\d)", ".", t)  # 12,5 -> 12.5 (Czech decimal comma)
    b = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)  # 2,500 -> 2500 (English thousands)
    return a, b


def number_variants(token):
    """'12 345 678' -> {'12345678'}; '12,5' -> {'12.5'}; '2,500' -> {'2.500', '2500'}."""
    t = re.sub(r"[ \u00a0\u202f]", "", token)
    out = {t.replace(",", ".")}
    if re.fullmatch(r"\d{1,3}(,\d{3})+", t):
        out.add(t.replace(",", ""))
    return sorted(out)


def entities(claim):
    c = MARK_RE.sub(" ", claim)
    c = re.sub(
        r"[„“\"”\u2018\u2019«»].*?[“”\"\u2019»]", " ", c
    )  # ignore quoted snippets (P3)
    c = unicodedata.normalize("NFKC", c)
    nums = [
        number_variants(t)
        for t in re.findall(r"\d+(?:[ \u00a0\u202f]\d{3})*(?:[.,]\d+)*", c)
    ]
    nums = [list(v) for v in {tuple(v) for v in nums}]
    first = re.match(r"\s*(\w+)", c)
    first = first.group(1) if first else ""
    words = set()
    for w in re.findall(
        r"\b[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\wÁČĎÉĚÍŇÓŘŠŤÚŮÝŽáčďéěíňóřšťúůýž\-]{3,}", c
    ):
        if w.lower() not in STOP and w != first:
            words.add(w.lower())
    return sorted(nums), sorted(words)


def match_ratio(nums, words, page_text):
    if not (nums or words) or not page_text:
        return ""
    forms = norm_forms(page_text)
    found = 0
    for variants in nums:
        found += any(
            re.search(rf"(?<![\d.]){re.escape(v)}(?![\d])", f)
            for v in variants
            for f in forms
        )
    for w in words:
        found += any(w in f for f in forms)
    return f"{found / (len(nums) + len(words)):.2f}"


# ----------------------------------------------------------------- main
def stratified_sample(answer_rows, share, rng):
    groups = collections.defaultdict(list)
    for a in answer_rows:
        groups[(a["_phase"], a["_system"], a["_condition"])].append(
            a["blind_answer_id"]
        )
    chosen = set()
    for key in sorted(groups):
        ids = sorted(groups[key])
        k = max(1, math.ceil(len(ids) * share))
        chosen.update(rng.sample(ids, min(k, len(ids))))
    return chosen


def merge_steward_file(path, rows, fields, replaced_ids):
    old = []
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig", newline="") as f:
            old = [
                x for x in csv.DictReader(f) if x["blind_answer_id"] not in replaced_ids
            ]
    write_csv(path, sorted(old + rows, key=lambda k: k["blind_answer_id"]), fields)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(ROOT, "runs", "run_plan_*.csv"))
    ap.add_argument("--root", default=ROOT, help="base dir for answer_file paths")
    ap.add_argument("--data-dir", default=os.path.join(ROOT, "data"))
    ap.add_argument(
        "--test-file",
        help="private holdout matching the freeze (not opened for dev/val)",
    )
    ap.add_argument("--freeze", help="G1 for dev/val; G2 for test/repeat")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument(
        "--synthetic", action="store_true", help="local DEMO-* fixtures only"
    )
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "annotation"))
    ap.add_argument(
        "--key-dir",
        default=os.path.join(ROOT, "annotation_key"),
        help="data steward only: blind key, salt, answer metadata",
    )
    ap.add_argument("--offline", action="store_true", help="skip HTTP checks")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument(
        "--retry-wait",
        type=float,
        default=600,
        help="seconds before 2nd attempt on failed URLs",
    )
    ap.add_argument("--double-share", type=float, default=0.25)
    ap.add_argument(
        "--seed",
        type=int,
        default=2026,
        help="seed for answer order and rater-2 sample",
    )
    ap.add_argument(
        "--salt",
        default="",
        help="override salt (default: <key-dir>/salt.txt, created if missing)",
    )
    args = ap.parse_args()
    if (
        not 0.25 <= args.double_share <= 1
        or not math.isfinite(args.timeout)
        or args.timeout <= 0
        or not math.isfinite(args.retry_wait)
        or args.retry_wait < 0
    ):
        ap.error(
            "require 0.25 <= --double-share <= 1, finite positive timeout and nonnegative retry wait"
        )
    runs = read_csv_glob(args.runs)
    if not runs:
        raise SystemExit("no run metadata found")
    try:
        if not args.synthetic:
            args.out_dir, args.key_dir = (
                private_path(args.out_dir),
                private_path(args.key_dir),
            )
            if not args.pilot:
                if os.path.realpath(args.data_dir) != os.path.realpath(
                    os.path.join(ROOT, "data")
                ):
                    raise ValueError(
                        "production annotation must use the frozen repository data directory"
                    )
                gate = verify_freeze(
                    args.freeze,
                    "G2" if any(r.get("split") == "test" for r in runs) else "G1",
                )
                if (
                    args.test_file
                    and os.path.realpath(args.test_file) != gate["inputs"]["test_cases"]
                ):
                    raise ValueError("holdout does not match freeze")
                args.test_file = (
                    gate["inputs"]["test_cases"]
                    if any(r.get("split") == "test" for r in runs)
                    else None
                )
        verify_plans(args.runs, args.freeze, args.synthetic, args.pilot)
    except (ValueError, OSError, KeyError) as e:
        raise SystemExit(str(e)) from e
    try:
        unique_index(runs, "run_id", "runs")
    except ValueError as e:
        raise SystemExit(str(e)) from e
    problems, usable = [], []
    for r in runs:
        problems.extend(
            f"{r['run_id']}: {e}"
            for e in (run_problems(r) if args.synthetic else run_artifact_problems(r))
        )
        if r.get("run_status") == "completed":
            path = os.path.join(args.root, r["answer_file"])
            if not os.path.isfile(path) or os.path.getsize(path) == 0:
                problems.append(
                    f"{r['run_id']}: missing/empty completed answer_file {path}"
                )
            else:
                usable.append((r, path))
        if r.get("attempt1_file") and not os.path.isfile(
            os.path.join(args.root, r["attempt1_file"])
        ):
            problems.append(f"{r['run_id']}: missing first-attempt artifact")
    if problems:
        raise SystemExit("Invalid run manifest:\n" + "\n".join(problems))
    for name in (
        "answers_to_rate.csv",
        "pairs_to_rate.csv",
        "answers_to_rate_rater2.csv",
        "pairs_to_rate_rater2.csv",
    ):
        if os.path.exists(os.path.join(args.out_dir, name)):
            raise SystemExit(
                f"Refusing to overwrite annotation sheets in {args.out_dir}; use a new output directory"
            )

    os.makedirs(args.key_dir, exist_ok=True)
    salt_path = os.path.join(args.key_dir, "salt.txt")
    salt = args.salt
    if not salt:
        if os.path.exists(salt_path):
            with open(salt_path, encoding="utf-8") as f:
                salt = f.read().strip()
        else:
            salt = secrets.token_hex(16)
            with open(salt_path, "w", encoding="utf-8") as f:
                f.write(salt + "\n")

    rng = random.Random(args.seed)
    cases = load_all_cases(args.data_dir, args.test_file)
    if args.synthetic and any(
        not r["task_id"].startswith("DEMO-") or not r["system"].startswith("sys_")
        for r in runs
    ):
        raise SystemExit("synthetic mode accepts only anonymous DEMO-* runs")
    print(
        f"{len(runs)} manifest rows, {len(usable)} completed answers; "
        f"{sum(r.get('run_status') == 'failed' for r in runs)} terminal failures retained by score.py"
    )
    if not usable:
        return

    parsed = []
    for r, path in usable:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        claims, sources, seg, fmt = parse_answer(text)
        parsed.append((r, clean_text_urls(text), claims, sources, seg, fmt))

    url_results = {}
    check_dir = os.path.join(
        args.key_dir,
        "source_checks",
        hashlib.sha256(os.path.abspath(args.out_dir).encode()).hexdigest()[:16],
    )
    if not args.offline:
        urls = sorted(
            {
                s["url"]
                for _, _, _, srcs, _, _ in parsed
                for s in srcs.values()
                if s["url"]
            }
        )
        print(f"checking {len(urls)} unique URLs ...")
        for u in urls:
            url_results[u] = fetch(u, args.timeout)
            save_source_check(check_dir, u, url_results[u], 1)
        failed = [
            u
            for u, res in url_results.items()
            if res["status"] in (0, 404, 410) or res["status"] >= 500
        ]
        if failed and args.retry_wait > 0:
            print(
                f"{len(failed)} failed, second attempt in {args.retry_wait:.0f} s ..."
            )
            time.sleep(args.retry_wait)
        for u in failed:
            second = fetch(u, args.timeout)
            save_source_check(check_dir, u, second, 2)
            if second["status"] and second["status"] < 400:
                url_results[u] = second
            else:
                url_results[u]["error"] += " | 2nd attempt failed"

    key_path = os.path.join(args.key_dir, "blind_key.csv")
    old_key = read_csv(key_path) if os.path.exists(key_path) else []
    ids = {
        b: r["run_id"]
        for b, r in unique_index(
            old_key, "blind_answer_id", "existing blind key"
        ).items()
    }
    unique_index(old_key, "run_id", "existing blind key")
    if {r["run_id"] for r in runs} & {r["run_id"] for r in old_key}:
        raise SystemExit(
            "run already exported; preserve original sheets/key and use an audited new workspace version"
        )
    answers_out, pairs_out, key_out, meta_out = [], [], [], []
    for r, text, claims, sources, seg, fmt in parsed:
        bid = "A" + hashlib.sha256(f"{salt}:{r['run_id']}".encode()).hexdigest()[:7]
        if bid in ids and ids[bid] != r["run_id"]:
            raise SystemExit(f"blind ID collision {bid}; delete {salt_path} and rerun")
        ids[bid] = r["run_id"]
        case = cases.get(r["task_id"], {})
        ref = case.get("reference_answer_or_tests", {})
        structured = r["condition"] in STRUCTURED
        fmt_valid = ("yes" if all(fmt.values()) else "no") if structured else ""
        any_marks = any(parse_markers(c) for c in claims)
        answers_out.append(
            {
                "blind_answer_id": bid,
                "task_id": r["task_id"],
                "language": r["language"],
                "question": case.get("user_prompt", ""),
                "reference_answer": ref.get("reference_answer", ""),
                "reference_valid_as_of": case.get("reference_valid_as_of", ""),
                "key_facts": " | ".join(
                    f"RF{i}: {fact}" for i, fact in enumerate(required_facts(case), 1)
                ),
                "optional_facts": " | ".join(ref.get("optional_facts", [])),
                "n_key_facts": len(required_facts(case)),
                "required_constraints": " | ".join(
                    f"RC{i}: {c}"
                    for i, c in enumerate(ref.get("required_constraints", []), 1)
                ),
                "expected_properties": " | ".join(case.get("expected_properties", [])),
                "rater_notes": case.get("rater_notes", ""),
                "answer_text": text.strip(),
                "parsed_sources": "\n".join(
                    f"[{n}] {s['url']}" for n, s in sorted(sources.items())
                ),
                "segmentation": seg,
                "n_claims": len(claims),
                "n_sources": len(sources),
                "segmentation_reviewed": "",
                "correctness": "",
                "key_facts_supported": "",
                "key_fact_evidence": "",
                "constraint_results": "",
                "acknowledges_uncertainty": "",
                "check_minutes": "",
                "rater": "",
                "comment": "",
                "_phase": r["phase"],
                "_system": r["system"],
                "_condition": r["condition"],
            }
        )
        key_out.append({"blind_answer_id": bid, "run_id": r["run_id"]})
        meta_out.append(
            {
                "blind_answer_id": bid,
                "run_id": r["run_id"],
                "format_valid": fmt_valid,
                "segmentation": seg,
                **{k: ("yes" if v else "no") for k, v in fmt.items()},
            }
        )
        edge = case.get("edge_case_type", "")
        for ci, claim in enumerate(claims, 1):
            marks = parse_markers(claim)
            if not marks:
                marks = ["*"] if (sources and not any_marks) else [""]
            for n in marks:
                src = sources.get(n) if isinstance(n, int) else None
                url = src["url"] if src else ""
                res = url_results.get(url) if url else None
                nums, words = entities(claim)
                if isinstance(n, int) and not src:
                    sug = "FAB? (značka [n] bez záznamu ve zdrojích – zkontrolujte parsed_sources a originál)"
                else:
                    sug = suggestion(res) if res else ""
                pairs_out.append(
                    {
                        "pair_id": f"{bid}-T{ci}-{n if n != '' else 'none'}",
                        "blind_answer_id": bid,
                        "claim_id": f"T{ci}",
                        "claim_text": claim,
                        "segmentation": seg,
                        "citation_n": n,
                        "url": url
                        if n != "*"
                        else "(nepřiřazeno – vyberte zdroj z parsed_sources v answers_to_rate)",
                        "source_line": src["line"] if src else "",
                        "auto_http_status": res["status"] if res else "",
                        "auto_final_url": res["final_url"]
                        if res and res["final_url"] != url
                        else "",
                        "auto_error": res["error"] if res else "",
                        "auto_generic_url": ("yes" if is_generic(url) else "")
                        if url
                        else "",
                        "auto_published": res["published"] if res else "",
                        "auto_entities": "; ".join(["/".join(v) for v in nums] + words),
                        "auto_match_ratio": match_ratio(nums, words, res["text"])
                        if res
                        else "",
                        "auto_suggestion": sug,
                        "auto_checked_at": res["checked_at"] if res else "",
                        "auto_snapshot_file": res.get("snapshot_file", "")
                        if res
                        else "",
                        "auto_snapshot_sha256": res.get("snapshot_sha256", "")
                        if res
                        else "",
                        "auto_truncated": ("yes" if res["truncated"] else "no")
                        if res
                        else "",
                        "time_constraint_case": "yes"
                        if edge == "time_constraint"
                        else "",
                        "rater_source_n": "",
                        "rating": "",
                        "source_tier": "",
                        "time_ok": "",
                        "evidence_url": "",
                        "evidence_checked_at": "",
                        "evidence_locator": "",
                        "evidence_excerpt": "",
                        "evidence_snapshot": "",
                        "evidence_sha256": "",
                        "evidence_archive_url": "",
                        "error_code": "",
                        "rater": "",
                        "comment": "",
                    }
                )

    rng.shuffle(answers_out)
    order = {a["blind_answer_id"]: i for i, a in enumerate(answers_out)}
    pairs_out.sort(key=lambda p: (order[p["blind_answer_id"]], p["pair_id"]))

    a_fields = [
        k for k in answers_out[0] if not k.startswith("_") and k != "segmentation"
    ]
    p_fields = (
        [k for k in pairs_out[0] if k != "segmentation" and not k.startswith("auto_")]
        if pairs_out
        else ["pair_id", "blind_answer_id", "claim_id", "citation_n", "rating"]
    )
    os.makedirs(args.out_dir, exist_ok=True)
    write_csv(os.path.join(args.out_dir, "answers_to_rate.csv"), answers_out, a_fields)
    write_csv(os.path.join(args.out_dir, "pairs_to_rate.csv"), pairs_out, p_fields)
    chosen = stratified_sample(answers_out, args.double_share, rng)
    write_csv(
        os.path.join(args.out_dir, "answers_to_rate_rater2.csv"),
        [a for a in answers_out if a["blind_answer_id"] in chosen],
        a_fields,
    )
    write_csv(
        os.path.join(args.out_dir, "pairs_to_rate_rater2.csv"),
        [p for p in pairs_out if p["blind_answer_id"] in chosen],
        p_fields,
    )

    new_ids = {r["blind_answer_id"] for r in key_out}
    merge_steward_file(
        os.path.join(args.key_dir, "blind_key.csv"),
        key_out,
        ["blind_answer_id", "run_id"],
        new_ids,
    )
    merge_steward_file(
        os.path.join(args.key_dir, "answers_meta.csv"),
        meta_out,
        list(meta_out[0]),
        new_ids,
    )
    if pairs_out:
        auto_fields = ["pair_id", "blind_answer_id"] + [
            k for k in pairs_out[0] if k.startswith("auto_")
        ]
        merge_steward_file(
            os.path.join(args.key_dir, "pairs_auto_checks.csv"),
            pairs_out,
            auto_fields,
            new_ids,
        )
    # Original sample and sheets are immutable audit evidence, not rater labels.
    batch = os.path.join(
        args.key_dir,
        "batches",
        hashlib.sha256(os.path.abspath(args.out_dir).encode()).hexdigest()[:16],
        "annotation_batch.json",
    )
    write_json_new(
        batch,
        {
            "rater2_ids": sorted(chosen),
            "answer_ids": sorted(a["blind_answer_id"] for a in answers_out),
            "share": args.double_share,
            "sheets": {
                os.path.join(args.out_dir, n): sha256_file(
                    os.path.join(args.out_dir, n)
                )
                for n in (
                    "answers_to_rate.csv",
                    "pairs_to_rate.csv",
                    "answers_to_rate_rater2.csv",
                    "pairs_to_rate_rater2.csv",
                )
            },
        },
    )

    n_uncited = sum(1 for p in pairs_out if p["citation_n"] == "")
    n_unlinked = sum(1 for p in pairs_out if p["citation_n"] == "*")
    print(
        f"{len(answers_out)} answers, {len(pairs_out)} rows ({n_uncited} uncited claims, "
        f"{n_unlinked} unlinked), {len(chosen)} answers for rater 2 -> {args.out_dir}; key -> {args.key_dir}"
    )


if __name__ == "__main__":
    main()

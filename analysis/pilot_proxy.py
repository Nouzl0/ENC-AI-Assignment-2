"""Descriptive pilot metrics WITHOUT human ratings (standard library only).

Writes results/pilot/pilot_metrics.csv with, per product:
  - latency median / p90 of completed answers (upper bounds, polling included),
  - parser counts (claims and cited pairs per answer, share of uncited claims),
  - a LEXICAL SUPPORT PROXY: share of cited pairs whose fetched page contains the
    claim's key figures (or long content words). This is NOT an S2 rating, does
    not read meaning, and over-estimates support. Unreadable pages (403, JS-only)
    are reported as NA-proxy, never as unsupported.
Run from the repository root:  python3 analysis/pilot_proxy.py [url_cache.json]
HTTP is used only for the URLs already cited in the pilot answers.
"""

import csv
import glob
import html
import json
import re
import statistics as st
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

OUT = Path("results/pilot/pilot_metrics.csv")
CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else None


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def words(s):
    return set(re.findall(r"\w{4,}", s.lower()))


def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research check)"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw, status = r.read(2_000_000).decode("utf-8", "replace"), r.status
        raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S)
        return [status, norm(html.unescape(re.sub(r"<[^>]+>", " ", raw)))[:400000]]
    except Exception as exc:
        return [0, str(exc)[:60]]


def p90(x):
    x = sorted(x)
    k = 0.9 * (len(x) - 1)
    f, c = int(k), min(int(k) + 1, len(x) - 1)
    return x[f] + (x[c] - x[f]) * (k - f)


def main():
    files = {}
    for f in glob.glob("runs/pilot-*/**/*.txt", recursive=True):
        m = re.search(r"dev-(CIT-\d+)-P2-(\w+)-r1\.txt$", f)
        if m and ("/answers/" in f.replace("\\", "/") or "normalization-v2" in f):
            files[(m.group(1), m.group(2))] = words(Path(f).read_text(encoding="utf-8", errors="replace"))
    blind, claims_per = {}, defaultdict(list)
    for f in glob.glob("runs/pilot-*/human-review/answers_to_rate.csv"):
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            w = words(r["answer_text"])
            best = max(((len(w & v) / max(1, len(w | v)), k[1]) for k, v in files.items() if k[0] == r["task_id"]))
            blind[r["blind_answer_id"]] = best[1]
            claims_per[best[1]].append(int(r["n_claims"]))
    pairs = []
    for f in glob.glob("runs/pilot-*/human-review/pairs_to_rate.csv"):
        pairs += list(csv.DictReader(open(f, encoding="utf-8-sig")))
    cache = json.loads(CACHE.read_text()) if CACHE and CACHE.exists() else {}
    for u in sorted({p["url"] for p in pairs if p["url"]} - set(cache)):
        cache[u] = fetch(u)
    if CACHE:
        CACHE.write_text(json.dumps(cache))
    lat = defaultdict(list)
    for r in csv.DictReader(open("results/pilot/run_summary.csv", encoding="utf-8")):
        if r["run_status"] == "completed" and r["collection"] != "legacy" and r["observed_interval_s"]:
            lat[r["system"]].append(float(r["observed_interval_s"]))
    agg = defaultdict(lambda: defaultdict(int))
    for p in pairs:
        s = blind[p["blind_answer_id"]]
        if not p["url"]:
            agg[s]["uncited"] += 1
            continue
        status, text = cache[p["url"]]
        if status != 200 or len(text) < 800:
            agg[s]["na"] += 1
            continue
        t = text.lower()
        tn = re.sub(r"[\s .,]", "", t)
        nums = [re.sub(r"[\s .,]", "", n) for n in re.findall(r"\d[\d\s .,]*\d|\d", p["claim_text"])]
        nums = [n for n in nums if len(n) >= 2]
        ws = re.findall(r"\w{7,}", p["claim_text"].lower())
        if nums:
            frac = sum(n in tn for n in nums) / len(nums)
        elif ws:
            frac = sum(w in t for w in ws) / len(ws)
        else:
            agg[s]["na"] += 1
            continue
        agg[s]["supported" if frac >= 0.6 else "unsupported"] += 1
    cols = ["system", "answers", "latency_median_s_upper_bound", "latency_p90_s_upper_bound",
            "claims_per_answer_parser", "cited_pairs", "uncited_claim_rows", "proxy_supported",
            "proxy_unsupported", "proxy_unreadable", "proxy_support_share_all_cited", "proxy_support_share_readable"]
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for s in sorted(agg):
            d = agg[s]
            cited = d["supported"] + d["unsupported"] + d["na"]
            readable = d["supported"] + d["unsupported"]
            L = lat.get(s, [])
            w.writerow([s, len(claims_per[s]), round(st.median(L), 1) if L else "", round(p90(L), 1) if L else "",
                        round(st.mean(claims_per[s]), 2), cited, d["uncited"], d["supported"], d["unsupported"], d["na"],
                        round(d["supported"] / cited, 2), round(d["supported"] / readable, 2) if readable else ""])
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

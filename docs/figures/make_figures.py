"""Generate the report figures (SVG) from results/pilot/operational_summary.csv.

Standard library only. Run from the repository root:
    python3 docs/figures/make_figures.py
"""

import csv
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FONT = "font-family='Helvetica, Arial, sans-serif'"
INK, MUTED, BG = "#1f2937", "#6b7280", "#ffffff"
BLUE, RED, GREY = "#1d4ed8", "#b91c1c", "#9ca3af"
LABELS = OrderedDict(
    chatgpt="ChatGPT", gemini="Gemini", claude="Claude", perplexity="Perplexity", grok="Grok"
)


def svg(width, height, body, title):
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width} {height}' "
        f"width='{width}' height='{height}' role='img' aria-label='{title}'>"
        f"<rect width='{width}' height='{height}' fill='{BG}'/>{body}</svg>\n"
    )


def text(x, y, s, size=13, fill=INK, anchor="start", weight="normal"):
    return (
        f"<text x='{x}' y='{y}' {FONT} font-size='{size}' fill='{fill}' "
        f"text-anchor='{anchor}' font-weight='{weight}'>{s}</text>"
    )


def box(x, y, w, h, label, sub="", fill="#eff6ff", stroke=BLUE):
    body = f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='8' fill='{fill}' stroke='{stroke}'/>"
    body += text(x + w / 2, y + h / 2 - (4 if sub else -5), label, 14, INK, "middle", "bold")
    if sub:
        body += text(x + w / 2, y + h / 2 + 14, sub, 10.5, MUTED, "middle")
    return body


def arrow(x1, y, x2):
    return (
        f"<line x1='{x1}' y1='{y}' x2='{x2 - 6}' y2='{y}' stroke='{MUTED}' stroke-width='2'/>"
        f"<polygon points='{x2},{y} {x2 - 8},{y - 5} {x2 - 8},{y + 5}' fill='{MUTED}'/>"
    )


def outcomes():
    counts = {k: [0, 0, 0] for k in LABELS}
    with open(ROOT / "results/pilot/operational_summary.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            c = counts[row["system"]]
            c[0] += int(row["completed_answers"])
            c[1] += int(row["failed_first_attempts"])
            c[2] += int(row["planned_not_sent"])
    return counts


def fig_outcomes():
    counts = outcomes()
    w, h, left, bar = 640, 300, 120, 26
    scale = 38
    body = text(left, 28, "Výsledek odeslaných a plánovaných řádků pilotu podle produktu", 14, INK, weight="bold")
    for i, (key, name) in enumerate(LABELS.items()):
        y = 55 + i * 42
        done, failed, unsent = counts[key]
        body += text(left - 10, y + 18, name, 13, INK, "end")
        x = left
        for n, color in ((done, BLUE), (failed, RED), (unsent, GREY)):
            if n:
                body += f"<rect x='{x}' y='{y}' width='{n * scale}' height='{bar}' fill='{color}'/>"
                body += text(x + n * scale / 2, y + 18, n, 12, "#ffffff", "middle", "bold")
                x += n * scale
    ly = 275
    for j, (color, lab) in enumerate(((BLUE, "dokončená odpověď"), (RED, "selhání prvního pokusu"), (GREY, "neodesláno (limit)"))):
        lx = left + j * 175
        body += f"<rect x='{lx}' y='{ly - 11}' width='12' height='12' fill='{color}'/>"
        body += text(lx + 18, ly, lab, 12, MUTED)
    (OUT / "pilot-outcomes.svg").write_text(svg(w, h, body, "Výsledky pilotu podle produktu"), encoding="utf-8")


def fig_design():
    w, h = 800, 230
    body = text(20, 28, "Návrh: produkt × prompt × úloha", 14, INK, weight="bold")
    body += box(20, 55, 230, 70, "5 produktů", "ChatGPT · Gemini · Claude · Perplexity · Grok")
    body += arrow(250, 90, 285)
    body += box(285, 55, 230, 70, "3 prompty", "P1 základní · P2 strukturovaný · P3 optimalizovaný")
    body += arrow(515, 90, 550)
    body += box(550, 55, 230, 70, "40 úloh CZ/EN", "20 dev · 10 val · 10 soukromý test")
    body += text(20, 160, "Jeden nový chat bez paměti na jednu odpověď; P2 na testu 3× opakováno.", 12, MUTED)
    body += text(20, 182, "Produkt = model + vyhledávání + rozhraní. Měříme produkty, ne izolované modely.", 12, MUTED)
    (OUT / "design.svg").write_text(svg(w, h, body, "Návrh experimentu"), encoding="utf-8")


def fig_flow():
    w, h = 760, 190
    body = text(20, 28, "Jak se hodnotí citace", 14, INK, weight="bold")
    xs = [20, 190, 360, 530]
    items = [
        ("Odpověď", "text + URL beze změn"),
        ("Tvrzení ↔ zdroj", "jen explicitní dvojice"),
        ("Dva lidé", "S2 / S1 / S0 / NA / FAB"),
        ("Přesnost", "S2 ÷ všechny dvojice"),
    ]
    for x, (a, b) in zip(xs, items):
        body += box(x, 55, 150, 70, a, b)
    for x in xs[:-1]:
        body += arrow(x + 150, 90, x + 170)
    body += text(20, 160, "NA a FAB zůstávají ve jmenovateli; S2 znamená podporu zdrojem, ne pravdivost odpovědi.", 12, MUTED)
    (OUT / "citation-flow.svg").write_text(svg(w, h, body, "Hodnocení citací"), encoding="utf-8")


def fig_proxy():
    rows = list(csv.DictReader(open(ROOT / "results/pilot/pilot_metrics.csv", encoding="utf-8")))
    w, h, left, scale = 680, 290, 120, 4.6
    body = text(left, 28, "Orientační podpora citací (lexikální proxy, ne lidský rating)", 14, INK, weight="bold")
    for i, r in enumerate(rows):
        y = 55 + i * 46
        cited = int(r["cited_pairs"])
        sup, uns, na = int(r["proxy_supported"]), int(r["proxy_unsupported"]), int(r["proxy_unreadable"])
        body += text(left - 10, y + 18, LABELS[r["system"]], 13, INK, "end")
        x = left
        for n, color in ((sup, BLUE), (uns, RED), (na, GREY)):
            if n:
                body += f"<rect x='{x}' y='{y}' width='{n * scale}' height='26' fill='{color}'/>"
                body += text(x + n * scale / 2, y + 18, n, 12, "#ffffff", "middle", "bold")
                x += n * scale
        body += text(x + 8, y + 18, f"{sup / cited:.2f} z {cited}", 12, MUTED)
    ly = 262
    for j, (color, lab) in enumerate(((BLUE, "nalezeno na stránce"), (RED, "nenalezeno"), (GREY, "stránka nečitelná"))):
        lx = left + j * 170
        body += f"<rect x='{lx}' y='{ly - 11}' width='12' height='12' fill='{color}'/>"
        body += text(lx + 18, ly, lab, 12, MUTED)
    (OUT / "pilot-proxy.svg").write_text(svg(w, h, body, "Orientační podpora citací"), encoding="utf-8")


if __name__ == "__main__":
    fig_outcomes()
    fig_proxy()
    fig_design()
    fig_flow()

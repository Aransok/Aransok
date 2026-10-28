"""Draws the WoW-style legendary item tooltip that heads the profile README.

Live fields, refreshed nightly from the same data as the streak card:
  Item Level  = contributions in the last 365 days
  Durability  = current streak / longest streak

Runs in GitHub Actions with the built-in GITHUB_TOKEN. Pass --demo to render
with made-up data (no network).
"""
import os
import sys
from datetime import date, timedelta
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(__file__))
from streak_card import demo_days, fetch_days, stats  # noqa: E402

OUT = os.environ.get("ITEM_OUT", "profile-3d-contrib/legendary-item.svg")

# WoW tooltip colors
LEGENDARY, YELLOW, GREEN, WHITE, GREY = "#ff8000", "#ffd100", "#1eff00", "#ffffff", "#9d9d9d"

LINES = [
    # (y, color, text, extra attrs)
    (78, YELLOW, "Item Level {ilvl}", ""),
    (100, WHITE, "Binds when hired", ""),
    (122, WHITE, "Unique-Equipped", ""),
    (172, WHITE, "+95 Python", ""),
    (194, WHITE, "+88 Retrieval (Pinecone)", ""),
    (216, WHITE, "+85 Django", ""),
    (246, GREEN, "Equip: Builds AI agents and RAG pipelines from scratch.", ""),
    (268, GREEN, "No LangChain. No CrewAI. Pure Python.", ""),
    (292, GREEN, "Use: Ships to production. broffice.bg is live. (1 day cooldown)", ""),
    (322, YELLOW, "“Forged in Plovdiv, the city of seven hills.”", ' font-style="italic"'),
]


def render(days):
    _, _, cur, longest = stats(days)
    cutoff = date.today() - timedelta(days=365)
    ilvl = sum(n for d, n in days if d > cutoff)
    cur_n, long_n = cur[0], max(longest[0], cur[0], 1)

    text = []
    for y, color, t, extra in LINES:
        t = escape(t.format(ilvl=f"{ilvl:,}"))
        text.append(f'<text x="168" y="{y}" fill="{color}"{extra}>{t}</text>')

    return f"""<svg viewBox="0 0 840 380" width="840" height="380" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Doan Idriz, Forger of Agents: legendary item tooltip, item level {ilvl}">
  <title>Doan Idriz, Forger of Agents</title>
  <style>
    .w{{font-family:"Friz Quadrata TT","Friz Quadrata",Verdana,"Segoe UI",system-ui,sans-serif}}
    .aura{{animation:aura 2.4s ease-in-out infinite}}
    @keyframes aura{{50%{{opacity:.35}}}}
    .edge{{animation:edge 3s ease-in-out infinite}}
    @keyframes edge{{50%{{stroke:#fde68a;stroke-opacity:1}}}}
    @media (prefers-reduced-motion:reduce){{.aura,.edge{{animation:none}}}}
  </style>
  <defs>
    <radialGradient id="icon" cx=".35" cy=".3" r=".9"><stop offset="0" stop-color="#fdba74"/><stop offset=".45" stop-color="#ea580c"/><stop offset="1" stop-color="#431407"/></radialGradient>
    <linearGradient id="tip" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1225"/><stop offset="1" stop-color="#050913"/></linearGradient>
  </defs>

  <rect class="aura" x="10" y="10" width="112" height="112" rx="10" fill="none" stroke="{LEGENDARY}" stroke-width="3"/>
  <rect x="16" y="16" width="100" height="100" rx="6" fill="url(#icon)" stroke="#a3a3a3" stroke-width="3"/>
  <text x="66" y="84" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="44" font-weight="700" fill="#fff7ed">{{ }}</text>

  <rect class="edge" x="140" y="10" width="690" height="360" rx="8" fill="url(#tip)" fill-opacity=".96" stroke="#9ca3af" stroke-opacity=".7" stroke-width="2"/>
  <g class="w" font-size="15">
    <text x="168" y="46" font-size="23" font-weight="700" fill="{LEGENDARY}">Doan Idriz, Forger of Agents</text>
    {chr(10).join("    " + t for t in text).strip()}
    <text x="168" y="148" fill="{WHITE}">Two-Hand</text>
    <text x="804" y="148" text-anchor="end" fill="{WHITE}">Python</text>
    <text x="168" y="352" fill="{WHITE}">Sell Price: <tspan fill="{YELLOW}">hire me</tspan> <tspan fill="{YELLOW}" font-size="11">⬤</tspan></text>
    <text x="804" y="352" text-anchor="end" fill="{GREY}" font-size="13">Durability {cur_n} / {long_n}</text>
  </g>
</svg>
"""


def main():
    days = demo_days() if "--demo" in sys.argv else fetch_days()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(days))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

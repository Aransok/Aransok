"""Draws the static WoW-style README pieces: the action bar (tech stack) and
the quest log (projects). Edit the lists below and re-run:

    python3 .github/scripts/wow_static.py
"""
import os
from xml.sax.saxutils import escape as e

DIR = "profile-3d-contrib"
FONT = '"Friz Quadrata TT", Verdana, "Segoe UI", system-ui, sans-serif'

# --- action bar -------------------------------------------------------------
# (glyph on the icon, name under it, two gradient colors)
SKILLS = [
    ("Py", "Python", "#3776ab", "#ffd43b"),
    ("Dj", "Django", "#0c4b33", "#44b78b"),
    ("Fl", "Flask", "#1f2937", "#9ca3af"),
    ("Re", "React", "#0b3a4a", "#61dafb"),
    ("TS", "TypeScript", "#1e3a8a", "#3178c6"),
    ("Pg", "Postgres", "#1e3a5f", "#4f7ab3"),
    ("Pc", "Pinecone", "#14213d", "#38bdf8"),
    ("Dk", "Docker", "#0b3d91", "#2496ed"),
    ("n8", "n8n", "#4a1325", "#ea4b71"),
    ("Gt", "Git", "#5a1a0d", "#f05032"),
]
KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]


def action_bar():
    W, H, slot, gap = 840, 150, 64, 14
    x0 = (W - (len(SKILLS) * slot + (len(SKILLS) - 1) * gap)) / 2
    defs, slots = [], []
    for i, (glyph, name, c1, c2) in enumerate(SKILLS):
        x = x0 + i * (slot + gap)
        defs.append(
            f'<linearGradient id="s{i}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{c2}"/><stop offset="1" stop-color="{c1}"/></linearGradient>'
        )
        cd = (
            f'<rect x="{x + 3}" y="45" width="{slot - 6}" height="{slot - 6}" fill="#000" class="cd" '
            f'style="animation-delay:{i * 0.9:.1f}s"/>'
        )
        slots.append(f"""<g>
  <rect x="{x}" y="42" width="{slot}" height="{slot}" rx="6" fill="#0d0a06" stroke="#6b5426" stroke-width="2"/>
  <rect x="{x + 3}" y="45" width="{slot - 6}" height="{slot - 6}" rx="4" fill="url(#s{i})"/>
  <rect x="{x + 3}" y="45" width="{slot - 6}" height="{(slot - 6) / 2}" rx="4" fill="#fff" opacity=".12"/>
  {cd}
  <text x="{x + slot / 2}" y="{42 + slot / 2 + 9}" text-anchor="middle" font-size="24" font-weight="700" fill="#fff" stroke="#000" stroke-width=".8" paint-order="stroke">{glyph}</text>
  <text x="{x + slot - 7}" y="58" text-anchor="end" font-size="12" font-weight="700" fill="#e5e7eb" stroke="#000" stroke-width="2" paint-order="stroke">{KEYS[i]}</text>
  <text x="{x + slot / 2}" y="128" text-anchor="middle" font-size="11" fill="#c8b98f">{e(name)}</text>
</g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack as an action bar: {", ".join(s[1] for s in SKILLS)}">
<title>Action Bar</title>
<style>
text {{ font-family: {FONT}; }}
.cd {{ opacity: 0; animation: cd 9s linear infinite; }}
@keyframes cd {{ 0% {{ opacity: .6; }} 8% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .cd {{ animation: none; }} }}
</style>
<defs>
  <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b2418"/><stop offset="1" stop-color="#14100a"/></linearGradient>
  {"".join(defs)}
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="10" fill="url(#bar)" stroke="#c9a24a" stroke-width="3"/>
<text x="24" y="28" font-size="14" font-weight="700" fill="#ffd100">Action Bar</text>
<text x="816" y="28" text-anchor="end" font-size="11" fill="#9a8a6a">spells learned: {len(SKILLS)}</text>
{chr(10).join(slots)}
</svg>
"""


# --- quest log --------------------------------------------------------------
DONE = {
    "title": "Broffice: Open the Shop",
    "text": "Build and launch a full e-shop for a Bulgarian retailer.",
    "objectives": ["Product catalog", "Dual pricing engine", "Promotions system", "B2B and company orders", "Self-hosted CI/CD and backups"],
    "reward": "Real customers at broffice.bg",
}
ACTIVE = [
    ("AI Agents Office", "Run a virtual company of 8 AI agents."),
    ("Project Ember", "Forge a hardcore mobile RPG in Unity."),
]


def quest_log():
    W, H = 840, 400
    INK, HEAD, FAINT = "#2b1a08", "#5a2d00", "#7a5a32"
    obj = "".join(
        f'<text x="52" y="{150 + i * 24}" font-size="14" fill="{INK}"><tspan fill="#2f7d16" font-weight="700">✓</tspan>  {e(o)}</text>'
        for i, o in enumerate(DONE["objectives"])
    )
    act = "".join(
        f"""<g transform="translate(470 {118 + i * 100})">
  <circle cx="12" cy="-5" r="11" fill="#2a1d0c" stroke="#c9a24a"/>
  <text x="12" y="0" text-anchor="middle" font-size="15" font-weight="700" fill="#ffd100">!</text>
  <text x="34" y="0" font-size="16" font-weight="700" fill="{HEAD}">{e(t)}</text>
  <text x="34" y="22" font-size="12.5" fill="{INK}">{e(d)}</text>
  <rect x="34" y="34" width="296" height="8" rx="2" fill="#c8b48a"/>
  <rect x="34" y="34" width="296" height="8" rx="2" fill="#8a5a1c" class="prog" style="animation-delay:{i * .4:.1f}s"/>
</g>"""
        for i, (t, d) in enumerate(ACTIVE)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Quest log: completed Broffice, active {", ".join(a[0] for a in ACTIVE)}">
<title>Quest Log</title>
<style>
text {{ font-family: {FONT}; }}
.prog {{ transform-box: fill-box; transform-origin: left; animation: prog 6s ease-in-out infinite; }}
@keyframes prog {{ 0% {{ transform: scaleX(.15); }} 50% {{ transform: scaleX(.85); }} 100% {{ transform: scaleX(.15); }} }}
@media (prefers-reduced-motion: reduce) {{ .prog {{ animation: none; transform: scaleX(.6); }} }}
</style>
<defs>
  <radialGradient id="parch" cx=".5" cy=".45" r=".75"><stop offset="0" stop-color="#f3e3bf"/><stop offset=".8" stop-color="#e2c994"/><stop offset="1" stop-color="#c9a86a"/></radialGradient>
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="10" fill="#1a130b" stroke="#c9a24a" stroke-width="3"/>
<rect x="16" y="44" width="{W - 32}" height="{H - 60}" rx="4" fill="url(#parch)"/>
<text x="24" y="31" font-size="16" font-weight="700" fill="#ffd100">Quest Log</text>
<text x="816" y="31" text-anchor="end" font-size="11" fill="#9a8a6a">1 completed · {len(ACTIVE)} active</text>
<line x1="440" y1="64" x2="440" y2="368" stroke="{FAINT}" stroke-opacity=".5"/>

<text x="36" y="82" font-size="19" font-weight="700" fill="{HEAD}">{e(DONE["title"])}</text>
<text x="36" y="106" font-size="13" fill="{INK}">{e(DONE["text"])}</text>
<text x="36" y="132" font-size="13" font-weight="700" fill="{HEAD}">Objectives</text>
{obj}
<text x="36" y="290" font-size="13" font-weight="700" fill="{HEAD}">Rewards</text>
<text x="36" y="312" font-size="13" fill="{INK}">{e(DONE["reward"])}</text>
<g transform="translate(36 332)">
  <rect width="150" height="26" rx="3" fill="#2a1d0c" stroke="#c9a24a"/>
  <text x="75" y="18" text-anchor="middle" font-size="13" font-weight="700" fill="#ffd100">Quest Complete</text>
</g>

<text x="470" y="82" font-size="13" font-weight="700" fill="{HEAD}">ACTIVE QUESTS</text>
{act}
</svg>
"""


if __name__ == "__main__":
    os.makedirs(DIR, exist_ok=True)
    for name, svg in [("action-bar.svg", action_bar()), ("quest-log.svg", quest_log())]:
        with open(os.path.join(DIR, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", name)

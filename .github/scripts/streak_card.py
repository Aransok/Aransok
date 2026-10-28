"""Draws the WoW-style achievements panel (contribution streak card) for the profile README.

Runs in GitHub Actions with the built-in GITHUB_TOKEN, so no outside service
is involved. Pass --demo to render with made-up data (no network).
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone

USER = os.environ.get("USERNAME", "Aransok")
OUT = os.environ.get("OUT", "profile-3d-contrib/achievements.svg")

# Same palette as .github/profile-3d.json
BG, FG, WEAK = "#090b0f", "#e9edf2", "#8b95a3"
EMBER, TEAL, LINE = "#ffb35c", "#4cc7b4", "#1b2230"
CELLS = ["#141922", "#12423f", "#1d7268", "#4cc7b4", "#ffb35c"]


def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]


def fetch_days():
    created = gql(
        "query($u:String!){user(login:$u){createdAt}}", {"u": USER}
    )["user"]["createdAt"]
    start = datetime.fromisoformat(created.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    q = """query($u:String!,$f:DateTime!,$t:DateTime!){user(login:$u){
      contributionsCollection(from:$f,to:$t){contributionCalendar{
        weeks{contributionDays{date contributionCount}}}}}}"""
    days = {}
    year = start.year
    while year <= now.year:
        f = max(start, datetime(year, 1, 1, tzinfo=timezone.utc))
        t = min(now, datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        cal = gql(q, {"u": USER, "f": f.isoformat(), "t": t.isoformat()})
        for w in cal["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[date.fromisoformat(d["date"])] = d["contributionCount"]
        year += 1
    return sorted(days.items())


def demo_days():
    import random
    random.seed(4)
    today = date.today()
    out = []
    for i in range(500, -1, -1):
        d = today - timedelta(days=i)
        n = 0 if (random.random() < 0.25 and i > 23) else random.randint(1, 14)
        out.append((d, n))
    return out


def stats(days):
    total = sum(n for _, n in days)
    first_day = next((d for d, n in days if n), days[0][0])

    longest = (0, None, None)
    run, run_start = 0, None
    for d, n in days:
        if n:
            run_start = d if run == 0 else run_start
            run += 1
            if run > longest[0]:
                longest = (run, run_start, d)
        else:
            run = 0

    # Today with no commits yet doesn't break the streak.
    idx = len(days) - 1
    if days[idx][1] == 0:
        idx -= 1
    cur, cur_end = 0, days[idx][0] if idx >= 0 else None
    while idx >= 0 and days[idx][1]:
        cur += 1
        idx -= 1
    cur_start = cur_end - timedelta(days=cur - 1) if cur else None
    return total, first_day, (cur, cur_start, cur_end), longest


def fmt(d):
    return d.strftime("%b %-d, %Y") if d else ""


def span(a, b):
    if not a:
        return "No active streak"
    if a == b:
        return fmt(a)
    left = a.strftime("%b %-d") if a.year == b.year else fmt(a)
    return f"{left} to {fmt(b)}"


def level(n, top):
    if n == 0:
        return 0
    return min(4, 1 + int(3 * n / max(top, 1)))


def render(days):
    """WoW achievements panel: three achievement rows plus a daily XP bar."""
    total, first_day, cur, longest = stats(days)
    W, H = 840, 360
    GOLD, YEL, TXT, DIM = "#c9a24a", "#ffd100", "#f1e6cf", "#9a8a6a"

    def row(y, title, desc, sub, pts, icon, earned, delay):
        edge = GOLD if earned else "#4a4030"
        tcol = YEL if earned else DIM
        return f'''<g class="fade" style="animation-delay:{delay}s">
  <rect x="24" y="{y}" width="792" height="72" rx="6" fill="url(#rowbg)" stroke="{edge}" stroke-opacity=".8"/>
  <rect x="34" y="{y+8}" width="56" height="56" rx="4" fill="#1a120a" stroke="{edge}" stroke-width="2"/>
  <g transform="translate(62 {y+36})" fill="{tcol}">{icon}</g>
  <text x="420" y="{y+30}" text-anchor="middle" font-size="18" font-weight="700" fill="{tcol}">{title}</text>
  <text x="420" y="{y+52}" text-anchor="middle" font-size="13" fill="{TXT}">{desc}</text>
  <text x="420" y="{y+67}" text-anchor="middle" font-size="11" fill="{DIM}">{sub}</text>
  <path d="M760 {y+12} h36 v26 q0 18 -18 26 q-18 -8 -18 -26z" fill="#2a1d0c" stroke="{edge}" stroke-width="2"/>
  <text x="778" y="{y+42}" text-anchor="middle" font-size="{14 if pts < 1000 else 11}" font-weight="700" fill="{TXT}">{pts:,}</text>
</g>'''

    flame = '<path class="flame" d="M0 -20 c10 12 14 20 14 28 a14 14 0 0 1 -28 0 c0 -6 3 -10 6 -13 c0 5 2 8 5 9 c-1 -9 1 -16 3 -24z"/>'
    sword = '<path d="M-16 16 l4 4 l6 -6 l4 4 l3 -3 l-4 -4 l17 -17 l2 -12 l-12 2 l-17 17 l-4 -4 l-3 3 l4 4z"/>'
    coins = '<ellipse cx="0" cy="12" rx="16" ry="6"/><ellipse cx="0" cy="3" rx="16" ry="6" opacity=".85"/><ellipse cx="0" cy="-6" rx="16" ry="6" opacity=".7"/><ellipse cx="0" cy="-15" rx="16" ry="6"/>'

    alive = cur[0] > 0
    rows = (
        row(70, "Unbroken Chain", f"Commit {cur[0]} days in a row", span(cur[1], cur[2]) if alive else "Start a new streak today", cur[0], flame, alive, .1)
        + row(152, "Iron Will", f"Longest streak: {longest[0]} days", span(longest[1], longest[2]), longest[0], sword, longest[0] > 0, .25)
        + row(234, "The Grind", f"{total:,} contributions on GitHub", f"{fmt(first_day)} to present", total, coins, total > 0, .4)
    )

    recent = days[-53:]
    top = max((n for _, n in recent), default=1)
    xp_cols = ["#1b1530", "#3b2a6b", "#6a3fb5", "#9a63e6", YEL]
    seg_w = 762 / len(recent)
    xp = "".join(
        f'<rect x="{39 + i * seg_w:.1f}" y="328" width="{seg_w - 2:.1f}" height="12" fill="{xp_cols[level(n, top)]}" class="cell" style="animation-delay:{i * 15}ms"><title>{d}: {n}</title></rect>'
        for i, (d, n) in enumerate(recent)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Achievements: current streak {cur[0]} days, longest {longest[0]} days, {total} contributions">
<title>Achievements</title>
<style>
text {{ font-family: "Friz Quadrata TT", Verdana, "Segoe UI", system-ui, sans-serif; }}
.fade {{ animation: fade .7s ease-out backwards; }}
.cell {{ animation: fade .4s ease-out backwards; }}
.flame {{ animation: flicker 1.6s ease-in-out infinite; }}
@keyframes fade {{ from {{ opacity: 0; }} }}
@keyframes flicker {{ 50% {{ opacity: .6; }} }}
@media (prefers-reduced-motion: reduce) {{ .fade, .cell, .flame {{ animation: none; }} }}
</style>
<defs>
  <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a130b"/><stop offset="1" stop-color="#0b0805"/></linearGradient>
  <linearGradient id="rowbg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a1e0f"/><stop offset=".5" stop-color="#1c140a"/><stop offset="1" stop-color="#2a1e0f"/></linearGradient>
</defs>
<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="10" fill="url(#panel)" stroke="{GOLD}" stroke-width="3"/>
<rect x="9" y="9" width="{W-18}" height="{H-18}" rx="6" fill="none" stroke="#5a4520"/>
<text x="28" y="48" font-size="22" font-weight="700" fill="{YEL}">Achievements</text>
<text x="812" y="48" text-anchor="end" font-size="15" font-weight="700" fill="{YEL}">{total + cur[0] + longest[0]:,}</text>
<text x="812" y="30" text-anchor="end" font-size="11" fill="{DIM}">Achievement Points</text>
{rows}
<text x="39" y="322" font-size="11" fill="{DIM}">Daily XP · last {len(recent)} days</text>
<rect x="36" y="325" width="768" height="18" rx="3" fill="#0a0710" stroke="#5a4520"/>
{xp}
</svg>
'''


if __name__ == "__main__":
    days = demo_days() if "--demo" in sys.argv else fetch_days()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(days))
    print("wrote", OUT, stats(days)[2:])

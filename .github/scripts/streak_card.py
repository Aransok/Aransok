"""Draws the contribution streak card for the profile README.

Runs in GitHub Actions with the built-in GITHUB_TOKEN, so no outside service
is involved. Pass --demo to render with made-up data (no network).
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone

USER = os.environ.get("USERNAME", "Aransok")
OUT = os.environ.get("OUT", "profile-3d-contrib/streak-ember.svg")

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
    return f"{left} – {fmt(b)}"


def level(n, top):
    if n == 0:
        return 0
    return min(4, 1 + int(3 * n / max(top, 1)))


def render(days):
    total, first_day, cur, longest = stats(days)
    W, H = 1280, 345
    col = [W / 6, W / 2, 5 * W / 6]

    recent = days[-53:]
    top = max((n for _, n in recent), default=1)
    cell, gap = 18, 4
    strip_w = len(recent) * (cell + gap) - gap
    x0 = (W - strip_w) / 2
    strip = "".join(
        f'<rect x="{x0 + i * (cell + gap):.1f}" y="300" width="{cell}" height="{cell}" rx="4" '
        f'fill="{CELLS[level(n, top)]}" style="animation-delay:{i * 18}ms" class="cell"><title>{d}: {n}</title></rect>'
        for i, (d, n) in enumerate(recent)
    )

    alive = cur[0] > 0
    ring = EMBER if alive else WEAK
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
* {{ font-family: "Ubuntu", "Helvetica", "Arial", sans-serif; }}
.big {{ font-size: 64px; font-weight: 700; }}
.label {{ font-size: 22px; font-weight: 600; fill: {FG}; }}
.sub {{ font-size: 17px; fill: {WEAK}; }}
.fade {{ animation: fade .7s ease-out backwards; }}
.cell {{ animation: fade .4s ease-out backwards; }}
.flame {{ transform-origin: {col[1]}px 64px; animation: flicker 1.6s ease-in-out infinite; }}
@keyframes fade {{ from {{ opacity: 0; }} }}
@keyframes flicker {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.12) rotate(-3deg); }} }}
</style>
<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>
<line x1="{W/3}" y1="50" x2="{W/3}" y2="250" stroke="{LINE}" stroke-width="2"/>
<line x1="{2*W/3}" y1="50" x2="{2*W/3}" y2="250" stroke="{LINE}" stroke-width="2"/>

<g class="fade" style="animation-delay:.1s" text-anchor="middle">
  <text x="{col[0]}" y="150" class="big" fill="{TEAL}">{total:,}</text>
  <text x="{col[0]}" y="200" class="label">Total Contributions</text>
  <text x="{col[0]}" y="230" class="sub">{fmt(first_day)} – Present</text>
</g>

<g class="fade" style="animation-delay:.25s" text-anchor="middle">
  <circle cx="{col[1]}" cy="128" r="62" fill="none" stroke="{ring}" stroke-width="6" stroke-opacity=".9"/>
  <rect x="{col[1]-22}" y="52" width="44" height="30" fill="{BG}"/>
  <path class="flame" fill="{ring}" d="M{col[1]} 46 c10 12 14 20 14 28 a14 14 0 0 1 -28 0 c0 -6 3 -10 6 -13 c0 5 2 8 5 9 c-1 -9 1 -16 3 -24 z"/>
  <text x="{col[1]}" y="150" class="big" fill="{EMBER if alive else FG}">{cur[0]}</text>
  <text x="{col[1]}" y="226" class="label" fill="{EMBER}">Current Streak</text>
  <text x="{col[1]}" y="254" class="sub">{span(cur[1], cur[2])}</text>
</g>

<g class="fade" style="animation-delay:.4s" text-anchor="middle">
  <text x="{col[2]}" y="150" class="big" fill="{FG}">{longest[0]}</text>
  <text x="{col[2]}" y="200" class="label">Longest Streak</text>
  <text x="{col[2]}" y="230" class="sub">{span(longest[1], longest[2])}</text>
</g>

<text x="{x0}" y="288" class="sub" font-size="14">Last {len(recent)} days</text>
{strip}
</svg>
'''


if __name__ == "__main__":
    days = demo_days() if "--demo" in sys.argv else fetch_days()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(days))
    print("wrote", OUT, stats(days)[2:])

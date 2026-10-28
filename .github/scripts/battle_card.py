"""Draws the "Bug Hunt" panel: a pixel hero fighting through an endless world.

One 12 second loop: two crawling bugs (sword), a flying bug (fireball), then the
LEGACY CODE elite boss (3-hit combo, it hits back), coins, XP and LEVEL UP.
Every animation is pure CSS generated from the EVENT times below, so it runs
inside a GitHub README image. The kill counter reads the real contribution
count from legendary-item.svg when it exists.

    python3 .github/scripts/battle_card.py
"""
import os
import random
import re

OUT = "profile-3d-contrib/battle.svg"
W, H = 840, 270
GROUND = 222
C = 12.0  # loop length in seconds
PX = 4
rng = random.Random(27)

# --- timeline (seconds) -----------------------------------------------------
A_SPAWN, A_HIT = 0.0, 1.6          # NullPointer, sword
B_SPAWN, B_HIT = 1.9, 3.5          # off-by-one, sword
CAST, M_HIT = 4.5, 5.15            # fireball at the flying memory leak
BOSS_IN, BOSS_STOP = 5.5, 7.3      # LEGACY CODE walks in
BOSS_HITS = [7.6, 8.2, 8.8]        # 3-hit combo, last one crits
BOSS_ATK = 7.95                    # boss strikes back
BOSS_DIE = 8.95
LVL_UP, LVL_END = 9.4, 10.9
SWINGS = [A_HIT, B_HIT] + BOSS_HITS
WALK = [(0.0, 1.5), (1.95, 3.4), (3.75, 4.3), (5.4, 7.3), (10.9, 12.0)]

HERO_X = 200
HERO_W = 12 * PX
CONTACT = HERO_X + HERO_W + 14


def pct(t):
    return max(0.0, min(100.0, t / C * 100))


def kf(name, stops):
    """stops: list of (seconds, css). Adds 0% and 100% if missing."""
    stops = sorted(stops, key=lambda s: s[0])
    if stops[0][0] > 0:
        stops.insert(0, (0, stops[0][1]))
    if stops[-1][0] < C:
        stops.append((C, stops[-1][1]))
    body = " ".join(f"{pct(t):.2f}% {{ {css} }}" for t, css in stops)
    return f"@keyframes {name} {{ {body} }}"


def sprite(rows, cols, x0, y0, px=PX):
    out = []
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c in cols:
                out.append(f'<rect x="{x0 + x * px}" y="{y0 + y * px}" width="{px}" height="{px}" fill="{cols[c]}"/>')
    return "".join(out)


# --- sprites ----------------------------------------------------------------
HERO_TOP = [
    "....hhhh....",
    "...hHHHHh...",
    "..hHffffHh..",
    "..hfeffefh..",
    "..hffffffh..",
    ".ccOOOOOOc..",
    "ccOOOgOOOOc.",
    "ccOOOgOOOOc.",
    ".cOOOgOOOOc.",
    "..cOOOOOOc..",
]
LEGS_A = ["...bb..bb...", "...bb..bb...", "..BBB..BBB.."]
LEGS_B = ["....bbbb....", "...bb..bb...", "..BBB...BBB."]
HERO_COL = {"h": "#0f766e", "H": "#2dd4bf", "f": "#fcd9b6", "e": "#111827", "c": "#7c2d12",
            "O": "#f97316", "g": "#fde047", "b": "#3f3f46", "B": "#18181b"}
HERO_RED = {k: "#ef4444" for k in HERO_COL}

BUG = [
    "..a.....a..",
    "...a...a...",
    "..kKKKKKk..",
    ".kKrKKKrKk.",
    "kKKKKKKKKKk",
    ".kKKKKKKKk.",
    "..l.l.l.l..",
    ".l..l.l..l.",
]
MOTH = [
    "ww.....ww",
    "wwwa.awww",
    "wwwkKkwww",
    ".wwkKkww.",
    "..wkKkw..",
    "...k.k...",
]
BOSS = [
    ".....g.g..g.g....",
    ".....ggggggg.....",
    "...a.........a...",
    "....a.......a....",
    "...kKKKKKKKKKk...",
    "..kKKrrKKKrrKKk..",
    ".kKKKrrKKKrrKKKk.",
    "kKKKKKKKKKKKKKKKk",
    "kKKmmKmmKmmKmmKKk",
    "kKKKKKKKKKKKKKKKk",
    ".kKKKKKKKKKKKKKk.",
    "..l..l..l..l..l..",
    ".l..l..l..l..l..l",
]
BOSS_PX = 6


# --- pieces -----------------------------------------------------------------
css = []   # collected keyframes + rules
defs = []


def hero():
    h = (len(HERO_TOP) + 3) * PX
    y0 = GROUND - h
    top = sprite(HERO_TOP, HERO_COL, HERO_X, y0)
    la = sprite(LEGS_A, HERO_COL, HERO_X, y0 + len(HERO_TOP) * PX)
    lb = sprite(LEGS_B, HERO_COL, HERO_X, y0 + len(HERO_TOP) * PX)
    red = sprite(HERO_TOP + LEGS_A, HERO_RED, HERO_X, y0)
    hx, hy = HERO_X + 42, y0 + 28  # sword hand
    sword = (
        f'<g class="bh-sword" style="transform-origin:{hx}px {hy}px">'
        f'<rect x="{hx - 2}" y="{hy - 4}" width="4" height="10" fill="#78350f"/>'
        f'<rect x="{hx - 8}" y="{hy - 8}" width="16" height="4" fill="#fde047"/>'
        f'<rect x="{hx - 3}" y="{hy - 48}" width="6" height="40" fill="#e5e7eb"/>'
        f'<rect x="{hx - 3}" y="{hy - 48}" width="2" height="40" fill="#fff"/>'
        f'<rect x="{hx - 1}" y="{hy - 46}" width="2" height="36" fill="#7dd3fc" class="bh-rune"/>'
        f"</g>"
    )
    glow = f'<circle cx="{hx + 4}" cy="{hy - 6}" r="10" fill="url(#bh-fire)" class="bh-handglow"/>'
    slash = (
        f'<path class="bh-slash" d="M{hx + 8} {hy - 46} Q{hx + 64} {hy - 10} {hx + 22} {hy + 34}" '
        f'fill="none" stroke="#fde68a" stroke-width="6" stroke-linecap="round"/>'
        f'<path class="bh-slash" d="M{hx + 14} {hy - 40} Q{hx + 56} {hy - 8} {hx + 24} {hy + 26}" '
        f'fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/>'
    )

    # sword timeline
    st = [(0, "transform: rotate(-35deg)")]
    for t in SWINGS:
        st += [(t - 0.28, "transform: rotate(-35deg)"), (t - 0.08, "transform: rotate(-80deg)"),
               (t, "transform: rotate(120deg)"), (t + 0.22, "transform: rotate(-35deg)")]
    st += [(CAST - 0.4, "transform: rotate(-35deg)"), (CAST - 0.15, "transform: rotate(-150deg)"),
           (CAST + 0.25, "transform: rotate(-150deg)"), (CAST + 0.55, "transform: rotate(-35deg)")]
    st += [(LVL_UP, "transform: rotate(-35deg)"), (LVL_UP + 0.2, "transform: rotate(-170deg)"),
           (LVL_END - 0.3, "transform: rotate(-170deg)"), (LVL_END, "transform: rotate(-35deg)")]
    css.append(kf("bh-sword", st))
    css.append(".bh-sword { animation: bh-sword 12s linear infinite; }")

    sl = [(0, "opacity: 0")]
    for t in SWINGS:
        sl += [(t - 0.02, "opacity: 0"), (t, "opacity: 1"), (t + 0.14, "opacity: 0")]
    css.append(kf("bh-slash", sl))
    css.append(".bh-slash { opacity: 0; animation: bh-slash 12s linear infinite; }")

    css.append(kf("bh-handglow", [(0, "opacity: 0; transform: scale(.2)"), (CAST - 0.4, "opacity: 0; transform: scale(.2)"),
                                  (CAST - 0.05, "opacity: 1; transform: scale(1.4)"), (CAST + 0.1, "opacity: 0; transform: scale(.4)")]))
    css.append(f".bh-handglow {{ transform-origin: {hx + 4}px {hy - 6}px; animation: bh-handglow 12s ease-out infinite; }}")

    # legs: alternate only while walking
    on = [(0, "opacity: 0")]
    for a, b in WALK:
        n = int((b - a) / 0.16)
        for i in range(n):
            t = a + i * 0.16
            on += [(t, f"opacity: {i % 2}"), (t + 0.159, f"opacity: {i % 2}")]
        on += [(b, "opacity: 0")]
    css.append(".bh-legb { opacity: 0; }")
    css.append(kf("bh-legb", on))
    css.append(".bh-legb { animation: bh-legb 12s step-end infinite; }")

    css.append(kf("bh-hurt", [(0, "opacity: 0"), (BOSS_ATK, "opacity: 0"), (BOSS_ATK + 0.03, "opacity: .75"),
                              (BOSS_ATK + 0.25, "opacity: 0")]))
    css.append(".bh-hurt { opacity: 0; animation: bh-hurt 12s linear infinite; }")
    css.append(kf("bh-knock", [(0, "transform: none"), (BOSS_ATK, "transform: none"), (BOSS_ATK + 0.08, "transform: translateX(-10px)"),
                               (BOSS_ATK + 0.3, "transform: none")]))
    css.append(".bh-hero { animation: bh-knock 12s ease-out infinite; }")

    shadow = f'<ellipse cx="{HERO_X + 24}" cy="{GROUND + 3}" rx="24" ry="4" fill="#000" opacity=".5"/>'
    return (f'{shadow}<g class="bh-hero"><g class="bh-px">{top}<g>{la}</g><g class="bh-legb">{lb}</g>'
            f'<g class="bh-hurt">{red}</g></g>{sword}{glow}</g>{slash}')


def walker(name, rows, cols, spawn, hit, px=PX, label=""):
    """A crawling enemy that walks to the hero, gets hit once and dies."""
    w = len(rows[0]) * px
    h = len(rows) * px
    x0, y0 = W + 10, GROUND - h
    travel = CONTACT - x0
    arrive = hit - 0.12
    css.append(kf(f"bh-{name}", [
        (0, "opacity: 0; transform: translateX(0)"),
        (spawn, "opacity: 1; transform: translateX(0)"),
        (arrive, "opacity: 1; transform: translateX(%dpx)" % travel),
        (hit, "opacity: 1; transform: translateX(%dpx)" % travel),
        (hit + 0.04, "opacity: .2; transform: translateX(%dpx)" % (travel + 8)),
        (hit + 0.08, "opacity: 1; transform: translateX(%dpx)" % (travel + 14)),
        (hit + 0.4, "opacity: 0; transform: translate(%dpx, -34px) rotate(40deg)" % (travel + 60)),
        (C - 0.01, "opacity: 0; transform: translateX(0)"),
    ]))
    css.append(f".bh-{name} {{ opacity: 0; animation: bh-{name} 12s linear infinite; transform-box: view-box; }}")
    hp = (f'<rect x="{x0 + w / 2 - 20}" y="{y0 - 10}" width="40" height="5" fill="#3f0d0d"/>'
          f'<rect x="{x0 + w / 2 - 20}" y="{y0 - 10}" width="40" height="5" fill="#dc2626" class="bh-{name}-hp" '
          f'style="transform-origin:{x0 + w / 2 - 20}px 0"/>')
    css.append(kf(f"bh-{name}-hp", [(0, "transform: scaleX(1)"), (hit, "transform: scaleX(1)"), (hit + 0.05, "transform: scaleX(0)")]))
    css.append(f".bh-{name}-hp {{ animation: bh-{name}-hp 12s linear infinite; }}")
    tag = f'<text x="{x0 + w / 2}" y="{y0 - 15}" text-anchor="middle" class="bh-tag">{label}</text>'
    shadow = f'<ellipse cx="{x0 + w / 2}" cy="{GROUND + 3}" rx="{w / 2}" ry="3" fill="#000" opacity=".4"/>'
    return f'<g class="bh-{name}">{shadow}<g class="bh-crawl bh-px">{sprite(rows, cols, x0, y0, px)}</g>{hp}{tag}</g>', CONTACT + w / 2


def moth():
    w, h = len(MOTH[0]) * PX, len(MOTH) * PX
    x0, y0 = W + 10, 100
    stop_x = 560
    cols = {"w": "#67e8f9", "a": "#a3a3a3", "k": "#111", "K": "#0e7490"}
    css.append(kf("bh-moth", [
        (0, "opacity: 0; transform: translate(0, 0)"),
        (3.2, "opacity: 1; transform: translate(0, 0)"),
        (4.0, "opacity: 1; transform: translate(%dpx, 24px)" % ((stop_x - x0) * .6)),
        (4.7, "opacity: 1; transform: translate(%dpx, -6px)" % (stop_x - x0)),
        (M_HIT, "opacity: 1; transform: translate(%dpx, 10px)" % (stop_x - x0)),
        (M_HIT + 0.05, "opacity: .2; transform: translate(%dpx, 10px)" % (stop_x - x0)),
        (M_HIT + 0.5, "opacity: 0; transform: translate(%dpx, 80px) rotate(160deg)" % (stop_x - x0 + 20)),
        (C - 0.01, "opacity: 0; transform: translate(0, 0)"),
    ]))
    css.append(".bh-moth { opacity: 0; animation: bh-moth 12s ease-in-out infinite; transform-box: view-box; }")
    css.append(f"@keyframes bh-flap {{ 50% {{ transform: scaleY(.35); }} }} .bh-flap {{ transform-origin: {x0 + w / 2}px {y0 + h / 2}px; animation: bh-flap .18s steps(1) infinite; }}")
    tag = f'<text x="{x0 + w / 2}" y="{y0 - 8}" text-anchor="middle" class="bh-tag">memory leak</text>'
    return f'<g class="bh-moth"><g class="bh-flap bh-px">{sprite(MOTH, cols, x0, y0)}</g>{tag}</g>', (stop_x + w / 2, y0 + 10 + h / 2)


def fireball(target):
    hx, hy = HERO_X + 46, GROUND - 52 - 6
    tx, ty = target
    css.append(kf("bh-fireball", [
        (0, "opacity: 0; transform: translate(0, 0) scale(.4)"),
        (CAST - 0.02, "opacity: 0; transform: translate(0, 0) scale(.4)"),
        (CAST, "opacity: 1; transform: translate(0, 0) scale(1)"),
        ((CAST + M_HIT) / 2, "opacity: 1; transform: translate(%dpx, %dpx) scale(1.2)" % ((tx - hx) / 2, (ty - hy) / 2 - 40)),
        (M_HIT, "opacity: 1; transform: translate(%dpx, %dpx) scale(1.3)" % (tx - hx, ty - hy)),
        (M_HIT + 0.02, "opacity: 0; transform: translate(%dpx, %dpx) scale(.2)" % (tx - hx, ty - hy)),
    ]))
    css.append(f".bh-fireball {{ opacity: 0; transform-box: view-box; transform-origin: {hx}px {hy}px; animation: bh-fireball 12s linear infinite; }}")
    ball = (f'<g class="bh-fireball"><circle cx="{hx - 10}" cy="{hy + 4}" r="6" fill="#f97316" opacity=".4"/>'
            f'<circle cx="{hx - 5}" cy="{hy + 2}" r="8" fill="#fb923c" opacity=".6"/>'
            f'<circle cx="{hx}" cy="{hy}" r="11" fill="url(#bh-fire)"/></g>')
    return ball + boom(M_HIT, tx, ty, "#fb923c", 46)


def boom(t, x, y, color, r):
    """Expanding shock ring + flash."""
    n = len(css)
    css.append(kf(f"bh-boom{n}", [(0, "opacity: 0; transform: scale(.1)"), (t, "opacity: 0; transform: scale(.1)"),
                                  (t + 0.02, "opacity: 1; transform: scale(.3)"), (t + 0.45, "opacity: 0; transform: scale(1)")]))
    return (f'<g style="transform-origin:{x}px {y}px;opacity:0;animation:bh-boom{n} 12s ease-out infinite">'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{color}" stroke-width="4"/>'
            f'<circle cx="{x}" cy="{y}" r="{r * .55}" fill="{color}" opacity=".35"/></g>')


def burst(t, x, y, colors, n=12, spread=60, up=50):
    out = []
    for i in range(n):
        dx = rng.uniform(-spread, spread)
        dy = -rng.uniform(up * .3, up)
        s = rng.choice([3, 4, 5])
        name = f"bh-p{len(css)}"
        css.append(kf(name, [
            (0, "opacity: 0; transform: translate(0, 0)"), (t, "opacity: 0; transform: translate(0, 0)"),
            (t + 0.02, "opacity: 1; transform: translate(0, 0)"),
            (t + 0.3, "opacity: 1; transform: translate(%.0fpx, %.0fpx)" % (dx * .7, dy)),
            (t + 0.7, "opacity: 0; transform: translate(%.0fpx, %.0fpx)" % (dx, dy + 60)),
        ]))
        out.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{rng.choice(colors)}" '
                   f'style="opacity:0;animation:{name} 12s cubic-bezier(.2,.7,.4,1) infinite"/>')
    return "".join(out)


def coins(t, x, y, n=14):
    out = []
    for i in range(n):
        dx = rng.uniform(-110, 70)
        peak = -rng.uniform(40, 90)
        name = f"bh-c{len(css)}"
        css.append(kf(name, [
            (0, "opacity: 0; transform: translate(0, 0)"), (t, "opacity: 0; transform: translate(0, 0)"),
            (t + 0.02, "opacity: 1; transform: translate(0, 0)"),
            (t + 0.35, "opacity: 1; transform: translate(%.0fpx, %.0fpx)" % (dx * .5, peak)),
            (t + 0.75, "opacity: 1; transform: translate(%.0fpx, %.0fpx)" % (dx, GROUND - y - 6)),
            (t + 1.6, "opacity: 1; transform: translate(%.0fpx, %.0fpx)" % (dx, GROUND - y - 6)),
            (t + 1.9, "opacity: 0; transform: translate(%.0fpx, %.0fpx)" % (HERO_X - x + 20, GROUND - y - 30)),
        ]))
        out.append(f'<g style="opacity:0;animation:{name} 12s ease-in infinite"><circle cx="{x}" cy="{y}" r="5" fill="#ffd100" stroke="#a16207" stroke-width="1.5"/>'
                   f'<rect x="{x - 1}" y="{y - 3}" width="2" height="6" fill="#fff7ae"/></g>')
    return "".join(out)


def popup(t, x, y, text, color, size=18, dur=0.9):
    name = f"bh-t{len(css)}"
    css.append(kf(name, [(0, "opacity: 0; transform: translate(0, 0) scale(.6)"), (t, "opacity: 0; transform: translate(0, 0) scale(.6)"),
                         (t + 0.04, "opacity: 1; transform: translate(0, -6px) scale(1.25)"),
                         (t + 0.18, "opacity: 1; transform: translate(0, -12px) scale(1)"),
                         (t + dur, "opacity: 0; transform: translate(0, -46px) scale(1)")]))
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" font-weight="700" fill="{color}" class="bh-pop" '
            f'style="transform-origin:{x}px {y}px;opacity:0;animation:{name} 12s ease-out infinite">{text}</text>')


def boss():
    w, h = len(BOSS[0]) * BOSS_PX, len(BOSS) * BOSS_PX
    x0, y0 = W + 20, GROUND - h
    stop = CONTACT + 6
    travel = stop - x0
    cols = {"g": "#ffd100", "a": "#a3a3a3", "k": "#0a0a0a", "K": "#581c87", "r": "#f87171", "m": "#f5f5f4", "l": "#404040"}
    st = [(0, "opacity: 0; transform: translateX(0)"), (BOSS_IN, "opacity: 1; transform: translateX(0)"),
          (BOSS_STOP, "opacity: 1; transform: translateX(%dpx)" % travel)]
    for t in BOSS_HITS:
        st += [(t - 0.01, "opacity: 1; transform: translateX(%dpx)" % travel),
               (t + 0.03, "opacity: .25; transform: translateX(%dpx)" % (travel + 10)),
               (t + 0.08, "opacity: 1; transform: translateX(%dpx)" % (travel + 4)),
               (t + 0.2, "opacity: 1; transform: translateX(%dpx)" % travel)]
    st += [(BOSS_ATK - 0.15, "opacity: 1; transform: translateX(%dpx)" % (travel + 14)),
           (BOSS_ATK, "opacity: 1; transform: translateX(%dpx)" % (travel - 22)),
           (BOSS_ATK + 0.15, "opacity: 1; transform: translateX(%dpx)" % travel)]
    st += [(BOSS_DIE, "opacity: 1; transform: translateX(%dpx) scale(1)" % travel),
           (BOSS_DIE + 0.1, "opacity: 1; transform: translateX(%dpx) scale(1.15)" % travel),
           (BOSS_DIE + 0.4, "opacity: 0; transform: translateX(%dpx) scale(1.5)" % travel),
           (C - 0.01, "opacity: 0; transform: translateX(0)")]
    css.append(kf("bh-boss", st))
    cx, cy = x0 + w / 2, y0 + h / 2
    css.append(f".bh-boss {{ opacity: 0; transform-box: view-box; transform-origin: {cx}px {GROUND}px; animation: bh-boss 12s linear infinite; }}")
    css.append(f"@keyframes bh-stomp {{ 50% {{ transform: translateY(-4px); }} }} .bh-stomp {{ animation: bh-stomp .4s steps(2) infinite; }}")
    tag = f'<text x="{cx}" y="{y0 - 8}" text-anchor="middle" class="bh-tag" fill="#ffd100" style="fill:#ffd100;font-weight:700">LEGACY CODE</text>'
    shadow = f'<ellipse cx="{cx}" cy="{GROUND + 3}" rx="{w / 2}" ry="5" fill="#000" opacity=".5"/>'
    eyes = f'<circle cx="{x0 + 6.5 * BOSS_PX}" cy="{y0 + 6 * BOSS_PX}" r="10" fill="#ef4444" opacity=".25" class="bh-eyes"/><circle cx="{x0 + 11.5 * BOSS_PX}" cy="{y0 + 6 * BOSS_PX}" r="10" fill="#ef4444" opacity=".25" class="bh-eyes"/>'
    css.append("@keyframes bh-eyes { 50% { opacity: .6; } } .bh-eyes { animation: bh-eyes .8s ease-in-out infinite; }")
    body = f'<g class="bh-boss">{shadow}<g class="bh-stomp"><g class="bh-px">{sprite(BOSS, cols, x0, y0, BOSS_PX)}</g>{eyes}</g>{tag}</g>'
    return body, (stop + w / 2, cy)


def level_up():
    x = HERO_X + 24
    css.append(kf("bh-beam", [(0, "opacity: 0; transform: scaleY(0)"), (LVL_UP, "opacity: 0; transform: scaleY(0)"),
                              (LVL_UP + 0.2, "opacity: .85; transform: scaleY(1)"), (LVL_END - 0.4, "opacity: .6; transform: scaleY(1)"),
                              (LVL_END, "opacity: 0; transform: scaleY(1)")]))
    css.append(f".bh-beam {{ transform-origin: {x}px {GROUND}px; opacity: 0; animation: bh-beam 12s ease-out infinite; }}")
    beam = f'<rect x="{x - 34}" y="0" width="68" height="{GROUND}" fill="url(#bh-beam)" class="bh-beam"/>'
    ring = boom(LVL_UP + 0.1, x, GROUND - 28, "#ffd100", 70)
    sparks = burst(LVL_UP + 0.15, x, GROUND - 30, ["#ffd100", "#fde68a", "#fff"], n=18, spread=80, up=120)
    text = popup(LVL_UP + 0.2, W / 2, 120, "LEVEL UP!", "#ffd100", size=40, dur=1.4)
    sub = popup(LVL_UP + 0.35, W / 2, 148, "new skill unlocked: Ship It", "#2dd4bf", size=14, dur=1.3)
    return beam + ring + sparks + text + sub


def ground_layer():
    # piecewise scroll: tiles move only while the hero walks
    speed_total = sum(b - a for a, b in WALK)
    dist_total = 480  # multiple of the 40px tile so the loop is seamless
    v = dist_total / speed_total
    stops, d = [(0, "transform: translateX(0)")], 0.0
    for a, b in WALK:
        stops.append((a, f"transform: translateX({-d:.1f}px)"))
        d += (b - a) * v
        stops.append((b, f"transform: translateX({-d:.1f}px)"))
    css.append(kf("bh-tiles", stops))
    css.append(".bh-tiles { animation: bh-tiles 12s linear infinite; }")
    tiles = "".join(
        f'<rect x="{x}" y="{GROUND}" width="38" height="12" fill="#2b2014"/><rect x="{x}" y="{GROUND}" width="38" height="2" fill="#6b5426"/>'
        f'<rect x="{x + 6}" y="{GROUND + 16}" width="26" height="8" fill="#1f170e"/>'
        + (f'<rect x="{x + 14}" y="{GROUND - 6}" width="3" height="6" fill="#3f6212"/><rect x="{x + 19}" y="{GROUND - 4}" width="3" height="4" fill="#4d7c0f"/>' if (x // 40) % 3 == 0 else "")
        for x in range(0, W + dist_total + 80, 40)
    )
    return f'<g class="bh-tiles">{tiles}</g>'


def scenery():
    stars = "".join(
        f'<circle cx="{rng.uniform(10, W - 10):.0f}" cy="{rng.uniform(56, 130):.0f}" r="{rng.uniform(.6, 1.5):.1f}" fill="#fff" '
        f'class="bh-star" style="animation-delay:{rng.uniform(0, 3):.1f}s"/>' for _ in range(40))
    far = "M0 170 L60 128 L110 150 L170 112 L240 152 L300 120 L360 148 L430 104 L500 150 L560 126 L630 150 L700 110 L770 146 L840 170 Z"
    mid = ("M0 190 Q70 150 150 178 Q220 140 300 174 Q370 132 450 170 Q540 146 610 176 Q690 150 760 174 Q800 164 840 186 V"
           f"{GROUND} H0Z")
    arches = "".join(f'<rect x="{318 + i * 26}" y="{GROUND - 30}" width="14" height="22" rx="7" fill="#170e1f"/>' for i in range(8))
    theatre = f'<rect x="304" y="{GROUND - 38}" width="226" height="38" fill="#26172f"/>{arches}'
    lay = lambda cls, inner: f'<g class="{cls}">{inner}<g transform="translate(840 0)">{inner}</g></g>'  # noqa: E731
    css.append("@keyframes bh-far { to { transform: translateX(-840px); } } .bh-far { animation: bh-far 90s linear infinite; }")
    css.append("@keyframes bh-mid { to { transform: translateX(-840px); } } .bh-mid { animation: bh-mid 45s linear infinite; }")
    css.append("@keyframes bh-tw { 50% { opacity: .15; } } .bh-star { animation: bh-tw 3s ease-in-out infinite; }")
    moon = '<circle cx="740" cy="74" r="20" fill="#fde68a"/><circle cx="749" cy="68" r="18" fill="#1d1033"/>'
    fog = f'<rect x="0" y="{GROUND - 46}" width="{W}" height="46" fill="url(#bh-fog)"/>'
    return (f'<rect x="0" y="0" width="{W}" height="{GROUND}" fill="url(#bh-sky)"/>{stars}{moon}'
            + lay("bh-far", f'<path d="{far}" fill="#1c1430"/>')
            + lay("bh-mid", f'<path d="{mid}" fill="#140c1c"/>{theatre}') + fog)


def hud(kills):
    out = []
    # hero frame
    out.append('<rect x="16" y="14" width="44" height="44" rx="6" fill="#120c07" stroke="#c9a24a" stroke-width="2"/>')
    out.append('<g class="bh-px">' + sprite(HERO_TOP[:5], HERO_COL, 22, 20, 3) + "</g>")
    css.append(kf("bh-lv27", [(0, "opacity: 1"), (LVL_UP, "opacity: 1"), (LVL_UP + 0.01, "opacity: 0")]))
    css.append(kf("bh-lv28", [(0, "opacity: 0"), (LVL_UP, "opacity: 0"), (LVL_UP + 0.01, "opacity: 1")]))
    out.append('<text x="68" y="27" font-size="13" font-weight="700" fill="#f1e6cf" class="bh-hud">Doan</text>')
    out.append('<text x="112" y="27" font-size="11" fill="#ffd100" class="bh-hud" style="animation:bh-lv27 12s step-end infinite">Lv 27</text>')
    out.append('<text x="112" y="27" font-size="11" fill="#ffd100" class="bh-hud" style="opacity:0;animation:bh-lv28 12s step-end infinite">Lv 28</text>')
    # HP + mana
    out.append('<rect x="68" y="34" width="120" height="8" rx="2" fill="#3f0d0d"/>')
    css.append(kf("bh-hp", [(0, "transform: scaleX(1)"), (BOSS_ATK, "transform: scaleX(1)"), (BOSS_ATK + 0.05, "transform: scaleX(.78)"),
                            (LVL_UP, "transform: scaleX(.78)"), (LVL_UP + 0.3, "transform: scaleX(1)")]))
    out.append('<rect x="68" y="34" width="120" height="8" rx="2" fill="#22c55e" style="transform-origin:68px 0;animation:bh-hp 12s ease-out infinite"/>')
    out.append('<rect x="68" y="46" width="120" height="6" rx="2" fill="#172554"/>')
    css.append(kf("bh-mp", [(0, "transform: scaleX(1)"), (CAST, "transform: scaleX(1)"), (CAST + 0.05, "transform: scaleX(.55)"),
                            (LVL_UP, "transform: scaleX(.7)"), (LVL_UP + 0.3, "transform: scaleX(1)")]))
    out.append('<rect x="68" y="46" width="120" height="6" rx="2" fill="#3b82f6" style="transform-origin:68px 0;animation:bh-mp 12s ease-out infinite"/>')
    # boss bar
    bx, bw = W / 2 - 150, 300
    css.append(kf("bh-bossbar", [(0, "opacity: 0"), (BOSS_IN + 0.3, "opacity: 0"), (BOSS_IN + 0.6, "opacity: 1"),
                                 (BOSS_DIE + 0.3, "opacity: 1"), (BOSS_DIE + 0.6, "opacity: 0")]))
    fill = [(0, "transform: scaleX(1)")]
    for i, t in enumerate(BOSS_HITS):
        fill += [(t, f"transform: scaleX({1 - i * .3:.2f})"), (t + 0.06, f"transform: scaleX({max(0, .7 - i * .3):.2f})")]
    css.append(kf("bh-bossfill", fill))
    out.append(f'<g style="opacity:0;animation:bh-bossbar 12s linear infinite">'
               f'<text x="{W / 2}" y="26" text-anchor="middle" font-size="12" font-weight="700" fill="#ffd100" class="bh-hud">LEGACY CODE  ·  Elite</text>'
               f'<rect x="{bx}" y="32" width="{bw}" height="10" rx="2" fill="#2a0a0a" stroke="#c9a24a"/>'
               f'<rect x="{bx + 1}" y="33" width="{bw - 2}" height="8" rx="1" fill="#dc2626" style="transform-origin:{bx + 1}px 0;animation:bh-bossfill 12s linear infinite"/></g>')
    # kill counter (real number + this loop's kills)
    kill_times = [A_HIT, B_HIT, M_HIT, BOSS_DIE]
    for i in range(5):
        a = 0 if i == 0 else kill_times[i - 1]
        b = kill_times[i] if i < 4 else C
        name = f"bh-k{i}"
        stops = [(0, "opacity: %d" % (1 if i == 0 else 0))]
        if i:
            stops += [(a, "opacity: 0"), (a + 0.01, "opacity: 1")]
        if i < 4:
            stops += [(b, "opacity: 1"), (b + 0.01, "opacity: 0")]
        css.append(kf(name, stops))
        out.append(f'<text x="{W - 20}" y="31" text-anchor="end" font-size="13" font-weight="700" fill="#f1e6cf" class="bh-hud" '
                   f'style="opacity:{1 if i == 0 else 0};animation:{name} 12s step-end infinite">Bugs slain: <tspan fill="#ffd100">{kills + i:,}</tspan></text>')
    out.append(f'<text x="{W - 20}" y="48" text-anchor="end" font-size="10" fill="#9a8a6a" class="bh-hud">endless mode · no frameworks equipped</text>')
    # XP bar along the bottom
    xp = [(0, "transform: scaleX(.05)"), (A_HIT, "transform: scaleX(.05)"), (A_HIT + .2, "transform: scaleX(.18)"),
          (B_HIT, "transform: scaleX(.18)"), (B_HIT + .2, "transform: scaleX(.32)"), (M_HIT, "transform: scaleX(.32)"),
          (M_HIT + .2, "transform: scaleX(.48)"), (BOSS_DIE + .3, "transform: scaleX(.48)"), (LVL_UP, "transform: scaleX(1)"),
          (LVL_UP + 0.5, "transform: scaleX(1)"), (LVL_UP + 0.6, "transform: scaleX(.02)"), (C, "transform: scaleX(.05)")]
    css.append(kf("bh-xp", xp))
    out.append(f'<rect x="16" y="{H - 18}" width="{W - 32}" height="8" rx="2" fill="#140d24" stroke="#5a4520"/>')
    out.append(f'<rect x="17" y="{H - 17}" width="{W - 34}" height="6" rx="1" fill="url(#bh-xpg)" style="transform-origin:17px 0;animation:bh-xp 12s ease-out infinite"/>')
    out.append(f'<text x="22" y="{H - 22}" font-size="9" fill="#a78bfa" class="bh-hud">XP</text>')
    return "".join(out)


def read_kills():
    try:
        s = open("profile-3d-contrib/legendary-item.svg", encoding="utf-8").read()
        return int(re.search(r"Item Level ([\d,]+)", s).group(1).replace(",", ""))
    except Exception:
        return 2000


def render():
    kills = read_kills()
    sc = scenery()
    gr = ground_layer()
    a, a_pos = walker("bugA", BUG, {"a": "#a3a3a3", "k": "#111", "K": "#22c55e", "r": "#fde047", "l": "#525252"}, A_SPAWN, A_HIT, label="NullPointer")
    b, b_pos = walker("bugB", BUG, {"a": "#a3a3a3", "k": "#111", "K": "#a855f7", "r": "#fde047", "l": "#525252"}, B_SPAWN, B_HIT, label="off-by-one")
    m, m_pos = moth()
    fb = fireball(m_pos)
    bs, boss_pos = boss()
    hero_svg = hero()
    hy = GROUND - 30
    fx = []
    fx.append(burst(A_HIT, a_pos, hy, ["#22c55e", "#86efac", "#fde047"]))
    fx.append(popup(A_HIT, a_pos, hy - 40, "-42", "#ffd100"))
    fx.append(popup(A_HIT + 0.3, a_pos + 30, hy - 24, "+15 XP", "#a78bfa", size=12))
    fx.append(burst(B_HIT, b_pos, hy, ["#a855f7", "#d8b4fe", "#fde047"]))
    fx.append(popup(B_HIT, b_pos, hy - 40, "-1", "#ffd100"))
    fx.append(popup(B_HIT + 0.25, b_pos + 26, hy - 64, "off by one!", "#f1e6cf", size=11))
    fx.append(burst(M_HIT, m_pos[0], m_pos[1], ["#fb923c", "#fde047", "#67e8f9"], n=16, spread=70, up=40))
    fx.append(popup(M_HIT, m_pos[0], m_pos[1] - 26, "-120  BURN", "#ff8000", size=16))
    bx, byy = boss_pos
    for i, t in enumerate(BOSS_HITS):
        crit = i == len(BOSS_HITS) - 1
        fx.append(burst(t, bx - 30, byy, ["#c084fc", "#fde047", "#fff"], n=8 if not crit else 16, spread=50))
        fx.append(popup(t, bx - 10 + i * 14, byy - 50 - i * 6, "CRIT -999" if crit else f"-{180 + i * 70}", "#ff8000" if crit else "#ffd100", size=26 if crit else 18))
        if i:
            fx.append(popup(t + 0.05, HERO_X + 24, GROUND - 92, f"x{i + 1} COMBO", "#2dd4bf", size=15, dur=0.6))
    fx.append(popup(BOSS_ATK + 0.02, HERO_X + 24, GROUND - 70, "-12", "#ef4444", size=16))
    fx.append(boom(BOSS_DIE + 0.05, bx - 10, byy, "#ffd100", 80))
    fx.append(burst(BOSS_DIE + 0.05, bx - 10, byy, ["#581c87", "#c084fc", "#ffd100", "#fff"], n=26, spread=110, up=90))
    fx.append(coins(BOSS_DIE + 0.1, bx - 10, byy - 10))
    fx.append(popup(BOSS_DIE + 0.25, bx - 10, byy - 70, "+250 XP", "#a78bfa", size=18, dur=1.1))
    lvl = level_up()

    # screen shake on the crit and the boss death
    shake = [(0, "transform: none")]
    for t in (BOSS_HITS[-1], BOSS_DIE + 0.05):
        shake += [(t, "transform: none"), (t + 0.03, "transform: translate(5px, -3px)"), (t + 0.06, "transform: translate(-6px, 2px)"),
                  (t + 0.09, "transform: translate(4px, 3px)"), (t + 0.12, "transform: translate(-3px, -2px)"), (t + 0.16, "transform: none")]
    css.append(kf("bh-shake", shake))
    hud_svg = hud(kills)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Animated pixel hero fighting bugs, a flying memory leak and the Legacy Code boss, then leveling up, in an endless loop">
<title>Bug Hunt</title>
<style>
text {{ font-family: "Friz Quadrata TT", Verdana, "Segoe UI", system-ui, sans-serif; }}
.bh-px rect {{ shape-rendering: crispEdges; }}
.bh-tag {{ font: 10px ui-monospace, Menlo, Consolas, monospace; fill: #f1e6cf; stroke: #000; stroke-width: 2.5px; paint-order: stroke; }}
.bh-pop, .bh-hud {{ stroke: #000; stroke-width: 3px; paint-order: stroke; }}
.bh-pop {{ transform-box: view-box; }}
.bh-world {{ animation: bh-shake 12s linear infinite; }}
.bh-crawl {{ animation: bh-crawl .25s steps(2) infinite; }}
@keyframes bh-crawl {{ 50% {{ transform: translateY(-2px); }} }}
{chr(10).join(css)}
@media (prefers-reduced-motion: reduce) {{ [class^="bh"], [style*="animation"] {{ animation: none !important; }} }}
</style>
<defs>
  <linearGradient id="bh-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c0a1f"/><stop offset=".6" stop-color="#2a1340"/><stop offset="1" stop-color="#4a1a22"/></linearGradient>
  <linearGradient id="bh-fog" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f97316" stop-opacity="0"/><stop offset="1" stop-color="#f97316" stop-opacity=".12"/></linearGradient>
  <linearGradient id="bh-beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffd100" stop-opacity="0"/><stop offset=".5" stop-color="#fff7ae" stop-opacity=".9"/><stop offset="1" stop-color="#ffd100" stop-opacity="0"/></linearGradient>
  <linearGradient id="bh-xpg" x1="0" x2="1"><stop offset="0" stop-color="#6d28d9"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
  <radialGradient id="bh-fire"><stop offset="0" stop-color="#fff7ae"/><stop offset=".45" stop-color="#fb923c"/><stop offset="1" stop-color="#dc2626" stop-opacity="0"/></radialGradient>
  <clipPath id="bh-clip"><rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="6"/></clipPath>
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="10" fill="#120c07" stroke="#c9a24a" stroke-width="3"/>
<g clip-path="url(#bh-clip)">
  <g class="bh-world">
    {sc}
    <rect x="0" y="{GROUND}" width="{W}" height="{H - GROUND}" fill="#120c07"/>
    {gr}
    {a}{b}{m}{bs}
    {hero_svg}
    {fb}
    {"".join(fx)}
  </g>
  {lvl}
  {hud_svg}
</g>
</svg>
"""


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    svg = render()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", OUT, f"({len(svg) // 1024} KB)")

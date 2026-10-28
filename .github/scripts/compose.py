"""Stitches all profile cards into one continuous game window
(profile-3d-contrib/profile-window.svg), so GitHub's page background never
shows between panels in light or dark mode.

Run after the card generators: python3 .github/scripts/compose.py
"""
import re

DIR = "profile-3d-contrib"
PARTS = ["legendary-item", "battle", "achievements", "quest-log", "action-bar"]
W, PAD, GAP, TOP = 840, 34, 30, 182
INNER = W - 2 * PAD


def embed(name, y):
    src = open(f"{DIR}/{name}.svg", encoding="utf-8").read()
    src = re.sub(r"<\?xml[^>]*\?>", "", src).strip()
    root = re.match(r"<svg\b[^>]*>", src).group(0)
    vb = re.search(r'viewBox="([^"]+)"', root).group(1)
    _, _, vw, vh = (float(v) for v in vb.split())
    h = INNER * vh / vw
    body = src[len(root):].rsplit("</svg>", 1)[0]
    frame = ""
    if name == "profile-ember":  # the 3D graph has no frame of its own
        frame = f'<rect x="{PAD}" y="{y:.1f}" width="{INNER}" height="{h:.1f}" rx="10" fill="none" stroke="#c9a24a" stroke-width="3"/>'
    return f'<svg x="{PAD}" y="{y:.1f}" width="{INNER}" height="{h:.1f}" viewBox="{vb}">{body}</svg>{frame}', h


def stars():
    import random
    r = random.Random(7)
    return "".join(
        f'<circle class="bg-star" cx="{r.uniform(10, W - 10):.0f}" cy="{r.uniform(10, 110):.0f}" r="{r.uniform(.6, 1.6):.1f}" fill="#fff" style="animation-delay:{r.uniform(0, 3):.1f}s"/>'
        for _ in range(38)
    )


def embers(H):
    """Embers drifting up through the margins and gaps between panels."""
    import random
    r = random.Random(11)
    out = []
    for _ in range(46):
        x = r.choice([r.uniform(8, PAD - 6), r.uniform(W - PAD + 6, W - 8), r.uniform(PAD, W - PAD)])
        y = r.uniform(240, H - 20)
        out.append(
            f'<circle class="bg-ember" cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(1, 2.4):.1f}" fill="{r.choice(["#f97316", "#fbbf24", "#fb923c"])}" '
            f'style="animation-duration:{r.uniform(5, 10):.1f}s;animation-delay:-{r.uniform(0, 10):.1f}s"/>'
        )
    return "".join(out)


def main():
    pieces, y = [], TOP
    for name in PARTS:
        svg, h = embed(name, y)
        pieces.append(svg)
        y += h + GAP
    H = y - GAP + PAD + 40
    out = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="Doan Idriz: legendary item card, bug hunt animation, achievements, quest log and action bar">
<title>Doan Idriz, Forger of Agents</title>
<style>
.bg-star {{ animation: bg-twinkle 3s ease-in-out infinite; }}
@keyframes bg-twinkle {{ 50% {{ opacity: .15; }} }}
.bg-ember {{ animation: bg-rise linear infinite; }}
@keyframes bg-rise {{ from {{ transform: translateY(0); opacity: 0; }} 10% {{ opacity: .9; }} 85% {{ opacity: .6; }} to {{ transform: translateY(-260px); opacity: 0; }} }}
.bg-win {{ animation: bg-flick 5s steps(1) infinite; }}
@keyframes bg-flick {{ 40% {{ fill: #2a1d33; }} 70% {{ fill: #fbbf24; }} }}
@media (prefers-reduced-motion: reduce) {{ .bg-star, .bg-ember, .bg-win {{ animation: none; }} }}
</style>
<defs>
  <linearGradient id="bg-sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0a0820"/><stop offset="{120 / H:.3f}" stop-color="#2a1340"/><stop offset="{170 / H:.3f}" stop-color="#4a1a22"/>
    <stop offset="{260 / H:.3f}" stop-color="#1c0f0a"/><stop offset=".6" stop-color="#120c07"/><stop offset="1" stop-color="#2a0f08"/>
  </linearGradient>
  <pattern id="bg-runes" width="28" height="28" patternUnits="userSpaceOnUse">
    <path d="M14 3 L25 14 L14 25 L3 14Z" fill="none" stroke="#c9a24a" stroke-opacity=".06"/>
    <circle cx="14" cy="14" r="1.2" fill="#c9a24a" fill-opacity=".08"/>
  </pattern>
  <radialGradient id="bg-glow" cx=".5" cy="1" r=".7"><stop offset="0" stop-color="#f97316" stop-opacity=".22"/><stop offset="1" stop-color="#f97316" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H:.0f}" rx="14" fill="url(#bg-sky)"/>
<rect y="200" width="{W}" height="{H - 200:.0f}" fill="url(#bg-runes)"/>
<rect y="{H - 420:.0f}" width="{W}" height="420" fill="url(#bg-glow)"/>
{stars()}
<circle cx="700" cy="52" r="24" fill="#fde68a"/><circle cx="711" cy="45" r="22" fill="#1d0f33" opacity=".96"/>
<path d="M0 150 Q70 92 150 132 Q220 80 300 126 Q370 70 450 122 Q540 86 610 128 Q690 94 760 126 Q800 112 840 120 V170 H0Z" fill="#170d1e"/>
<g fill="#22142c"><rect x="300" y="128" width="240" height="42"/><polygon points="55,150 95,122 135,150"/><rect x="60" y="148" width="70" height="22"/><polygon points="615,148 660,120 705,148"/><rect x="620" y="146" width="80" height="24"/></g>
<g fill="#120a18">{"".join(f'<rect x="{316 + i * 30}" y="138" width="18" height="24" rx="9"/>' for i in range(8))}</g>
<g fill="#fbbf24"><rect x="76" y="154" width="9" height="10" class="bg-win"/><rect x="104" y="154" width="9" height="10"/><rect x="640" y="152" width="9" height="10"/><rect x="668" y="152" width="9" height="10" class="bg-win" style="animation-delay:2s"/></g>
<text x="420" y="58" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="13" letter-spacing="6" fill="#c9a24a" fill-opacity=".85">REALM OF PLOVDIV</text>
<rect x="6" y="6" width="{W - 12}" height="{H - 12:.0f}" rx="10" fill="none" stroke="#c9a24a" stroke-opacity=".55" stroke-width="2"/>
<g fill="#c9a24a" fill-opacity=".7"><path d="M6 6 l26 0 l-26 26z"/><path d="M{W - 6} 6 l-26 0 l26 26z"/><path d="M6 {H - 6:.0f} l26 0 l-26 -26z"/><path d="M{W - 6} {H - 6:.0f} l-26 0 l26 -26z"/></g>
{embers(H)}
{chr(10).join(pieces)}
</svg>
"""
    with open(f"{DIR}/profile-window.svg", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote profile-window.svg ({W}x{H:.0f})")


if __name__ == "__main__":
    main()

"""Stitches all profile cards into one continuous game window
(profile-3d-contrib/profile-window.svg), so GitHub's page background never
shows between panels in light or dark mode.

Run after the card generators: python3 .github/scripts/compose.py
"""
import re

DIR = "profile-3d-contrib"
PARTS = ["legendary-item", "achievements", "quest-log", "action-bar", "profile-ember"]
W, PAD, GAP = 840, 20, 18
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


def main():
    pieces, y = [], PAD
    for name in PARTS:
        svg, h = embed(name, y)
        pieces.append(svg)
        y += h + GAP
    H = y - GAP + PAD
    out = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="Doan Idriz: legendary item card, achievements, quest log, action bar and 3D contribution graph">
<title>Doan Idriz, Forger of Agents</title>
<defs>
  <linearGradient id="win" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#140f09"/><stop offset=".5" stop-color="#0b0805"/><stop offset="1" stop-color="#140f09"/></linearGradient>
</defs>
<rect width="{W}" height="{H:.0f}" rx="14" fill="url(#win)"/>
{chr(10).join(pieces)}
</svg>
"""
    with open(f"{DIR}/profile-window.svg", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote profile-window.svg ({W}x{H:.0f})")


if __name__ == "__main__":
    main()

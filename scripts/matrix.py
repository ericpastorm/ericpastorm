#!/usr/bin/env python3
"""Generate matrix.svg: cmatrix-style rain, white on pure black.

Pure CSS animation, no scripts, so GitHub renders it inside an <img>.
Run from the repo root:  python3 scripts/matrix.py > matrix.svg
"""
import random
from html import escape

random.seed(1999)

W, H = 1000, 340
TAIL = "#d4d4d4"
HEAD = "#ffffff"
# cmatrix default charset is plain ASCII, so it renders with any monospace font
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@#$%&*+-=/\\|<>?!:;{}[]()^~"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"

# depth layers: far columns are small, dim, slow and slightly out of focus
LAYERS = {
    "far": dict(size=11, lh=13, dur=(8, 13), weight=0.45),
    "mid": dict(size=14, lh=16, dur=(5, 8), weight=0.35),
    "near": dict(size=17, lh=19, dur=(3, 5), weight=0.20),
}
MAXLEN = 22
TRAVEL = H + MAXLEN * LAYERS["near"]["lh"] + 40  # head runs until its whole tail has left


def stream(x, layer):
    p = LAYERS[layer]
    n = random.randint(6, MAXLEN)
    chars = escape("".join(random.choice(CHARS) for _ in range(n)), quote=False)
    xs = " ".join("0" * n)
    ys = " ".join(str(-(n - i) * p["lh"]) for i in range(n))
    dur = random.uniform(*p["dur"])
    delay = -random.uniform(0, dur)
    if layer == "far":
        heads = f'<text class="h">{escape(random.choice(CHARS), quote=False)}</text>'
    else:
        # three head glyphs take turns, so the leading character keeps mutating
        f = random.uniform(0.3, 0.7)
        heads = "".join(
            f'<text class="h c" style="animation-duration:{f:.2f}s;animation-delay:{-f * k / 3:.2f}s">'
            f"{escape(random.choice(CHARS), quote=False)}</text>"
            for k in range(3)
        )
    return (
        f'<g transform="translate({x:.1f} 0)">'
        f'<g class="s" style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s">'
        f'<text class="t" x="{xs}" y="{ys}">{chars}</text>{heads}</g></g>'
    )


def rain():
    groups = {name: [] for name in LAYERS}
    names, weights = list(LAYERS), [p["weight"] for p in LAYERS.values()]
    for x in range(6, W, 13):
        for _ in range(2 if random.random() < 0.35 else 1):
            layer = random.choices(names, weights)[0]
            groups[layer].append(stream(x + random.uniform(-2, 2), layer))
    return "\n".join(f'<g class="{name}">{"".join(items)}</g>' for name, items in groups.items())


def main():
    style = f"""
text{{font-family:{FONT};text-anchor:middle}}
.s{{animation:fall linear infinite}}
@keyframes fall{{from{{transform:translateY(-20px)}}to{{transform:translateY({TRAVEL}px)}}}}
.t{{fill:url(#tail)}}
.h{{fill:{HEAD}}}
.c{{animation:cyc .5s step-end infinite}}
@keyframes cyc{{0%{{opacity:1}}33.3%{{opacity:0}}100%{{opacity:0}}}}
.far{{font-size:11px;opacity:.3;filter:url(#dof)}}
.mid{{font-size:14px;opacity:.6}}
.near{{font-size:17px;filter:url(#glow)}}
"""

    print(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="matrix rain">
<style>{style}</style>
<defs>
<linearGradient id="tail" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{TAIL}" stop-opacity="0"/>
<stop offset=".6" stop-color="{TAIL}" stop-opacity=".5"/>
<stop offset="1" stop-color="{TAIL}" stop-opacity=".95"/>
</linearGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".72">
<stop offset=".45" stop-color="#000" stop-opacity="0"/>
<stop offset="1" stop-color="#000" stop-opacity=".92"/>
</radialGradient>
<filter id="glow" x="-50%" y="-10%" width="200%" height="120%">
<feGaussianBlur stdDeviation="2.2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="dof"><feGaussianBlur stdDeviation=".6"/></filter>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="10"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="#000"/>
<g class="rain">
{rain()}
</g>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</g>
</svg>""")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate matrix.svg: cmatrix-style rain around a vantablack void.

Pure CSS animation, no scripts, so GitHub renders it inside an <img>.
Run from the repo root:  python3 scripts/matrix.py > matrix.svg
"""
import random
from html import escape

random.seed(1999)

W, H = 1000, 340
GREEN = "#00ff41"
HEAD = "#e6ffe9"
# cmatrix default charset is plain ASCII, so it renders with any monospace font
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@#$%&*+-=/\\|<>?!:;{}[]()^~"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"

NAME = "ERIC PASTOR"
SUB = "software engineer  //  basalt works  //  tarragona"
LINES = [  # (text, seconds held after typing)
    ("> wake up, neo...", 1.8),
    ("> the matrix has you...", 1.8),
    ("> follow the white rabbit.", 1.8),
    ("> knock, knock.", 2.6),
]

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


def typed_lines(x0, y, adv, start):
    """Each line types in, holds, clears; the cycle loops forever."""
    rate, gap = 0.08, 0.4
    spans, t = [], 0.0
    for text, hold in LINES:
        typing = len(text) * rate
        spans.append((t, t + typing, t + typing + hold))
        t += typing + hold + gap
    total = t

    css, svg = [], []
    for i, ((text, _), (s, e, out)) in enumerate(zip(LINES, spans)):
        n = len(text)
        w = n * adv
        S, E, O = (round(v / total * 100, 3) for v in (s, e, out))
        css.append(
            f"@keyframes v{i}{{0%{{opacity:0}}{S}%{{opacity:1}}{O}%{{opacity:0}}100%{{opacity:0}}}}"
            f"@keyframes k{i}{{0%,{S}%{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{E}%,100%{{transform:translateX({w}px)}}}}"
            f".l{i}{{animation:v{i} {total:.2f}s step-end {start}s infinite both}}"
            f".l{i} .cv{{animation:k{i} {total:.2f}s {start}s infinite both}}"
        )
        svg.append(
            f'<g class="l{i}">'
            f'<text class="ty" x="{x0}" y="{y}" textLength="{w}" lengthAdjust="spacing" xml:space="preserve">{escape(text, quote=False)}</text>'
            f'<g class="cv"><rect x="{x0}" y="{y - 14}" width="{w + adv + 8}" height="20" fill="#000"/>'
            f'<rect class="cur" x="{x0 + 1}" y="{y - 12}" width="{adv - 1}" height="16" fill="{GREEN}"/></g>'
            f"</g>"
        )
    return "".join(css), "".join(svg)


def main():
    cx = W / 2
    adv = 9  # 0.6em advance of a 15px monospace glyph
    x0 = cx - max(len(t) for t, _ in LINES) * adv / 2
    line_css, line_svg = typed_lines(x0, 217, adv, start=2.2)

    style = f"""
text{{font-family:{FONT}}}
.rain text{{text-anchor:middle}}
.s{{animation:fall linear infinite}}
@keyframes fall{{from{{transform:translateY(-20px)}}to{{transform:translateY({TRAVEL}px)}}}}
.t{{fill:url(#tail)}}
.h{{fill:{HEAD}}}
.c{{animation:cyc .5s step-end infinite}}
@keyframes cyc{{0%{{opacity:1}}33.3%{{opacity:0}}100%{{opacity:0}}}}
.far{{font-size:11px;opacity:.3;filter:url(#dof)}}
.mid{{font-size:14px;opacity:.6}}
.near{{font-size:17px;filter:url(#glow)}}
.nm{{font-size:40px;font-weight:700;letter-spacing:10px;fill:#f2fff4;text-anchor:middle;filter:url(#nglow);animation:on 1.8s .3s step-end both}}
@keyframes on{{0%{{opacity:0}}12%{{opacity:.7}}16%{{opacity:0}}24%{{opacity:1}}28%{{opacity:.15}}40%{{opacity:1}}100%{{opacity:1}}}}
.sub{{font-size:13px;letter-spacing:1.5px;fill:{GREEN};text-anchor:middle;animation:fade 1.2s 1.3s ease-out both}}
@keyframes fade{{from{{opacity:0}}to{{opacity:.72}}}}
.ty{{font-size:15px;fill:{GREEN}}}
.cur{{animation:blink 1s step-end infinite}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
{line_css}
"""

    print(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{NAME.lower()}: software engineer at basalt works">
<style>{style}</style>
<defs>
<linearGradient id="tail" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>
<stop offset=".6" stop-color="{GREEN}" stop-opacity=".55"/>
<stop offset="1" stop-color="{GREEN}" stop-opacity="1"/>
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
<filter id="void" x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="nglow" x="-10%" y="-50%" width="120%" height="200%">
<feGaussianBlur in="SourceAlpha" stdDeviation="6" result="b"/>
<feFlood flood-color="{GREEN}" flood-opacity=".5"/>
<feComposite in2="b" operator="in" result="g"/>
<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="10"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="#000"/>
<g class="rain">
{rain()}
</g>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<rect x="217" y="76" width="566" height="188" fill="#000" filter="url(#void)"/>
<text class="nm" x="{cx + 5}" y="149">{NAME}</text>
<text class="sub" x="{cx}" y="179" xml:space="preserve">{SUB}</text>
{line_svg}
</g>
</svg>""")


if __name__ == "__main__":
    main()

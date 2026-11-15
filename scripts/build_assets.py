#!/usr/bin/env python3
"""Generates the animated SVGs used by README.md.

    python3 scripts/build_assets.py

GitHub strips CSS/JS from READMEs, but an SVG loaded through <img> keeps its
own <style> and SMIL animations. Everything here is self-contained: no
external fonts, scripts or images. Text that is typed/clipped uses
`textLength` so it lines up the same on every OS font.
"""
import random
import re
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'SF Mono','Fira Code','JetBrains Mono',Menlo,Consolas,'Liberation Mono',monospace"

SKY, NAVY, CARET = "#54c5f8", "#0553b1", "#2f81f7"
GH = dict(bg="#0d1117", dim="#010409", line="#30363d", fg="#e6edf3", mute="#8b949e", num="#6e7681",
          btn="#21262d")

# ---- content you are most likely to edit -----------------------------------
GREETING = "Hey, I'm"
NAME = "Saram Rabbi"
ROLES = [
    "High-Impact Flutter Developer",
    "Real-Time Communication Expert",
    "Automation & Python Explorer",
    "Always Learning & Building",
    "Builder of robust cross-platform apps",
]
# Typed into the editor in the About section; the phone preview is built from it.
# First entry is the name, second the role; strings become rows, lists become chips.
PROFILE = [
    ("name", "Saram Rabbi"),
    ("role", "Flutter Developer"),
    ("experience", "2+ years, iOS & Android"),
    ("realtime", ["WebRTC", "SIP", "WebSocket"]),
    ("architecture", ["MVVM", "Clean Architecture", "Provider"]),
    ("alsoInto", ["Python", "Selenium", "AR"]),
]
# -----------------------------------------------------------------------------


def n(x):
    """Compact number formatting."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def text_w(s, size):
    """Rough width of bold sans text, so `textLength` stays close to natural."""
    em = 0
    for ch in s:
        if ch in "iIlj.,:;'|!":
            em += .27
        elif ch in "ftr":
            em += .37
        elif ch == " ":
            em += .24
        elif ch in "mwMW":
            em += .85
        elif ch.isupper() or ch == "&":
            em += .69
        else:
            em += .56
    return round(em * size * 1.03)


def svg(w, h, title, css, defs, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{css}</style><defs>{defs}</defs>{body}</svg>\n"
    )


def discrete(attr, pts, total):
    kt = ";".join(f"{t / total:.5f}" for t, _ in pts)
    vals = ";".join(n(v) for _, v in pts)
    return (
        f'<animate attributeName="{attr}" calcMode="discrete" dur="{total}s" repeatCount="indefinite" '
        f'keyTimes="{kt}" values="{vals}"/>'
    )


# =============================================================================
# HERO: name, typed role line, Flutter mark. Flat, same palette as the editor.
# =============================================================================
FLUTTER = ("M14.314 0L2.3 12 6 15.7 21.684.013h-7.357zm.014 11.072L7.857 17.53l6.47 6.47H21.7"
           "l-6.46-6.468 6.46-6.46h-7.37z")
FLUTTER_SHADE = "M11.55 21.22 15.24 17.532 21.7 24H14.327z"


def hero():
    W, H = 900, 250
    X, Y, FS, CW = 52, 194, 22, 13.2
    g = GH
    rnd = random.Random(8)

    # The first role is already on screen at t=0 (so a paused or static render
    # still reads correctly); then: hold, delete, type the next one, repeat.
    k = len(ROLES)
    tracks = [[(0.0, len(ROLES[0]) * CW + 1)]] + [[(0.0, 0.0)] for _ in ROLES[1:]]
    cur, t = [(0.0, X + len(ROLES[0]) * CW)], 0.0
    for i in range(k):
        line, nxt = ROLES[i], ROLES[(i + 1) % k]
        t += 1.9
        for c in range(len(line) - 1, -1, -1):
            t += .024
            tracks[i].append((t, c * CW + 1 if c else 0))
            cur.append((t, X + c * CW))
        t += .45
        for c, ch in enumerate(nxt, 1):
            t += rnd.uniform(.04, .085) + (.09 if ch == " " and rnd.random() < .4 else 0)
            tracks[(i + 1) % k].append((t, c * CW + 1))
            cur.append((t, X + c * CW))
    T = round(t + .5, 2)                     # the last keystroke must land before the loop point
    clips = roles = ""
    for i, (line, pts) in enumerate(zip(ROLES, tracks)):
        clips += (f'<clipPath id="t{i}"><rect x="{X}" y="{Y - FS}" width="{n(pts[0][1])}" height="{FS + 12}">'
                  f'{discrete("width", pts, T)}</rect></clipPath>')
        roles += (f'<text class="role" clip-path="url(#t{i})" x="{X}" y="{Y}" '
                  f'textLength="{n(len(line) * CW)}">{escape(line)}</text>')
    caret = (f'<rect class="cur" x="{n(cur[0][1])}" y="{Y - FS + 3}" width="2.2" height="{FS + 3}" rx="1.1" '
             f'transform="translate(3 0)">{discrete("x", cur, T)}</rect>')

    S = 5.2
    css = f"""
.hi{{font:400 20px {SANS};fill:{g["mute"]}}}.nm{{font:800 72px {SANS};fill:{g["fg"]}}}
.role{{font:400 {FS}px {MONO};fill:{g["fg"]}}}
.cur{{fill:{CARET};animation:bl 1.06s steps(1) infinite}}@keyframes bl{{50%{{opacity:0}}}}
"""
    defs = (
        f'<clipPath id="fr"><rect width="{W}" height="{H}" rx="10"/></clipPath>'
        f'<pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="{g["line"]}"/></pattern>'
        f'<linearGradient id="fade" x1="0" x2="1"><stop offset=".5" stop-color="#000"/><stop offset=".85" stop-color="#fff"/></linearGradient>'
        f'<mask id="right" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>'
        + clips
    )
    body = (
        f'<g clip-path="url(#fr)"><rect width="{W}" height="{H}" fill="{g["bg"]}"/>'
        f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#right)"/>'
        f'<text class="hi" x="{X}" y="74">{escape(GREETING)}</text>'
        f'<text class="nm" x="{X - 4}" y="146">{escape(NAME)}</text>'
        f"{roles}{caret}"
        f'<g transform="translate({n(770 - 12 * S)} {n(H / 2 - 12 * S)}) scale({S})">'
        f'<path d="{FLUTTER}" fill="{SKY}"/><path d="{FLUTTER_SHADE}" fill="{NAVY}"/></g></g>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="9.5" fill="none" stroke="{g["line"]}"/>'
    )
    return svg(W, H, f"{GREETING} {NAME} - " + ", ".join(ROLES), css, defs, body)


# =============================================================================
# ABOUT: an editor window (GitHub Dark colours) where the profile gets typed,
# and a phone that hot-reloads each field as its line is finished.
# =============================================================================

SCAFFOLD = [
    [("k", "import "), ("s", "'package:flutter/material.dart'"), ("p", ";")],
    [],
    [("k", "class "), ("o", "AboutMe "), ("k", "extends "), ("b", "StatelessWidget "), ("p", "{")],
    [("k", "  const "), ("o", "AboutMe"), ("p", "({"), ("b", "super"), ("p", ".key});")],
    [],
    [("k", "  @override")],
    [("b", "  Widget "), ("f", "build"), ("p", "("), ("b", "BuildContext "), ("p", "context) {")],
    [("k", "    return const "), ("b", "ProfileCard"), ("p", "(")],
]
CLOSING = ["    );", "  }", "}"]


def prop_tokens(key, val):
    toks = [("p", key + ": ")]
    if isinstance(val, str):
        toks.append(("s", f"'{val}'"))
    else:
        toks.append(("p", "["))
        for i, v in enumerate(val):
            if i:
                toks.append(("p", ", "))
            toks.append(("s", f"'{v}'"))
        toks.append(("p", "]"))
    return toks + [("p", ",")]


def about():
    W, H, SPLIT = 880, 460, 610
    X0, Y0, LH, CW, T = 58, 82, 20, 7.8, 34.0
    g = GH
    rnd = random.Random(4)
    first, nprops = len(SCAFFOLD), len(PROFILE)
    base = first + 1 + len(CLOSING)            # lines in the file before typing starts

    def code_line(toks, x, y, extra=""):
        k = sum(len(t) for _, t in toks)
        spans = "".join(f'<tspan class="{c}">{escape(t)}</tspan>' for c, t in toks)
        return (f'<text class="cd" xml:space="preserve" x="{n(x)}" y="{y}" textLength="{n(k * CW)}"{extra}>'
                f"{spans}</text>")

    static = "".join(code_line(toks, X0, Y0 + i * LH) for i, toks in enumerate(SCAFFOLD) if toks)

    # --- typing timeline: uneven keystrokes, a pause, Enter, next line ------
    xi = X0 + 6 * CW
    t = 1.4
    clips = props = ""
    cur_x, cur_y, enters, reveal = [(0.0, xi)], [(0.0, Y0 + first * LH)], [], []
    for i, (key, val) in enumerate(PROFILE):
        y = Y0 + (first + i) * LH
        if i:
            enters.append(t)
            cur_x.append((t, xi))
            cur_y.append((t, y))
            t += .3
        toks = prop_tokens(key, val)
        pts = [(0.0, 0.0)]
        for c, ch in enumerate("".join(tx for _, tx in toks), 1):
            t += rnd.uniform(.03, .075) + (.1 if ch in ", " and rnd.random() < .35 else 0)
            pts.append((t, c * CW + 1))
            cur_x.append((t, xi + c * CW))
        reveal.append(t + .4)
        t += .95
        clips += (f'<clipPath id="c{i}"><rect x="{n(xi)}" y="{y - 15}" width="0" height="{LH}">'
                  f'{discrete("width", pts, T)}</rect></clipPath>')
        props += code_line(toks, xi, y, f' clip-path="url(#c{i})"')

    shift = (f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" dur="{T}s" '
             f'repeatCount="indefinite" keyTimes="{";".join(f"{a / T:.5f}" for a in [0.0] + enters)}" '
             f'values="{";".join(f"0 {-(nprops - 1 - i) * LH}" for i in range(nprops))}"/>')
    closing = (f'<g transform="translate(0 {-(nprops - 1) * LH})">'
               + "".join(code_line([("p", c)], X0, Y0 + (first + nprops + j) * LH) for j, c in enumerate(CLOSING))
               + shift + "</g>")

    nums = ""
    for m in range(1, first + nprops + len(CLOSING) + 1):
        y = Y0 + (m - 1) * LH
        if m <= base:
            nums += f'<text class="ln" x="40" y="{y}" text-anchor="end">{m}</text>'
        else:
            nums += (f'<text class="ln" x="40" y="{y}" text-anchor="end" opacity="0">{m}<animate attributeName="opacity" '
                     f'calcMode="discrete" dur="{T}s" repeatCount="indefinite" keyTimes="0;{enters[m - base - 1] / T:.5f}" '
                     f'values="0;1"/></text>')

    y9 = Y0 + first * LH
    hilite = (f'<rect x="1" y="{y9 - 14.5}" width="{SPLIT - 1}" height="{LH}" fill="{g["num"]}" opacity=".12">'
              f'{discrete("y", [(a, b - 14.5) for a, b in cur_y], T)}</rect>')
    cursor = (f'<rect class="cur" x="{n(xi)}" y="{y9 - 13}" width="1.8" height="16" rx=".9">'
              f'{discrete("x", cur_x, T)}{discrete("y", [(a, b - 13) for a, b in cur_y], T)}</rect>')

    # --- phone: the ProfileCard, one field per finished line -----------------
    PW, PH, PY = 180, 356, 70
    PX = (SPLIT + W - PW) / 2
    left, right = PX + 20, PX + PW - 20
    els, rules, y = "", "", PY + 124
    for i, (key, val) in enumerate(PROFILE):
        if i == 0:
            ini = "".join(w[0] for w in val.split()[:2]).upper()
            el = (f'<circle cx="{n(left + 18)}" cy="{PY + 80}" r="18" fill="{SKY}"/>'
                  f'<text class="av" x="{n(left + 18)}" y="{PY + 84.5}" text-anchor="middle">{escape(ini)}</text>'
                  f'<text class="nm" x="{n(left + 46)}" y="{PY + 78}">{escape(val)}</text>')
        elif i == 1:
            el = f'<text class="rl" x="{n(left + 46)}" y="{PY + 92}">{escape(val)}</text>'
        else:
            label = re.sub(r"(?<!^)(?=[A-Z])", " ", key).upper()
            el = f'<text class="lb" x="{n(left)}" y="{y}">{escape(label)}</text>'
            if i == 2:
                el = f'<rect x="{n(left)}" y="{PY + 106}" width="{n(right - left)}" height="1" fill="{g["line"]}"/>' + el
            if isinstance(val, str):
                el += f'<text class="vl" x="{n(left)}" y="{y + 14}">{escape(val)}</text>'
                y += 36
            else:
                cx, top = left, y + 7
                for v in val:
                    tw = round(text_w(v, 8.5) * .93)
                    w = tw + 12
                    if cx + w > right + .5 and cx > left:
                        cx, top = left, top + 22
                    el += (f'<rect x="{n(cx)}" y="{top}" width="{w}" height="18" rx="6" fill="{g["bg"]}" stroke="{g["line"]}"/>'
                           f'<text class="cp" x="{n(cx + 6)}" y="{top + 12.2}" textLength="{tw}">{escape(v)}</text>')
                    cx += w + 5
                y = top + 22 + 16
        pct = reveal[i] / T * 100
        rules += (f"@keyframes r{i}{{0%,{pct:.2f}%{{opacity:0;transform:translateY(5px)}}"
                  f"{pct + .9:.2f}%,100%{{opacity:1;transform:none}}}}.r{i}{{animation-name:r{i}}}")
        els += f'<g class="r r{i}">{el}</g>'

    phone = (
        f'<rect x="{SPLIT}" y="37" width="{W - SPLIT}" height="{H - 59}" fill="{g["dim"]}"/>'
        f'<rect x="{SPLIT}" y="37" width="1" height="{H - 59}" fill="{g["line"]}"/>'
        f'<rect x="{n(PX)}" y="{PY}" width="{PW}" height="{PH}" rx="24" fill="{g["dim"]}" stroke="{g["line"]}" stroke-width="1.5"/>'
        f'<rect x="{n(PX + 6)}" y="{PY + 6}" width="{PW - 12}" height="{PH - 12}" rx="19" fill="#161b22"/>'
        f'<circle cx="{n(PX + PW / 2)}" cy="{PY + 17}" r="3.2" fill="{g["dim"]}"/>'
        f'<text class="tm" x="{n(left)}" y="{PY + 20}">9:41</text>'
        f'<rect x="{n(right - 16)}" y="{PY + 13}" width="16" height="8" rx="2.2" fill="none" stroke="{g["mute"]}"/>'
        f'<rect x="{n(right - 14.5)}" y="{PY + 14.5}" width="10" height="5" rx="1" fill="{g["mute"]}"/>'
        f'<text class="ab" x="{n(left)}" y="{PY + 48}">About</text>'
        f'<g class="dyn">{els}</g>'
        f'<rect x="{n(PX + PW / 2 - 24)}" y="{PY + PH - 16}" width="48" height="3" rx="1.5" fill="{g["num"]}"/>'
    )

    css = f"""
.cd{{font:400 13px {MONO}}}.ln{{font:400 12px {MONO};fill:{g["num"]}}}
.k{{fill:#ff7b72}}.s{{fill:#a5d6ff}}.b{{fill:#79c0ff}}.o{{fill:#ffa657}}.f{{fill:#d2a8ff}}.p{{fill:{g["fg"]}}}
.ui{{font:400 12px {SANS};fill:{g["fg"]}}}.mu{{fill:{g["mute"]}}}.sm{{font-size:11px}}
.cur{{fill:#2f81f7;animation:bl 1.06s steps(1) infinite}}@keyframes bl{{50%{{opacity:0}}}}
.dyn{{animation:dyn {T}s linear infinite}}@keyframes dyn{{0%,96%{{opacity:1}}98.5%,100%{{opacity:0}}}}
.r{{animation:{T}s linear infinite both}}
.tm{{font:600 8.5px {SANS};fill:{g["fg"]}}}.ab{{font:600 14px {SANS};fill:{g["fg"]}}}
.av{{font:700 12px {SANS};fill:{g["bg"]}}}.nm{{font:700 13px {SANS};fill:{g["fg"]}}}.rl{{font:400 9.5px {SANS};fill:{g["mute"]}}}
.lb{{font:600 7px {SANS};fill:{g["mute"]};letter-spacing:1.1px}}.vl{{font:400 10px {SANS};fill:{g["fg"]}}}
.cp{{font:500 8.5px {SANS};fill:{g["fg"]}}}
""" + rules
    defs = f'<clipPath id="fr"><rect width="{W}" height="{H}" rx="10"/></clipPath>' + clips
    body = (
        f'<g clip-path="url(#fr)"><rect width="{W}" height="{H}" fill="{g["bg"]}"/>'
        # tab bar
        f'<rect width="{W}" height="36" fill="{g["dim"]}"/><rect y="36" width="{W}" height="1" fill="{g["line"]}"/>'
        f'<circle cx="20" cy="18" r="5.5" fill="#ff5f57"/><circle cx="38" cy="18" r="5.5" fill="#febc2e"/><circle cx="56" cy="18" r="5.5" fill="#28c840"/>'
        f'<rect x="80" y="0" width="150" height="37" fill="{g["bg"]}"/><rect x="80" y="0" width="150" height="1.5" fill="#f78166"/>'
        f'<rect x="80" y="0" width="1" height="36" fill="{g["line"]}"/><rect x="230" y="0" width="1" height="36" fill="{g["line"]}"/>'
        f'<path transform="translate(93 12.5)" d="M0 6.2 6.2 0H11.5V5.3L5.3 11.5Z" fill="{SKY}"/>'
        f'<text class="ui" x="112" y="22.5">about_me.dart</text>'
        f'<path d="M210 14.5l7 7m0-7l-7 7" stroke="{g["mute"]}" stroke-width="1.1" stroke-linecap="round"/>'
        f'<circle cx="249" cy="18.5" r="4" fill="none" stroke="{g["mute"]}" stroke-width="1.3"/>'
        f'<text class="ui mu" x="262" y="22.5">pubspec.yaml</text>'
        # breadcrumbs
        f'<text class="ui mu sm" x="20" y="53">lib  ›  about_me.dart  ›  AboutMe  ›  build</text>'
        f"{hilite}{nums}{static}<g class=\"dyn\">{props}</g>{closing}{cursor}{phone}"
        # status bar
        f'<rect y="{H - 22}" width="{W}" height="22" fill="{g["bg"]}"/><rect y="{H - 22}" width="{W}" height="1" fill="{g["line"]}"/>'
        f'<g transform="translate(14 {H - 17.5})" fill="none" stroke="{g["mute"]}" stroke-width="1.1"><circle cx="2" cy="2" r="1.6"/>'
        f'<circle cx="2" cy="11" r="1.6"/><circle cx="8" cy="4.5" r="1.6"/><path d="M2 3.6v5.8M8 6.1c0 2.6-6 1.4-6 3.3"/></g>'
        f'<text class="ui mu sm" x="30" y="{H - 7}">main</text>'
        f'<text class="ui mu sm" x="{W - 14}" y="{H - 7}" text-anchor="end" xml:space="preserve">Spaces: 2     UTF-8     LF     Dart</text></g>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="9.5" fill="none" stroke="{g["line"]}"/>'
    )
    return svg(W, H, "A Flutter widget describing Saram Rabbi, typed in an editor while a phone hot-reloads each field",
               css, defs, body)


# =============================================================================
# CONTACT BUTTONS: plain GitHub-style buttons
# =============================================================================
def button(label, icon):
    H = 40
    tl = text_w(label, 14)
    W = 16 + 18 + 9 + tl + 16
    g = GH
    css = (f".l{{font:600 14px {SANS};fill:{g['fg']}}}"
           f".i{{fill:none;stroke:{g['mute']};stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}}"
           f".it{{font:700 9.5px {SANS};fill:{g['mute']}}}")
    body = (
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{g["btn"]}" stroke="{g["line"]}"/>'
        f'<g transform="translate(16 11)">{icon}</g>'
        f'<text class="l" x="43" y="25" textLength="{tl}">{escape(label)}</text>'
    )
    return svg(W, H, label, css, "", body)


ICON_MAIL = '<rect class="i" x="1" y="3" width="16" height="12" rx="2"/><path class="i" d="M2 5.2l7 5.3 7-5.3"/>'
ICON_IN = '<rect class="i" x="1" y="1" width="16" height="16" rx="3.5"/><text class="it" x="9" y="12.6" text-anchor="middle">in</text>'


# =============================================================================
# FOOTER: sign-off card, same flat palette, slow waves along the bottom
# =============================================================================
SIGN_OFF = [("k", "while "), ("p", "(alive) { "), ("f", "learn"), ("p", "(); "), ("f", "build"), ("p", "(); "),
            ("f", "ship"), ("p", "(); }")]


def footer():
    W, H, CW = 900, 160, 9.6
    g = GH

    def wave(period, amp, base, cls):
        d = f"M{-period} {base}"
        for _ in range(W // period + 3):
            d += f"q{n(period / 4)} {-amp} {n(period / 2)} 0t{n(period / 2)} 0"
        return f'<path class="{cls}" d="{d}V{H}H{-period}z"/>'

    chars = sum(len(t) for _, t in SIGN_OFF)
    x0 = (W - chars * CW) / 2
    spans = "".join(f'<tspan class="{c}">{escape(t)}</tspan>' for c, t in SIGN_OFF)
    css = f"""
.h{{font:800 30px {SANS};fill:{g["fg"]}}}.c{{font:400 16px {MONO}}}
.k{{fill:#ff7b72}}.f{{fill:#d2a8ff}}.p{{fill:{g["mute"]}}}
.cur{{fill:{CARET};animation:bl 1.06s steps(1) infinite}}@keyframes bl{{50%{{opacity:0}}}}
.w1{{fill:{NAVY};opacity:.45;animation:w1 16s linear infinite}}
.w2{{fill:{SKY};opacity:.14;animation:w2 11s linear infinite reverse}}
.w3{{fill:{SKY};opacity:.22;animation:w3 8s linear infinite}}
@keyframes w1{{to{{transform:translateX(360px)}}}}@keyframes w2{{to{{transform:translateX(260px)}}}}
@keyframes w3{{to{{transform:translateX(200px)}}}}
"""
    defs = f'<clipPath id="fr"><rect width="{W}" height="{H}" rx="10"/></clipPath>'
    body = (
        f'<g clip-path="url(#fr)"><rect width="{W}" height="{H}" fill="{g["bg"]}"/>'
        f'{wave(360, 16, 132, "w1")}{wave(260, 12, 140, "w2")}{wave(200, 9, 147, "w3")}'
        f'<text class="h" x="{W / 2:.0f}" y="60" text-anchor="middle">Thanks for stopping by</text>'
        f'<text class="c" xml:space="preserve" x="{n(x0)}" y="94" textLength="{n(chars * CW)}">{spans}</text>'
        f'<rect class="cur" x="{n(x0 + chars * CW + 5)}" y="79" width="2" height="19" rx="1"/></g>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="9.5" fill="none" stroke="{g["line"]}"/>'
    )
    return svg(W, H, "Thanks for stopping by", css, defs, body)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(),
        "about.svg": about(),
        "btn-email.svg": button("Email me", ICON_MAIL),
        "btn-linkedin.svg": button("LinkedIn", ICON_IN),
        "footer.svg": footer(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"{name:20s} {len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()

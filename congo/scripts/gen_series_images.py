"""Generate hero and feature images for the Kiil principles series, in the style of gen_hero.py.

Each post gets two files in its page bundle:
  background.svg  transparent hero that works under Blowfish's light and dark overlays
  featured.png    opaque 1.91:1 image for article cards and social previews

Usage: python3 gen_series_images.py <content-root>   (e.g. /Users/lk/Web/kiils.dk)
Requires rsvg-convert for the PNG.
"""
import math
import random
import subprocess
import sys
from pathlib import Path

W, H = 1600, 640
BLUE, VIOLET, CYAN, PINK = "#2563eb", "#7c3aed", "#0891b2", "#db2777"
COLORS = [BLUE, VIOLET, CYAN]
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Page bundle per language and scene
POSTS = {
    "principles": {"da": "da/blog/2026-10-21-de-kiilske-principper-for-ai",
                   "en": "en/blog/the-kiil-principles-for-ai"},
    "rules": {"da": "da/blog/2026-10-26-regler-i-kode-skoen-i-modellen",
              "en": "en/blog/rules-in-code-judgement-in-the-model"},
    "wrong": {"da": "da/blog/2026-10-27-naar-modellen-tager-fejl",
              "en": "en/blog/when-the-model-gets-it-wrong"},
}

WORDS = {
    "da": {
        "principles": [["regel", "model", "kode", "skøn"], ["fejl", "tjek", "stop", "nul"],
                       ["spor", "log", "hvorfor", "beslut"], ["menneske", "godkend", "fortryd", "ansvar"]],
        "rules": (["assert", "==", "moms 25%", "fredag", "test", "sand", "falsk", "kode", "regel", "fast", "∈ master", "stop"],
                  ["skøn", "tone", "relevans", "nuance", "måske", "formulering", "tekst", "valg", "forslag"]),
        "wrong": (["sag 1", "sag 2", "sag 3", "sag 4", "sag 5"], ["videre", "spring over", "menneske"]),
    },
    "en": {
        "principles": [["rule", "model", "code", "judgement"], ["error", "check", "stop", "zero"],
                       ["trace", "log", "why", "decide"], ["human", "approve", "undo", "owner"]],
        "rules": (["assert", "==", "VAT 25%", "friday", "test", "true", "false", "code", "rule", "fixed", "∈ master", "stop"],
                  ["judgement", "tone", "relevance", "nuance", "maybe", "phrasing", "text", "choice", "proposal"]),
        "wrong": (["case 1", "case 2", "case 3", "case 4", "case 5"], ["apply", "skip", "human"]),
    },
}


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;")


def token_width(text):
    return 18 + 9.2 * len(text)


def pill(x, y, text, color, opacity=1.0, strong=False):
    """A token pill with its top-left corner at x, y."""
    w = token_width(text)
    fill = 0.32 if strong else 0.16
    width = 2.2 if strong else 1
    return (f'<g opacity="{opacity:.2f}"><rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="30" rx="8" '
            f'fill="{color}" fill-opacity="{fill}" stroke="{color}" stroke-opacity="0.9" stroke-width="{width}"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 20:.0f}" text-anchor="middle" fill="{color}">{esc(text)}</text></g>')


def centred_pill(cx, cy, text, color, **kw):
    return pill(cx - token_width(text) / 2, cy - 15, text, color, **kw)


def arc(a, b, weight, lift=None, stroke="url(#arc)"):
    (ax, ay), (bx, by) = a, b
    lift = 30 + 0.35 * math.dist(a, b) if lift is None else lift
    mx, my = (ax + bx) / 2, min(ay, by) - lift
    return (f'<path d="M{ax:.0f} {ay:.0f} Q{mx:.0f} {my:.0f} {bx:.0f} {by:.0f}" stroke="{stroke}" '
            f'stroke-width="{0.8 + 2.4 * weight:.1f}" stroke-opacity="{0.28 + 0.55 * weight:.2f}"/>')


def line(a, b, weight, color=BLUE, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M{a[0]:.0f} {a[1]:.0f} L{b[0]:.0f} {b[1]:.0f}" stroke="{color}"{d} '
            f'stroke-width="{0.8 + 2.4 * weight:.1f}" stroke-opacity="{0.28 + 0.55 * weight:.2f}"/>')


def glows(fields):
    out = ['<g filter="url(#glow)">']
    out += [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" fill-opacity="{o}"/>' for cx, cy, r, c, o in fields]
    return out + ["</g>"]


def scene_principles(words):
    """Four clusters, one per question, loosely linked to each other."""
    hubs = [(270, 190), (1330, 190), (270, 480), (1330, 480)]
    shapes, lines, pills = [], [], []
    for (hx, hy), cluster, color in zip(hubs, words, [BLUE, VIOLET, CYAN, PINK]):
        pills.append(centred_pill(hx, hy, cluster[0], color, strong=True))
        for k, word in enumerate(cluster[1:]):
            angle = -math.pi / 2 + (k - 1) * 0.95 + (math.pi if hy > H / 2 else 0)
            px, py = hx + 175 * math.cos(angle), hy + 95 * math.sin(angle)
            lines.append(arc((hx, hy - 15), (px, py - 15), random.uniform(0.5, 1), lift=25))
            pills.append(centred_pill(px, py, word, color, opacity=random.uniform(0.75, 1)))
    for a, b in [(0, 1), (2, 3), (0, 2), (1, 3)]:
        (ax, ay), (bx, by) = hubs[a], hubs[b]
        lines.append(arc((ax, ay - 15), (bx, by - 15), 0.15, lift=60))
    fields = [(270, 190, 220, BLUE, 0.45), (1330, 190, 220, VIOLET, 0.4),
              (270, 480, 200, CYAN, 0.4), (1330, 480, 200, PINK, 0.3)]
    return fields, shapes, lines, pills


def scene_rules(words):
    """A rigid grid of rules on the left, free model arcs on the right, a fence in between."""
    rules, model = words
    shapes, lines, pills = [], [], []
    fence_x = 800
    gaps = [230, 410]
    # The fence: a row of posts with two gates the model must pass through
    for y in range(90, H - 20, 26):
        if any(abs(y - g) < 30 for g in gaps):
            continue
        shapes.append(f'<rect x="{fence_x - 3}" y="{y}" width="6" height="16" rx="3" fill="{BLUE}" fill-opacity="0.55"/>')
    # Rules: aligned rows and straight links
    cols, rows = [70, 250, 430], [110, 200, 290, 380, 470, 560]
    grid = []
    for i, word in enumerate(rules):
        x, y = cols[i % 3], rows[i // 3 % len(rows)] + (i // 9) * 0
        grid.append((x, y, word))
    for x, y, word in grid:
        pills.append(pill(x, y, word, BLUE, opacity=random.uniform(0.8, 1)))
    for x, y, word in grid:
        right = [(gx, gy, gw) for gx, gy, gw in grid if gy == y and gx > x]
        if right:
            gx, gy, _ = min(right)
            lines.append(line((x + token_width(word), y + 15), (gx, gy + 15), 0.5))
    # Model: scattered tokens with arcs, some reaching the gates in the fence
    spots = [(1040, 140), (1330, 120), (1180, 250), (1450, 300), (980, 380), (1270, 420),
             (1110, 540), (1420, 520), (1500, 180)]
    centres = []
    for (x, y), word in zip(spots, model):
        color = random.choice([VIOLET, PINK, VIOLET])
        pills.append(centred_pill(x, y, word, color, opacity=random.uniform(0.75, 1)))
        centres.append((x, y - 15))
    for i, a in enumerate(centres):
        for j in sorted(range(len(centres)), key=lambda k: math.dist(a, centres[k]))[1:3]:
            if j > i:
                lines.append(arc(a, centres[j], random.random() ** 1.4))
    for gate, src in zip(gaps, [centres[0], centres[4]]):
        lines.append(arc(src, (fence_x + 40, gate), 0.9, lift=-20))
        lines.append(line((fence_x + 40, gate), (fence_x - 70, gate), 0.9, color=BLUE, dash="2 8"))
    fields = [(260, 330, 260, BLUE, 0.45), (1250, 200, 260, VIOLET, 0.4), (1300, 520, 200, PINK, 0.25)]
    return fields, shapes, lines, pills


def scene_wrong(words):
    """Each case is judged twice. Agreement routes on, disagreement goes to a human."""
    cases, outcomes = words
    shapes, lines, pills = [], [], []
    left_x, right_x = 230, 1330
    case_y = [130, 230, 330, 430, 530]
    out_y = {"go": 190, "skip": 350, "human": 510}
    out_word = dict(zip(["go", "skip", "human"], outcomes))
    # Rule verdict, model verdict per case; case 4 is the disagreement
    routes = [("go", "go"), ("skip", "skip"), ("go", "go"), ("skip", "go"), ("skip", "skip")]
    for (rule, model), y, word in zip(routes, case_y, cases):
        pills.append(centred_pill(left_x, y, word, CYAN))
        start = (left_x + token_width(word) / 2 + 6, y)
        if rule == model:
            # Asked twice, same answer: the rule line and the model arc travel together
            end = (right_x - token_width(out_word[rule]) / 2 - 6, out_y[rule])
            lines.append(line(start, end, 0.45, color=BLUE))
            lines.append(arc(start, end, 0.45, lift=22))
            continue
        # The two verdicts part ways at a junction; neither reaches its target, the case goes to a human
        junction = (720, y)
        lines.append(line(start, junction, 0.8, color=BLUE))
        lines.append(arc(start, junction, 0.8, lift=22))
        for verdict, color in [(rule, BLUE), (model, VIOLET)]:
            tx = right_x - token_width(out_word[verdict]) / 2 - 6
            stub = (junction[0] + 0.35 * (tx - junction[0]), y + 0.35 * (out_y[verdict] - y))
            lines.append(line(junction, stub, 0.3, color=color, dash="4 8"))
        end = (right_x - token_width(out_word["human"]) / 2 - 6, out_y["human"])
        lines.append(line(junction, end, 1.0, color=PINK))
        shapes.append(f'<circle cx="{junction[0]}" cy="{y}" r="11" fill="{PINK}" fill-opacity="0.9"/>')
        pills.append(f'<text x="{junction[0]}" y="{y + 5}" text-anchor="middle" fill="#fff" font-weight="bold">?</text>')
    for key, y in out_y.items():
        color = PINK if key == "human" else VIOLET
        pills.append(centred_pill(right_x, y, out_word[key], color, strong=True))
    fields = [(230, 330, 230, CYAN, 0.4), (1330, 260, 240, VIOLET, 0.4), (1330, 520, 180, PINK, 0.35)]
    return fields, shapes, lines, pills


SCENES = {"principles": scene_principles, "rules": scene_rules, "wrong": scene_wrong}


def render(scene, words, opaque):
    random.seed(f"{scene}-35172831")
    fields, shapes, lines, pills = SCENES[scene](words)
    # Padding keeps the scene whole under object-cover: 1.91:1 for social previews, ~16:9 for the hero
    view = f"-80 -140 {W + 160} 920" if opaque else f"0 -130 {W} 900"
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" preserveAspectRatio="xMidYMid slice">',
             f"""<defs>
<filter id="glow" filterUnits="userSpaceOnUse" x="-600" y="-700" width="{W + 1200}" height="{H + 1400}"><feGaussianBlur stdDeviation="80"/></filter>
<linearGradient id="arc" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="0.5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
</defs>"""]
    if opaque:
        parts.append(f'<rect x="-80" y="-140" width="{W + 160}" height="920" fill="#f8fafc"/>')
    parts += glows(fields)
    parts += shapes
    parts += ['<g fill="none" stroke-linecap="round">'] + lines + ["</g>"]
    parts += [f'<g font-family="{MONO}" font-size="15">'] + pills + ["</g>"]
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main(root):
    root = Path(root)
    for scene, bundles in POSTS.items():
        for lang, bundle in bundles.items():
            out = root / bundle
            out.mkdir(parents=True, exist_ok=True)
            words = WORDS[lang][scene]
            (out / "background.svg").write_text(render(scene, words, opaque=False))
            featured_svg = out / "featured.svg"
            featured_svg.write_text(render(scene, words, opaque=True))
            subprocess.run(["rsvg-convert", "-w", "1200", "-o", str(out / "featured.png"), str(featured_svg)], check=True)
            featured_svg.unlink()
            print(out)


if __name__ == "__main__":
    main(sys.argv[1])

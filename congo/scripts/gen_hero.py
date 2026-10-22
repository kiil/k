"""Generate the kiils.dk front page background: Danish word tokens linked by attention arcs.

The SVG has a transparent base so it works under Blowfish's light and dark overlays.
Usage: python3 gen_hero.py <out.svg>
"""
import math
import random
import sys

W, H = 1600, 640
random.seed(35172831)

COLORS = ["#2563eb", "#7c3aed", "#0891b2", "#db2777"]

# Words and subword pieces as a tokenizer might split them
TOKENS = [
    "sprog", "mening", "kon", "##tekst", "ord", "spørgs", "##mål", "svar", "regel",
    "skøn", "menneske", "tvivl", "kilde", "▁venlig", "intelli", "##gens", "værdi",
    "prompt", "data", "for", "##klaring", "beslut", "##ning", "▁og", "▁der", "tale",
    "skrift", "lytte", "lære", "fejl", "spor", "valg", "ansvar", "tanke", "tekst",
    "betyd", "##ning", "æ", "ø", "å", "dansk", "viden", "løsning", "▁at", "sætning",
    "grammatik", "nuance", "tone", "tillid", "▁kan", "fortryd", "##es",
]


def token_width(text):
    return 18 + 9.2 * len(text)


def center_weight(x, y):
    """0 at the centre of the hero, 1 at the edges; keeps the headline area calm."""
    dx = (x - W / 2) / (W * 0.36)
    dy = (y - H * 0.46) / (H * 0.55)
    return min(1.0, math.hypot(dx, dy))


def place_tokens():
    placed = []
    attempts = 0
    pool = list(dict.fromkeys(TOKENS))
    random.shuffle(pool)
    while pool and len(placed) < 44 and attempts < 6000:
        attempts += 1
        text = pool[-1]
        w, h = token_width(text), 30
        # Keep clear of the fixed header bar
        x, y = random.uniform(20, W - w - 20), random.uniform(78, H - h - 20)
        cw = center_weight(x + w / 2, y + h / 2)
        if cw < 0.55 and random.random() > cw * 0.4:
            continue
        if any(x < px + pw + 28 and px < x + w + 28 and y < py + ph + 22 and py < y + h + 22
               for px, py, pw, ph, _, _ in placed):
            continue
        placed.append((x, y, w, h, text, cw))
        pool.pop()
    return placed


def main(out):
    tokens = place_tokens()
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">']
    parts.append("""  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="80"/></filter>
    <linearGradient id="arc" x1="0" x2="1">
      <stop offset="0" stop-color="#2563eb"/><stop offset="0.5" stop-color="#7c3aed"/><stop offset="1" stop-color="#db2777"/>
    </linearGradient>
    <radialGradient id="calm" cx="0.5" cy="0.46" r="0.62">
      <stop offset="0" stop-color="#000"/><stop offset="0.45" stop-color="#000" stop-opacity="0.6"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
    </radialGradient>
    <mask id="edges"><rect width="100%" height="100%" fill="#fff"/><rect width="100%" height="100%" fill="url(#calm)"/></mask>
  </defs>""")

    # Soft colour fields
    parts.append('  <g filter="url(#glow)">')
    for cx, cy, r, c, o in [(220, 110, 250, COLORS[0], 0.55), (1380, 140, 270, COLORS[2], 0.45),
                            (860, 600, 230, COLORS[1], 0.45), (1150, 470, 150, COLORS[3], 0.3),
                            (380, 560, 170, COLORS[1], 0.3)]:
        parts.append(f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" fill-opacity="{o}"/>')
    parts.append("  </g>")

    parts.append('  <g mask="url(#edges)">')

    # Attention arcs between nearby tokens, stronger weights drawn thicker
    parts.append('    <g fill="none" stroke="url(#arc)" stroke-linecap="round">')
    centres = [(x + w / 2, y + h / 2) for x, y, w, h, _, _ in tokens]
    for i, (ax, ay) in enumerate(centres):
        near = sorted(range(len(centres)), key=lambda j: math.dist((ax, ay), centres[j]))[1:4]
        for j in near:
            if j < i and i in sorted(range(len(centres)), key=lambda k: math.dist(centres[j], centres[k]))[1:4]:
                continue
            bx, by = centres[j]
            weight = random.random() ** 1.6
            lift = 30 + 0.35 * math.dist((ax, ay), (bx, by))
            mx, my = (ax + bx) / 2, min(ay, by) - lift
            parts.append(f'      <path d="M{ax:.0f} {ay - 15:.0f} Q{mx:.0f} {my:.0f} {bx:.0f} {by - 15:.0f}" '
                         f'stroke-width="{0.8 + 2.4 * weight:.1f}" stroke-opacity="{0.28 + 0.55 * weight:.2f}"/>')
    parts.append("    </g>")

    # Token pills
    parts.append('    <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="15">')
    for x, y, w, h, text, _ in tokens:
        c = random.choice(COLORS)
        o = random.uniform(0.75, 1.0)
        text = text.replace("&", "&amp;").replace("<", "&lt;")
        parts.append(f'      <g opacity="{o:.2f}"><rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h}" rx="8" '
                     f'fill="{c}" fill-opacity="0.16" stroke="{c}" stroke-opacity="0.9"/>'
                     f'<text x="{x + w / 2:.0f}" y="{y + 20:.0f}" text-anchor="middle" fill="{c}">{text}</text></g>')
    parts.append("    </g>")
    parts.append("  </g>")
    parts.append("</svg>")
    open(out, "w").write("\n".join(parts) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])

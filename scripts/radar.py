"""Generates the radar charts in assets/. Edit the scores (0-100) and run: python3 scripts/radar.py"""
import math
from pathlib import Path

SKILL_RADAR = {
    "DSA": 70,
    "JavaScript": 80,
    "React": 75,
    "Node / API": 75,
    "Databases": 70,
    "Python": 80,
    "Data Science": 70,
    "HTML / CSS": 80,
}

LANGUAGE_MIX = {
    "JavaScript": 85,
    "Python": 75,
    "R": 45,
    "SQL": 50,
    "HTML": 60,
    "CSS": 55,
}

GREEN = "#39ff14"
W, H, CX, CY, R = 480, 440, 240, 240, 130


def radar(title, data):
    n = len(data)
    point = lambda i, frac: (
        CX + R * frac * math.cos(-math.pi / 2 + 2 * math.pi * i / n),
        CY + R * frac * math.sin(-math.pi / 2 + 2 * math.pi * i / n),
    )
    fmt = lambda pts: " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    rings = "".join(
        f'<polygon points="{fmt(point(i, level / 4) for i in range(n))}" fill="none" stroke="#2a3a2a"/>'
        for level in range(1, 5)
    )
    spokes = "".join(
        f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="#2a3a2a"/>'
        for x, y in (point(i, 1) for i in range(n))
    )
    shape = fmt(point(i, v / 100) for i, v in enumerate(data.values()))
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{GREEN}"/>'
        for x, y in (point(i, v / 100) for i, v in enumerate(data.values()))
    )
    labels = ""
    for i, (name, value) in enumerate(data.items()):
        x, y = point(i, 1.2)
        anchor = "middle" if abs(x - CX) < 10 else ("start" if x > CX else "end")
        labels += (
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="label">{name}</text>'
            f'<text x="{x:.1f}" y="{y + 13:.1f}" text-anchor="{anchor}" class="value">{value}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .title {{ font: 600 15px 'Fira Code', ui-monospace, monospace; fill: #c9d1d9; }}
  .label {{ font: 600 11px 'Fira Code', ui-monospace, monospace; fill: #c9d1d9; }}
  .value {{ font: 10px 'Fira Code', ui-monospace, monospace; fill: #8b949e; }}
</style>
<rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#21262d"/>
<text x="20" y="30" class="title">{title}</text>
{rings}{spokes}
<g>
  <polygon points="{shape}" fill="{GREEN}" fill-opacity="0.25" stroke="{GREEN}" stroke-width="2"/>
  {dots}
</g>
{labels}
</svg>
"""


out = Path(__file__).resolve().parent.parent / "assets"
(out / "skill-radar.svg").write_text(radar("skill radar", SKILL_RADAR))
(out / "language-mix.svg").write_text(radar("language mix", LANGUAGE_MIX))
print("Wrote assets/skill-radar.svg and assets/language-mix.svg")

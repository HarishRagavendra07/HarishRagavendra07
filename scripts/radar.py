"""Generates the radar charts in assets/.

- skill radar: hand-picked scores (0-100) below; edit them to change the chart.
- language mix: computed from the languages in my public GitHub repos.
  Falls back to LANGUAGE_MIX below if GitHub can't be reached.

Run: python3 scripts/radar.py   (the profile workflow runs it automatically)
"""
import datetime
import json
import math
import os
import urllib.request
from collections import defaultdict
from pathlib import Path

GITHUB_USER = "HarishRagavendra07"

SKILL_RADAR = {
    "Python": 90,
    "AI / ML": 85,
    "Data Eng": 85,
    "Cloud": 80,
    "Backend / APIs": 80,
    "DevOps / CI-CD": 75,
    "SQL": 85,
    "C++": 70,
}

LANGUAGE_MIX = {
    "Python": 90,
    "SQL": 80,
    "PySpark": 80,
    "C++": 65,
    "JavaScript": 60,
}

# Languages GitHub reports that aren't worth a spoke, and ones to merge or rename
IGNORED = {"Dockerfile", "Makefile", "Procfile", "Go Template", "Batchfile"}
ALIASES = {"Jupyter Notebook": "Python", "HCL": "Terraform"}
MAX_SPOKES = 6

GREEN = "#39ff14"
W, H, CX, CY, R = 480, 440, 240, 240, 130


def radar(title, data, display=None, subtitle=""):
    """data: {label: 0-100 spoke length}; display: optional {label: text shown under it}"""
    display = display or data
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
    for i, name in enumerate(data):
        x, y = point(i, 1.2)
        anchor = "middle" if abs(x - CX) < 10 else ("start" if x > CX else "end")
        labels += (
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="label">{name}</text>'
            f'<text x="{x:.1f}" y="{y + 13:.1f}" text-anchor="{anchor}" class="value">{display[name]}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .title {{ font: 600 15px 'Fira Code', ui-monospace, monospace; fill: #c9d1d9; }}
  .label {{ font: 600 11px 'Fira Code', ui-monospace, monospace; fill: #c9d1d9; }}
  .value {{ font: 10px 'Fira Code', ui-monospace, monospace; fill: #8b949e; }}
  .subtitle {{ font: 10px 'Fira Code', ui-monospace, monospace; fill: #8b949e; }}
</style>
<rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#21262d"/>
<text x="20" y="30" class="title">{title}</text>
<text x="20" y="46" class="subtitle">{subtitle}</text>
{rings}{spokes}
<g>
  <polygon points="{shape}" fill="{GREEN}" fill-opacity="0.25" stroke="{GREEN}" stroke-width="2"/>
  {dots}
</g>
{labels}
</svg>
"""


def github_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": GITHUB_USER}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as res:
        return json.load(res)


def language_mix_from_github():
    """Average each language's share per repo, so one huge generated file can't dominate."""
    repos = github_json(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&type=owner")
    repos = [r for r in repos if not r["fork"] and not r["archived"] and r["name"] != GITHUB_USER]
    shares = defaultdict(float)
    counted = 0
    for repo in repos:
        langs = defaultdict(int)
        for lang, size in github_json(repo["languages_url"]).items():
            if lang not in IGNORED:
                langs[ALIASES.get(lang, lang)] += size
        total = sum(langs.values())
        if not total:
            continue
        counted += 1
        for lang, size in langs.items():
            shares[lang] += size / total
    top = sorted(shares.items(), key=lambda kv: kv[1], reverse=True)[:MAX_SPOKES]
    if len(top) < 3:
        raise ValueError("need at least 3 languages for a radar chart")
    total = sum(shares.values())
    percents = {lang: 100 * share / total for lang, share in top}
    biggest = max(percents.values())
    # Square root keeps smaller languages visible next to the main one
    lengths = {lang: 100 * math.sqrt(p / biggest) for lang, p in percents.items()}
    display = {lang: f"{p:.0f}%" for lang, p in percents.items()}
    return lengths, display, counted


out = Path(__file__).resolve().parent.parent / "assets"
(out / "skill-radar.svg").write_text(radar("skill radar", SKILL_RADAR))

today = datetime.date.today().isoformat()
try:
    lengths, display, repo_count = language_mix_from_github()
    subtitle = f"from {repo_count} public repos · updated {today}"
    (out / "language-mix.svg").write_text(radar("language mix", lengths, display, subtitle))
    print(f"language mix from GitHub: {display}")
except Exception as err:  # offline, rate-limited, etc.: keep the chart usable
    print(f"GitHub language data unavailable ({err}); using LANGUAGE_MIX fallback")
    (out / "language-mix.svg").write_text(radar("language mix", LANGUAGE_MIX))
print("Wrote assets/skill-radar.svg and assets/language-mix.svg")

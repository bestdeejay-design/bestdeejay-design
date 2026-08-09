#!/usr/bin/env python3
"""Update the total-stars badge SVG for the GitHub profile.

Counts stargazers across all public repos of the configured user (with
pagination) and writes assets/total-stars.svg in shields.io style.
Pure Python 3 stdlib — no external dependencies.

Env:
  GITHUB_USER   owner to sum stars for (default: bestdeejay-design)
  GH_TOKEN      optional token (raises rate limits; GitHub Actions provides it)
"""

import json
import os
import sys
import urllib.request

USER = os.environ.get("GITHUB_USER", "bestdeejay-design")
TOKEN = os.environ.get("GH_TOKEN", "")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "badge-stars.svg")


def fetch_page(page: int) -> list:
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}"
    req = urllib.request.Request(url, headers={"User-Agent": "stars-badge", "Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def total_stars() -> int:
    total = 0
    page = 1
    while True:
        repos = fetch_page(page)
        if not repos:
            break
        total += sum(r.get("stargazers_count") or 0 for r in repos)
        if len(repos) < 100:
            break
        page += 1
    return total


def fmt(n: int) -> str:
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def render_svg(label: str, value: str) -> str:
    # Stamped badge: fixed 12px padding, width auto-fits, icon vertically centered.
    # Same layout as badge-axiiom.svg / badge-lovii.svg (icon + label | value).
    label = label.upper()
    font = 'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"'
    pad = 12
    char_w = 8.0
    icon_w = 22
    icon_y = 3.2  # star icon bbox ~7.2-14.4 -> center 14
    lw = pad + icon_w + len(label) * char_w + pad
    vw = pad + len(value) * char_w + pad
    w = lw + vw
    h = 28
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}: {value}">
  <rect width="{w}" height="{h}" rx="4" fill="#555555"/>
  <rect x="{lw}" width="{vw}" height="{h}" rx="4" fill="#D4A574"/>
  <path d="M{lw} 0H{lw+6}V{h}H{lw}Z" fill="#555555"/>
  <g fill="#D4A574" transform="translate({pad},{icon_y})">
    <path d="M10.5 7.2l1.6 3.2 3.5.5-2.5 2.5.6 3.5-3.2-1.7-3.2 1.7.6-3.5-2.5-2.5 3.5-.5z"/>
  </g>
  <text x="{pad + icon_w}" y="18.5" fill="#FFFFFF" {font} font-size="13" font-weight="700">{label}</text>
  <text x="{lw + pad}" y="18.5" fill="#FFFFFF" {font} font-size="13" font-weight="700">{value}</text>
</svg>
'''


def main() -> int:
    try:
        stars = total_stars()
    except Exception as e:  # noqa: BLE001 - badge should degrade gracefully
        print(f"error: {e}", file=sys.stderr)
        return 1
    svg = render_svg("total stars", fmt(stars))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"stars={stars} -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

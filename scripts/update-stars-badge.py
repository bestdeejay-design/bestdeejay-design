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
    # Series badge: fixed 150x34, dark gradient card, gold rim, star icon + label/value.
    # Same layout as badge-axiiom.svg / badge-lovii.svg — one consistent row.
    label = label.upper()
    font = 'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="150" height="34" viewBox="0 0 150 34" role="img" aria-label="{label}: {value}">
  <defs>
    <linearGradient id="b" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#262C35"/><stop offset="1" stop-color="#191E26"/>
    </linearGradient>
  </defs>
  <rect width="150" height="34" rx="9" fill="url(#b)" stroke="#D4A574" stroke-opacity="0.35" stroke-width="1"/>
  <g fill="#D4A574" transform="translate(12,9.5)">
    <path d="M10.5 7.2l1.6 3.2 3.5.5-2.5 2.5.6 3.5-3.2-1.7-3.2 1.7.6-3.5-2.5-2.5 3.5-.5z"/>
  </g>
  <text x="38" y="13.5" fill="#98A0AB" {font} font-size="9" font-weight="600" letter-spacing="1.2">{label}</text>
  <text x="38" y="26" fill="#FFFFFF" {font} font-size="14" font-weight="700">{value}</text>
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

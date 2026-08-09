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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = os.environ.get("GITHUB_USER", "bestdeejay-design")
TOKEN = os.environ.get("GH_TOKEN", "")

ICONS = {
    "axiiom": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzNiAzNiI+PHJlY3QgeD0iMiIgeT0iMiIgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiByeD0iMiIgc3Ryb2tlPSIjRDRBNTc0IiBzdHJva2Utd2lkdGg9IjEuNSIgb3BhY2l0eT0iLjQ1IiBmaWxsPSJub25lIi8+PHJlY3QgeD0iMjAiIHk9IjIiIHdpZHRoPSIxNCIgaGVpZ2h0PSIxNCIgcng9IjIiIHN0cm9rZT0iI0Q0QTU3NCIgc3Ryb2tlLXdpZHRoPSIxLjUiIG9wYWNpdHk9Ii40NSIgZmlsbD0ibm9uZSIvPjxyZWN0IHg9IjIiIHk9IjIwIiB3aWR0aD0iMTQiIGhlaWdodD0iMTQiIHJ4PSIyIiBzdHJva2U9IiNENEE1NzQiIHN0cm9rZS13aWR0aD0iMS41IiBvcGFjaXR5PSIuNDUiIGZpbGw9Im5vbmUiLz48cmVjdCB4PSIyMCIgeT0iMjAiIHdpZHRoPSIxNCIgaGVpZ2h0PSIxNCIgcng9IjIiIGZpbGw9IiNENEE1NzQiLz48L3N2Zz4=",
    "lovii": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+CjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDEyLDEyKSBzY2FsZSgwLjI1OCkgdHJhbnNsYXRlKC0xNjUuNCwtMjQwLjEpIj4KPHBhdGggZmlsbD0iI0Q0QTU3NCIgZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNMjA0LjQxLDIxOC4wNmMtNC4wNS02LjYzLTkuNDktMTEuOTEtMTYuMy0xNS44NC02LjgxLTMuOTMtMTQuMzgtNS45LTIyLjY5LTUuOXMtMTUuODMsMS45Ny0yMi42Niw1LjljLTYuODMsMy45My0xMi4yOCw5LjIxLTE2LjMzLDE1Ljg0LTQuMDUsNi42My02LjA4LDEzLjk3LTYuMDgsMjIuMDRzMi4wMywxNS40Miw2LjA4LDIyLjA0YzQuMDUsNi42Myw5LjUsMTEuOTIsMTYuMzMsMTUuODcsNi44MywzLjk1LDE0LjM5LDUuOTMsMjIuNjYsNS45M3MxNS44OC0xLjk4LDIyLjY5LTUuOTNjNi44MS0zLjk1LDEyLjI1LTkuMjQsMTYuMy0xNS44Nyw0LjA1LTYuNjMsNi4wOC0xMy45Nyw2LjA4LTIyLjA0cy0yLjAzLTE1LjQxLTYuMDgtMjIuMDRaIE0xODcuOTIsMjIzLjk4Yy01LjU4LTUuNTgtMTQuNjItNS41OC0yMC4yLDBsLTIuMzEsMi4zMS0yLjMxLTIuMzFjLTUuNTgtNS41OC0xNC42Mi01LjU4LTIwLjIsMC00LjkxLDQuOTEtNS41LDEyLjUtMS43NiwxOC4wNiw0LjYzLDUuNjYsMTAuNjksMTEuOTEsMjQuNDIsMjQuNWwyMi4zNi0yMi4zNmM1LjU4LTUuNTgsNS41OC0xNC42MiwwLTIwLjJaIi8+CjwvZz4KPC9zdmc+",
    "stars": "data:image/svg+xml;base64,PHN2ZyBmaWxsPSIjRDRBNTc0IiByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48dGl0bGU+R2l0SHViPC90aXRsZT48cGF0aCBkPSJNMTIgLjI5N2MtNi42MyAwLTEyIDUuMzczLTEyIDEyIDAgNS4zMDMgMy40MzggOS44IDguMjA1IDExLjM4NS42LjExMy44Mi0uMjU4LjgyLS41NzcgMC0uMjg1LS4wMS0xLjA0LS4wMTUtMi4wNC0zLjMzOC43MjQtNC4wNDItMS42MS00LjA0Mi0xLjYxQzQuNDIyIDE4LjA3IDMuNjMzIDE3LjcgMy42MzMgMTcuN2MtMS4wODctLjc0NC4wODQtLjcyOS4wODQtLjcyOSAxLjIwNS4wODQgMS44MzggMS4yMzYgMS44MzggMS4yMzYgMS4wNyAxLjgzNSAyLjgwOSAxLjMwNSAzLjQ5NS45OTguMTA4LS43NzYuNDE3LTEuMzA1Ljc2LTEuNjA1LTIuNjY1LS4zLTUuNDY2LTEuMzMyLTUuNDY2LTUuOTMgMC0xLjMxLjQ2NS0yLjM4IDEuMjM1LTMuMjItLjEzNS0uMzAzLS41NC0xLjUyMy4xMDUtMy4xNzYgMCAwIDEuMDA1LS4zMjIgMy4zIDEuMjMuOTYtLjI2NyAxLjk4LS4zOTkgMy0uNDA1IDEuMDIuMDA2IDIuMDQuMTM4IDMgLjQwNSAyLjI4LTEuNTUyIDMuMjg1LTEuMjMgMy4yODUtMS4yMy42NDUgMS42NTMuMjQgMi44NzMuMTIgMy4xNzYuNzY1Ljg0IDEuMjMgMS45MSAxLjIzIDMuMjIgMCA0LjYxLTIuODA1IDUuNjI1LTUuNDc1IDUuOTIuNDIuMzYuODEgMS4wOTYuODEgMi4yMiAwIDEuNjA2LS4wMTUgMi44OTYtLjAxNSAzLjI4NiAwIC4zMTUuMjEuNjkuODI1LjU3QzIwLjU2NSAyMi4wOTIgMjQgMTcuNTkyIDI0IDEyLjI5N2MwLTYuNjI3LTUuMzczLTEyLTEyLTEyIi8+PC9zdmc+",
}

OUTS = {
    "axiiom": ("AXIIOM", "CEO", "badge-axiiom.svg"),
    "lovii": ("LOVII", "FOUNDER", "badge-lovii-2.svg"),
    "stars": ("Total stars", "??", "badge-stars.svg"),
}


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


def render_svg(label: str, value: str, icon: str) -> str:
    label = label.upper()
    font = 'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"'
    h, icon_w, icon_h = 32, 14, 14
    pad_l, gap, pad_r = 14, 10, 14
    char_w = 8.8
    text_w = (len(label) + 1 + len(value)) * char_w
    w = int(pad_l + icon_w + gap + text_w + pad_r)
    icon_y = (h - icon_h) / 2
    text_x = pad_l + icon_w + gap
    text_y = h / 2 + 4.9
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}: {value}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2B313C"/><stop offset="1" stop-color="#171C23"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.10"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#D4A574" stop-opacity="0.30"/><stop offset="1" stop-color="#D4A574" stop-opacity="0"/>
    </radialGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
    <clipPath id="clip"><rect width="{w}" height="{h}" rx="10"/></clipPath>
  </defs>
  <g filter="url(#shadow)">
    <rect width="{w}" height="{h}" rx="10" fill="url(#bg)"/>
    <g clip-path="url(#clip)">
      <circle cx="{pad_l + icon_w / 2}" cy="{h / 2}" r="13" fill="url(#glow)"/>
      <rect width="{w}" height="14" fill="url(#shine)"/>
    </g>
    <rect width="{w}" height="{h}" rx="10" fill="none" stroke="#FFFFFF" stroke-opacity="0.10"/>
    <image x="{pad_l}" y="{icon_y}" width="{icon_w}" height="{icon_h}" href="{icon}"/>
    <text x="{text_x}" y="{text_y}" fill="#FFFFFF" {font} font-size="14" font-weight="700" letter-spacing="0.6">{label}<tspan fill="#D4A574" font-weight="800" letter-spacing="0"> {value}</tspan></text>
  </g>
</svg>
'''


def main() -> int:
    try:
        stars = total_stars()
    except Exception as e:  # noqa: BLE001 - badge should degrade gracefully
        print(f"error: {e}", file=sys.stderr)
        return 1
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    for name, (label, _value, filename) in OUTS.items():
        value = fmt(stars) if name == "stars" else _value
        svg = render_svg(label, value, ICONS[name])
        out = os.path.join(ROOT, "assets", filename)
        with open(out, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"stars={stars} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

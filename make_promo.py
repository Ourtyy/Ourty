#!/usr/bin/env python3
"""Make promotion material for published articles.

  python3 make_promo.py            -> for every published article that has a photo:
                                      * Pinterest pin  content/pins/<slug>.png   (1000x1500)
                                      * Pinterest text promo/pinterest/<slug>.txt (title, description, link)
                                      * Substack post  promo/substack/<slug>.md   (only if it doesn't exist yet;
                                        the writer fills in the body — see CLAUDE.md)
  python3 make_promo.py --force    -> re-render all pins

Pins use `pin_title` from the article front matter if present (short and catchy), else the title.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
SITE = build.SITE
PINS = ROOT / "content" / "pins"
PROMO = ROOT / "promo"


def main(force=False):
    PINS.mkdir(parents=True, exist_ok=True)
    (PROMO / "pinterest").mkdir(parents=True, exist_ok=True)
    (PROMO / "substack").mkdir(parents=True, exist_ok=True)
    base = SITE["base_url"].rstrip("/")
    for p in build.load_posts(include_drafts=False):
        slug = p["slug"]
        url = f"{base}/posts/{slug}/"
        cat = SITE["categories"].get(p["category"], {"label": p["category"]})["label"]
        pin = PINS / f"{slug}.png"
        if p.get("image") and (force or not pin.exists()):
            title = p.get("pin_title") or p["title"]
            subprocess.run(["swift", str(ROOT / "tools" / "make_pin.swift"), p["image"], cat, title, str(pin)], check=True)
        txt = PROMO / "pinterest" / f"{slug}.txt"
        if not txt.exists():
            txt.write_text(
                f"PIN IMAGE: content/pins/{slug}.png\n"
                f"TITLE: {(p.get('pin_title') or p['title'])[:100]}\n"
                f"DESCRIPTION: {p.get('pin_description') or p.get('description', '')}\n"
                f"LINK: {url}\n"
                f"BOARD: {cat}\n", encoding="utf-8")
        sub = PROMO / "substack" / f"{slug}.md"
        if not sub.exists():
            sub.write_text(f"TITLE: {p['title']}\nSUBTITLE: {p.get('description', '')}\nLINK: {url}\n\n"
                           "<!-- TODO: write a 150-250 word teaser (see CLAUDE.md) -->\n", encoding="utf-8")
        print(f"ok  {slug}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)

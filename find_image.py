#!/usr/bin/env python3
"""Find free, commercially usable photos (Openverse: Flickr, Wikimedia...) for an article.

  python3 find_image.py search "overnight oats"      -> downloads up to 6 candidates to .image-candidates/
  python3 find_image.py pick <N> <name>               -> saves candidate N as content/images/<name>.jpg
                                                         (resized to 1400px wide) and prints the front matter lines

Only licenses that allow commercial use are requested (CC0, Public Domain, CC BY, CC BY-SA).
Always look at the candidates before picking one: the photo must match the article.
"""
import json
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAND = ROOT / ".image-candidates"
IMAGES = ROOT / "content" / "images"
UA = {"User-Agent": "OurtyBlogBuilder/1.0 (+https://ourtyy.github.io/Ourty/)"}
PREFERRED = {"cc0": 0, "pdm": 0, "by": 1, "by-sa": 2}


def get(url, timeout=30, limit=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        data = r.read(limit + 1) if limit else r.read()
    if limit and len(data) > limit:
        raise ValueError("file too big")
    return data


def search(query):
    q = urllib.parse.urlencode({"q": query, "license": "cc0,pdm,by,by-sa", "page_size": 20})
    data = json.loads(get(f"https://api.openverse.org/v1/images/?{q}"))
    results = [r for r in data["results"] if (r.get("width") or 0) >= 900 and (r.get("width") or 0) >= (r.get("height") or 0)]
    # prefer open licenses, Flickr (reasonable file sizes) and widths close to 1600px
    results.sort(key=lambda r: (PREFERRED.get(r["license"], 9) > 1, r["source"] != "flickr", abs((r.get("width") or 0) - 1600)))
    if CAND.exists():
        shutil.rmtree(CAND)
    CAND.mkdir()
    picked = []
    for r in results:
        if len(picked) == 6:
            break
        try:
            raw = get(r["url"], timeout=15, limit=6_000_000)
        except Exception:
            continue
        n = len(picked) + 1
        (CAND / f"{n}.jpg").write_bytes(raw)
        picked.append(r)
        print(f"{n}. {r['title'][:60]} | {r['creator']} | CC {r['license'].upper()} {r.get('license_version') or ''} | {r['width']}x{r['height']}")
    (CAND / "meta.json").write_text(json.dumps(picked, indent=1))
    print(f"\nCandidates saved in {CAND}/ — view them, then: python3 find_image.py pick <N> <name>")


def pick(n, name):
    meta = json.loads((CAND / "meta.json").read_text())[int(n) - 1]
    IMAGES.mkdir(parents=True, exist_ok=True)
    out = IMAGES / f"{name}.jpg"
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "78", "--resampleWidth", "1400",
                    str(CAND / f"{n}.jpg"), "--out", str(out)], check=True, capture_output=True)
    lic = meta["license"]
    label = "Public domain" if lic in ("cc0", "pdm") else f"CC {lic.upper()} {meta.get('license_version') or ''}".strip()
    creator = (meta.get("creator") or "Unknown").replace(":", " -")
    print("Add these lines to the article front matter:\n")
    print(f"image: images/{name}.jpg")
    print("image_alt: <describe the photo in a few words>")
    print(f"image_credit: {creator}")
    print(f"image_source: {meta.get('foreign_landing_url') or meta['url']}")
    print(f"image_license: {label}")
    print(f"image_license_url: {meta.get('license_url') or ''}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "search":
        search(a[1])
    elif len(a) == 3 and a[0] == "pick":
        pick(a[1], a[2])
    else:
        print(__doc__)

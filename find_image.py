#!/usr/bin/env python3
"""Find beautiful, free, commercially usable photos for an article.

  python3 find_image.py search "overnight oats bowl"  -> saves up to 8 small candidates in .image-candidates/
  python3 find_image.py pick <N> <name>               -> downloads candidate N in high quality as
                                                         content/images/<name>.jpg and prints the front matter lines

Source: Pexels (needs a free API key in pexels_key.txt, never committed) — free for commercial use.
Fallback without a key: Openverse (Flickr/Wikimedia, CC0 / CC BY / CC BY-SA).
Always LOOK at the candidates before picking one: the photo must match the article and look beautiful.
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
KEY_FILE = ROOT / "pexels_key.txt"
UA = "OurtyBlogBuilder/1.0 (+https://ourtyy.github.io/Ourty/)"


def get(url, headers=None, timeout=20, limit=8_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(limit + 1)
    if len(data) > limit:
        raise ValueError("file too big")
    return data


def pexels(query):
    key = KEY_FILE.read_text().strip()
    q = urllib.parse.urlencode({"query": query, "orientation": "landscape", "per_page": 12})
    data = json.loads(get(f"https://api.pexels.com/v1/search?{q}", {"Authorization": key}))
    return [{
        "title": p.get("alt") or query,
        "creator": p["photographer"],
        "source_url": p["url"],
        "license": "Pexels License",
        "license_url": "https://www.pexels.com/license/",
        "preview": p["src"]["medium"],
        "full": p["src"]["large2x"],
    } for p in data.get("photos", [])]


def openverse(query):
    rank = {"cc0": 0, "pdm": 0, "by": 1, "by-sa": 2}
    q = urllib.parse.urlencode({"q": query, "license": "cc0,pdm,by,by-sa", "page_size": 20})
    data = json.loads(get(f"https://api.openverse.org/v1/images/?{q}"))
    res = [r for r in data["results"] if (r.get("width") or 0) >= 900 and (r.get("width") or 0) >= (r.get("height") or 0)]
    res.sort(key=lambda r: (rank.get(r["license"], 9) > 1, r["source"] != "flickr", abs((r.get("width") or 0) - 1600)))
    out = []
    for r in res:
        lic = r["license"]
        out.append({
            "title": r.get("title") or query,
            "creator": r.get("creator") or "Unknown",
            "source_url": r.get("foreign_landing_url") or r["url"],
            "license": "Public domain" if lic in ("cc0", "pdm") else f"CC {lic.upper()} {r.get('license_version') or ''}".strip(),
            "license_url": r.get("license_url") or "",
            "preview": r["url"],
            "full": r["url"],
        })
    return out


def search(query):
    results = pexels(query) if KEY_FILE.exists() else openverse(query)
    if CAND.exists():
        shutil.rmtree(CAND)
    CAND.mkdir()
    picked = []
    for r in results:
        if len(picked) == 8:
            break
        try:
            raw = get(r["preview"])
        except Exception:
            continue
        n = len(picked) + 1
        (CAND / f"{n}.jpg").write_bytes(raw)
        picked.append(r)
        print(f"{n}. {r['title'][:70]} | {r['creator']} | {r['license']}")
    (CAND / "meta.json").write_text(json.dumps(picked, indent=1))
    src = "Pexels" if KEY_FILE.exists() else "Openverse (no pexels_key.txt found)"
    print(f"\nSource: {src}. Candidates in {CAND}/ — look at them, then: python3 find_image.py pick <N> <name>")


def pick(n, name):
    meta = json.loads((CAND / "meta.json").read_text())[int(n) - 1]
    IMAGES.mkdir(parents=True, exist_ok=True)
    tmp = CAND / "full.jpg"
    tmp.write_bytes(get(meta["full"]))
    out = IMAGES / f"{name}.jpg"
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", "--resampleWidth", "1600",
                    str(tmp), "--out", str(out)], check=True, capture_output=True)
    print("Add these lines to the article front matter:\n")
    print(f"image: images/{name}.jpg")
    print("image_alt: <describe the photo in a few words>")
    print(f"image_credit: {meta['creator'].replace(':', ' -')}")
    print(f"image_source: {meta['source_url']}")
    print(f"image_license: {meta['license']}")
    print(f"image_license_url: {meta['license_url']}")
    print("\nFor an extra photo inside the article body use:")
    print(f"![<alt text>](images/{name}.jpg) Photo: [{meta['creator']}]({meta['source_url']})")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "search":
        search(a[1])
    elif len(a) == 3 and a[0] == "pick":
        pick(a[1], a[2])
    else:
        print(__doc__)

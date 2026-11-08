#!/usr/bin/env python3
"""Ourty site builder. Only needs Python 3 (no extra packages).

Usage:
  python3 build.py                 Build the public site into docs/
  python3 build.py preview         Build docs/ + drafts into preview/ (for review)
  python3 build.py list            List drafts waiting for review
  python3 build.py publish <slug>  Move a draft to posts (dated today) and rebuild
"""
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- markdown


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", text)

    def link(m):
        label, url = m.group(1), m.group(2).replace('"', "%22")
        ext = url.startswith("http")
        attrs = ' target="_blank" rel="noopener"' if ext else ""
        return f'<a href="{url}"{attrs}>{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)


def markdown(src, root=""):
    out, para, items, list_tag, quote = [], [], [], None, []

    def flush():
        nonlocal para, items, list_tag, quote
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
        if items:
            out.append(f"<{list_tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{list_tag}>")
        if quote:
            out.append("<blockquote><p>" + inline(" ".join(quote)) + "</p></blockquote>")
        para, items, list_tag, quote = [], [], None, []

    for raw in src.splitlines():
        line = raw.rstrip()
        s = line.strip()
        h = re.match(r"^(#{2,4})\s+(.*)", s)
        ul = re.match(r"^[-*]\s+(.*)", s)
        ol = re.match(r"^\d+[.)]\s+(.*)", s)
        img = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)\s*(.*)$", s)
        if not s:
            flush()
        elif img:
            flush()
            alt, url, cap = img.groups()
            url = url if url.startswith("http") else root + url
            caption = f"<figcaption>{inline(cap)}</figcaption>" if cap else ""
            out.append(f'<figure><img src="{url}" alt="{html.escape(alt)}" loading="lazy">{caption}</figure>')
        elif h:
            flush()
            level = len(h.group(1))
            out.append(f'<h{level} id="{slugify(h.group(2))}">{inline(h.group(2))}</h{level}>')
        elif ul or ol:
            tag = "ul" if ul else "ol"
            if para or quote or (list_tag and list_tag != tag):
                flush()
            list_tag = tag
            items.append((ul or ol).group(1))
        elif s.startswith(">"):
            if para or items:
                flush()
            quote.append(s.lstrip("> ").strip())
        elif items and raw.startswith(("  ", "\t")):
            items[-1] += " " + s
        else:
            if items or quote:
                flush()
            para.append(s)
    flush()
    return "\n".join(out)


def read_doc(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    meta["slug"] = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    meta["body"] = body
    meta["path"] = path
    return meta


# ---------------------------------------------------------------- templates


def ad(slot, mode):
    client, unit = SITE.get("adsense_client"), SITE.get("adsense_slot")
    if mode == "preview":
        return f'<div class="ad ad-placeholder">Ad space · {slot}</div>'
    if client and unit:
        return (f'<div class="ad"><ins class="adsbygoogle" style="display:block" data-ad-client="{client}" '
                f'data-ad-slot="{unit}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
                '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>')
    return ""


LANGS = [("es", "Español"), ("fr", "Français"), ("de", "Deutsch"), ("it", "Italiano"),
         ("pt", "Português"), ("ar", "العربية"), ("zh-CN", "中文"), ("hi", "हिन्दी")]


def page(title, body, root, mode, description="", canonical="", extra_head="", image=""):
    cats = SITE["categories"]
    nav = "".join(f'<a href="{root}category/{k}/">{c["label"]}</a>' for k, c in cats.items())
    client = SITE.get("adsense_client")
    ads_head = ""
    if client and mode != "preview":
        ads_head = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={client}" '
                    'crossorigin="anonymous"></script>')
    full_title = f"{title} · {SITE['name']}" if title != SITE["name"] else f"{SITE['name']} · {SITE['tagline']}"
    langs = "".join(f'<option value="{c}">{n}</option>' for c, n in LANGS)
    draft_bar = '<div class="draft-bar">PREVIEW — includes unpublished drafts</div>' if mode == "preview" else ""
    year = datetime.date.today().year
    canon = f'<link rel="canonical" href="{canonical}">' if canonical else ""
    return f"""<!doctype html>
<html lang="{SITE['language']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description or SITE['tagline'])}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description or SITE['tagline'])}">
<meta property="og:site_name" content="{SITE['name']}">
{f'<meta property="og:image" content="{image}">' if image else ''}
{canon}
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{SITE['name']}" href="{root}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css">
{ads_head}
{extra_head}
</head>
<body>
{draft_bar}
<header class="site-header">
  <div class="wrap header-row">
    <a class="logo" href="{root}index.html"><span class="logo-mark">o</span>urty</a>
    <label class="translate">
      <span aria-hidden="true">🌐</span>
      <select aria-label="Translate this page" onchange="if(this.value){{location.href='https://translate.google.com/translate?sl=en&tl='+this.value+'&u='+encodeURIComponent(location.href)}}">
        <option value="">Translate</option>{langs}
      </select>
    </label>
  </div>
  <nav class="wrap cat-nav">{nav}</nav>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p class="footer-brand"><span class="logo-mark small">o</span>urty — {SITE['tagline']}.</p>
    <p class="footer-links"><a href="{root}about/">About</a><a href="{root}disclaimer/">Medical disclaimer</a><a href="{root}privacy/">Privacy</a><a href="{root}contact/">Contact</a><a href="{root}feed.xml">RSS</a></p>
    <p class="fine">Content on Ourty is for general information only and is not a substitute for professional medical advice. © {year} {SITE['name']}.</p>
  </div>
</footer>
</body>
</html>
"""


def fmt_date(d):
    try:
        return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")
    except (ValueError, TypeError):
        return d or ""


def reading_time(body):
    return max(1, round(len(body.split()) / 220))


def img_url(src, root):
    return src if src.startswith("http") else root + src


def card(p, root):
    c = SITE["categories"].get(p["category"], {"label": p["category"], "emoji": "✨", "color": "#eee"})
    draft = '<span class="badge-draft">Draft</span>' if p.get("draft") else ""
    if p.get("image"):
        art = f'<img src="{img_url(p["image"], root)}" alt="{html.escape(p.get("image_alt", ""))}" loading="lazy">'
    else:
        art = f'<span>{p.get("emoji") or c["emoji"]}</span>'
    return f"""<article class="card">
  <a href="{root}posts/{p['slug']}/" class="card-art" style="background:{c['color']}">{art}</a>
  <div class="card-body">
    <p class="meta"><a href="{root}category/{p['category']}/">{c['label']}</a> · {reading_time(p['body'])} min read {draft}</p>
    <h2><a href="{root}posts/{p['slug']}/">{html.escape(p['title'])}</a></h2>
    <p>{html.escape(p.get('description', ''))}</p>
  </div>
</article>"""


# ---------------------------------------------------------------- build


def write(out, rel, text):
    f = out / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


def load_posts(include_drafts):
    (CONTENT / "posts").mkdir(parents=True, exist_ok=True)
    (CONTENT / "drafts").mkdir(parents=True, exist_ok=True)
    posts = [read_doc(p) for p in sorted((CONTENT / "posts").glob("*.md"))]
    if include_drafts:
        for p in sorted((CONTENT / "drafts").glob("*.md")):
            d = read_doc(p)
            d["draft"] = True
            d.setdefault("date", datetime.date.today().isoformat())
            posts.append(d)
    return sorted(posts, key=lambda p: (p.get("date", ""), p["slug"]), reverse=True)


def build(mode="public"):
    out = ROOT / ("preview" if mode == "preview" else "docs")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    for f in STATIC.iterdir():
        shutil.copy(f, out / f.name)
    if (CONTENT / "images").exists():
        shutil.copytree(CONTENT / "images", out / "images")

    base = SITE["base_url"].rstrip("/")
    posts = load_posts(include_drafts=(mode == "preview"))
    cats = SITE["categories"]

    # home
    if posts:
        lead, rest = posts[0], posts[1:]
        hero = f"""<section class="hero">
  <p class="eyebrow">{SITE['tagline']}</p>
  <h1>Feel a little better, <em>every day.</em></h1>
  <p class="lede">Practical guides on food, movement, sleep and a calmer mind — written in plain English, with sources you can check.</p>
</section>
<section class="lead-post">{card(lead, '')}</section>
{ad('home-top', mode)}
<section class="grid">{''.join(card(p, '') for p in rest[:12])}</section>"""
    else:
        hero = '<section class="hero"><h1>Coming soon.</h1></section>'
    write(out, "index.html", page(SITE["name"], hero, "", mode, canonical=base + "/"))

    # posts
    for p in posts:
        r = "../../"
        c = cats.get(p["category"], {"label": p["category"], "emoji": "✨", "color": "#eee"})
        body_html = markdown(p["body"], r)
        hero_img = ""
        if p.get("image"):
            credit = p.get("image_credit", "")
            if p.get("image_source"):
                credit = f'<a href="{p["image_source"]}" target="_blank" rel="noopener">{html.escape(credit)}</a>'
            lic = p.get("image_license", "")
            if lic and p.get("image_license_url"):
                lic = f'<a href="{p["image_license_url"]}" target="_blank" rel="noopener">{lic}</a>'
            cap = f"Photo: {credit}" + (f" · {lic}" if lic else "") if credit else ""
            hero_img = (f'<figure class="hero-img"><img src="{img_url(p["image"], r)}" alt="{html.escape(p.get("image_alt", ""))}">'
                        + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")
        # put an ad after the 3rd paragraph
        parts = body_html.split("</p>", 3)
        if len(parts) == 4:
            body_html = "</p>".join(parts[:3]) + "</p>" + ad("in-article", mode) + parts[3]
        related = [q for q in posts if q["category"] == p["category"] and q["slug"] != p["slug"]][:3]
        if len(related) < 3:
            related += [q for q in posts if q not in related and q["slug"] != p["slug"]][: 3 - len(related)]
        draft_note = '<p class="draft-note">This is a draft — not visible on the public site.</p>' if p.get("draft") else ""
        schema = json.dumps({
            "@context": "https://schema.org", "@type": "Article", "headline": p["title"],
            "description": p.get("description", ""), "datePublished": p.get("date", ""),
            "author": {"@type": "Organization", "name": SITE["author"]},
            "publisher": {"@type": "Organization", "name": SITE["name"]},
        })
        body = f"""<article class="post">
  {draft_note}
  <header class="post-head">
    <p class="meta"><a href="{r}category/{p['category']}/">{c['emoji']} {c['label']}</a></p>
    <h1>{html.escape(p['title'])}</h1>
    <p class="lede">{html.escape(p.get('description', ''))}</p>
    <p class="byline">By {SITE['author']} · {fmt_date(p.get('date'))} · {reading_time(p['body'])} min read</p>
  </header>
  {hero_img}
  <div class="prose">{body_html}</div>
  <aside class="disclaimer"><strong>Health note:</strong> this article is general information, not medical advice. Talk to a doctor or qualified professional before making changes to your diet, exercise or medication — especially if you are pregnant or have a health condition.</aside>
  {ad('after-article', mode)}
</article>
<section class="related"><h2>Keep reading</h2><div class="grid">{''.join(card(q, r) for q in related)}</div></section>"""
        write(out, f"posts/{p['slug']}/index.html",
              page(p["title"], body, r, mode, p.get("description", ""), f"{base}/posts/{p['slug']}/",
                   f'<script type="application/ld+json">{schema}</script>',
                   img_url(p["image"], base + "/") if p.get("image") else ""))

    # categories
    for k, c in cats.items():
        items = [p for p in posts if p["category"] == k]
        grid = "".join(card(p, "../../") for p in items) or '<p class="empty">New articles coming soon.</p>'
        body = f"""<section class="cat-head" style="background:{c['color']}"><span>{c['emoji']}</span><h1>{c['label']}</h1></section>
<section class="grid">{grid}</section>"""
        write(out, f"category/{k}/index.html", page(c["label"], body, "../../", mode, canonical=f"{base}/category/{k}/"))

    # static pages
    for f in sorted((CONTENT / "pages").glob("*.md")):
        d = read_doc(f)
        body = f'<article class="post"><header class="post-head"><h1>{html.escape(d["title"])}</h1></header><div class="prose">{markdown(d["body"], "../")}</div></article>'
        write(out, f"{d['slug']}/index.html", page(d["title"], body, "../", mode, d.get("description", ""), f"{base}/{d['slug']}/"))

    # feeds & SEO files (public only)
    if mode != "preview":
        urls = [base + "/"] + [f"{base}/posts/{p['slug']}/" for p in posts] + [f"{base}/category/{k}/" for k in cats]
        urls += [f"{base}/{read_doc(f)['slug']}/" for f in (CONTENT / "pages").glob("*.md")]
        write(out, "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
              + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
        write(out, "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
        items = "".join(
            f"<item><title>{html.escape(p['title'])}</title><link>{base}/posts/{p['slug']}/</link>"
            f"<guid>{base}/posts/{p['slug']}/</guid><description>{html.escape(p.get('description', ''))}</description></item>"
            for p in posts[:20])
        write(out, "feed.xml", f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{SITE["name"]}</title>'
              f'<link>{base}/</link><description>{html.escape(SITE["tagline"])}</description>{items}</channel></rss>')
        if SITE.get("adsense_client"):
            pub = SITE["adsense_client"].replace("ca-", "")
            write(out, "ads.txt", f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n")
        if SITE.get("custom_domain"):
            write(out, "CNAME", SITE["custom_domain"] + "\n")
        write(out, ".nojekyll", "")
    print(f"Built {len(posts)} articles into {out.name}/")


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "build"
    if cmd == "build":
        build("public")
    elif cmd == "preview":
        build("public")
        build("preview")
    elif cmd == "list":
        drafts = sorted((CONTENT / "drafts").glob("*.md"))
        print("\n".join(f"- {read_doc(d)['slug']}: {read_doc(d)['title']}" for d in drafts) or "No drafts.")
    elif cmd == "publish" and len(args) == 2:
        src = CONTENT / "drafts" / f"{args[1]}.md"
        if not src.exists():
            sys.exit(f"No draft named {args[1]}")
        today = datetime.date.today().isoformat()
        text = src.read_text(encoding="utf-8")
        text = re.sub(r"^date:.*$", f"date: {today}", text, count=1, flags=re.M) if re.search(r"^date:", text, re.M) \
            else text.replace("---\n", f"---\ndate: {today}\n", 1)
        (CONTENT / "posts").mkdir(parents=True, exist_ok=True)
        (CONTENT / "posts" / f"{today}-{args[1]}.md").write_text(text, encoding="utf-8")
        src.unlink()
        build("public")
        print(f"Published {args[1]}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

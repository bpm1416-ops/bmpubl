#!/usr/bin/env python3
"""Generate static blog pages from local drafts.

The external CMS (Soro) is no longer used. Blog articles are authored
directly as local draft files and turned into static HTML by this script.

Workflow for a new post:
  1. Drop a hero image into blogentwürfe/ (jpg/jpeg/png/webp). Its filename
     should either match the draft's filename, or match the article's slug
     (the slugified title), optionally followed by "-<number>" (e.g. an
     image generator's default suffix).
  2. Drop a draft .txt file into blogentwürfe/ with this shape:
       Line 1:  the article title (plain text)
       Line 2:  blank
       Line 3+: the article body as ready-to-use HTML (<p>, <h2>, <ul>, ...),
                exactly what should end up inside <div class="blog-article-body">.
  3. Run:
       python3 scripts/generate_blog.py

The script picks up any draft whose slug isn't already known, converts its
hero image to WEBP, writes blog/<slug>.html, records the article in
blog/articles.json (the persistent index that replaces the old Soro feed),
and regenerates blog.html and the blog entries in sitemap.xml from that
index. Already-published articles are left untouched; only new drafts are
processed, but blog.html/sitemap.xml are always fully rebuilt from the index
so they stay in sync.

On first run (no blog/articles.json yet), the index is bootstrapped by
reading the metadata already embedded in the existing blog/*.html pages, so
nothing has to be re-entered by hand.
"""
import html
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "blog"
IMAGES_DIR = ROOT / "images" / "blog"
DRAFTS_DIR = ROOT / "blogentwürfe"
MANIFEST_PATH = BLOG_DIR / "articles.json"
SITE = "https://liederbuecher.com"

WEBP_QUALITY = 82
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

GERMAN_MONTHS = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]

HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-V6GKLQ4KW3"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-V6GKLQ4KW3');
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{css_path}css/style.css">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{image}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Liederbücher für Alt und Jung">
  <meta property="og:locale" content="de_DE">
  <link rel="canonical" href="{url}">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": {headline_json},
    "datePublished": "{iso_date}",
    "image": "{image}",
    "author": {{ "@type": "Person", "name": "Sebastian Müller" }},
    "publisher": {{ "@type": "Organization", "name": "Schott Music" }}
  }}
  </script>
</head>
<body>

  <header class="site-header">
    <div class="container header-inner">
      <a href="{root}index.html" class="logo">
        <span class="logo-text">Liederbücher<small>für Alt und Jung</small></span>
      </a>
      <button class="nav-toggle" aria-label="Menü öffnen" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <nav class="site-nav" id="site-nav">
        <ul>
          <li><a href="{root}index.html">Home</a></li>
          <li class="has-dropdown">
            <a href="#">Bücher ▾</a>
            <ul class="dropdown">
              <li><a href="{root}fetenbuch.html">Das Fetenbuch</a></li>
              <li><a href="{root}rock-pop.html">Das Rock &amp; Pop Fetenbuch</a></li>
              <li><a href="{root}rock-pop-2.html">Das Rock &amp; Pop Fetenbuch 2</a></li>
              <li><a href="{root}folk.html">Das Folk- und Volksliederbuch</a></li>
              <li><a href="{root}schlagerbuch.html">Das Schlagerbuch</a></li>
              <li><a href="{root}kinderliederbuch.html">Das Kinderliederbuch</a></li>
              <li><a href="{root}weihnachten.html">Das Weihnachtsliederbuch</a></li>
            </ul>
          </li>
          <li><a href="{root}blog.html">Blog</a></li>
          <li><a href="{root}autor.html">Über den Autor</a></li>
        </ul>
      </nav>
    </div>
  </header>
"""

FOOTER_TEMPLATE = """
  <footer class="site-footer">
    <div class="container">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="logo-text">Liederbücher<br><small>für Alt und Jung</small></span>
          <p>Sing mit! – Liederbücher für gemeinsames Musizieren, herausgegeben bei Schott Music.</p>
        </div>
        <div class="footer-nav">
          <h4>Bücher</h4>
          <ul>
            <li><a href="{root}fetenbuch.html">Das Fetenbuch</a></li>
            <li><a href="{root}rock-pop.html">Rock &amp; Pop Fetenbuch</a></li>
            <li><a href="{root}rock-pop-2.html">Rock &amp; Pop Fetenbuch 2</a></li>
            <li><a href="{root}folk.html">Folk- und Volksliederbuch</a></li>
            <li><a href="{root}schlagerbuch.html">Das Schlagerbuch</a></li>
            <li><a href="{root}kinderliederbuch.html">Das Kinderliederbuch</a></li>
            <li><a href="{root}weihnachten.html">Weihnachtsliederbuch</a></li>
          </ul>
        </div>
        <div class="footer-nav">
          <h4>Info</h4>
          <ul>
            <li><a href="{root}autor.html">Über den Autor</a></li>
            <li><a href="{root}blog.html">Blog</a></li>
            <li><a href="{root}datenschutz.html">Datenschutz</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2025 Bernhard Müller · liederbuecher.com</p>
        <div class="footer-bottom-links">
          <a href="{root}impressum.html">Impressum</a>
          <a href="{root}datenschutz.html">Datenschutz</a>
          <a href="{root}kontakt.html">Kontakt</a>
        </div>
      </div>
    </div>
  </footer>

  <script src="{root}js/main.js"></script>
</body>
</html>
"""


def slugify(title):
    text = title.lower()
    for umlaut, replacement in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(umlaut, replacement)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    if len(text) > 80:
        text = text[:80].rsplit("-", 1)[0]
    return text


def format_date_de(dt):
    return f"{dt.day}. {GERMAN_MONTHS[dt.month - 1]} {dt.year}"


def truncate(text, length=155):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= length:
        return text
    return text[: length - 1].rsplit(" ", 1)[0] + "…"


def extract_excerpt(body_html):
    match = re.search(r"<p>(.*?)</p>", body_html, re.S)
    text = match.group(1) if match else body_html
    text = re.sub(r"<[^>]+>", "", text)
    return truncate(html.unescape(text))


def parse_draft(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].strip()
    body_lines = lines[1:]
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    return title, "\n".join(body_lines).strip()


def find_hero_image(draft_path, slug):
    candidates = [p for p in DRAFTS_DIR.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS]
    for p in candidates:
        if p.stem == draft_path.stem:
            return p
    pattern = re.compile(rf"^{re.escape(slug)}(-\d+)?$", re.I)
    for p in candidates:
        if pattern.match(p.stem):
            return p
    return None


def convert_hero_image(src_path, slug):
    dest_path = IMAGES_DIR / f"{slug}.webp"
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    if src_path.suffix.lower() == ".webp":
        shutil.copy(src_path, dest_path)
    else:
        subprocess.run(
            ["cwebp", "-q", str(WEBP_QUALITY), str(src_path), "-o", str(dest_path)],
            check=True, capture_output=True,
        )
    return dest_path


def bootstrap_manifest():
    """Rebuild blog/articles.json from the metadata already baked into existing blog/*.html pages."""
    articles = []
    for page_path in sorted(BLOG_DIR.glob("*.html")):
        text = page_path.read_text(encoding="utf-8")
        slug = page_path.stem
        title_m = re.search(r"<h1>(.*?)</h1>", text, re.S)
        desc_m = re.search(r'<meta name="description" content="(.*?)">', text)
        iso_m = re.search(r'"datePublished":\s*"([^"]+)"', text)
        date_disp_m = re.search(r'<p class="blog-article-date">(.*?)</p>', text, re.S)
        if not (title_m and desc_m and iso_m and date_disp_m):
            print(f"WARNING: could not bootstrap metadata for {page_path.name}, skipping.")
            continue
        articles.append({
            "slug": slug,
            "title": html.unescape(title_m.group(1).strip()),
            "iso_date": iso_m.group(1),
            "date_display": html.unescape(date_disp_m.group(1).strip()),
            "excerpt": html.unescape(desc_m.group(1).strip()),
        })
    articles.sort(key=lambda a: a["iso_date"], reverse=True)
    return articles


def load_manifest():
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest = bootstrap_manifest()
    print(f"Bootstrapped blog/articles.json from {len(manifest)} existing pages.")
    return manifest


def save_manifest(manifest):
    manifest.sort(key=lambda a: a["iso_date"], reverse=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def image_url(slug):
    return f"{SITE}/images/blog/{slug}.webp"


def article_url(slug):
    return f"{SITE}/blog/{slug}.html"


def render_article_page(article, body_html):
    title = f"{article['title']} – Liederbücher für Alt und Jung Blog"
    url = article_url(article["slug"])
    image = image_url(article["slug"])
    head = HEAD_TEMPLATE.format(
        title=html.escape(title),
        description=html.escape(article["excerpt"]),
        css_path="../",
        image=image,
        url=url,
        headline_json=json.dumps(article["title"]),
        iso_date=article["iso_date"],
        root="../",
    )
    footer = FOOTER_TEMPLATE.format(root="../")
    body = f"""
  <div class="contact-section">
    <div class="container">
      <article class="blog-article">
        <a href="../blog.html" class="blog-article-back">← Zurück zum Blog</a>
        <h1>{html.escape(article['title'])}</h1>
        <p class="blog-article-date">{html.escape(article['date_display'])}</p>
        <img class="blog-article-img" src="{image}" alt="{html.escape(article['title'])}">
        <div class="blog-article-body">
          {body_html}
        </div>
      </article>
    </div>
  </div>
"""
    return head + body + footer


def render_index(articles):
    title = "Blog – Liederbücher für Alt und Jung"
    description = "Blog rund um die Liederbücher für Alt und Jung – Neuigkeiten, Tipps und Wissenswertes über gemeinsames Singen und Musizieren."
    head = HEAD_TEMPLATE.format(
        title=html.escape(title),
        description=html.escape(description),
        css_path="",
        image=f"{SITE}/images/covers/fetenbuch.jpg",
        url=f"{SITE}/blog.html",
        headline_json=json.dumps(title),
        iso_date=articles[0]["iso_date"] if articles else "",
        root="",
    )
    # plain listing page doesn't need the BlogPosting JSON-LD; strip it out
    head = head.replace(
        head[head.index('<script type="application/ld+json">'):head.index("</script>\n</head>") + len("</script>\n")],
        "",
    )
    footer = FOOTER_TEMPLATE.format(root="")

    cards = []
    for a in articles:
        cards.append(f"""
        <a class="blog-card" href="blog/{a['slug']}.html">
          <img class="blog-card-img" src="{image_url(a['slug'])}" alt="{html.escape(a['title'])}" loading="lazy">
          <div class="blog-card-body">
            <h2>{html.escape(a['title'])}</h2>
            <p>{html.escape(a['excerpt'])}</p>
            <span class="blog-card-date">{html.escape(a['date_display'])}</span>
          </div>
        </a>""")

    body = f"""
  <div class="contact-section">
    <div class="container">
      <div class="page-intro">
        <h1>Blog</h1>
        <p>Neuigkeiten, Tipps und Wissenswertes rund um die Liederbücher für Alt und Jung.</p>
      </div>

      <div class="blog-grid">{''.join(cards)}
      </div>
    </div>
  </div>
"""
    return head + body + footer


def update_sitemap(articles):
    sitemap_path = ROOT / "sitemap.xml"
    text = sitemap_path.read_text(encoding="utf-8")
    entries = []
    for a in articles:
        entries.append(
            f"  <url>\n"
            f"    <loc>{article_url(a['slug'])}</loc>\n"
            f"    <lastmod>{a['iso_date'][:10]}</lastmod>\n"
            f"    <changefreq>yearly</changefreq>\n"
            f"    <priority>0.5</priority>\n"
            f"  </url>\n"
        )
    text = re.sub(
        r"\s*<!-- BEGIN GENERATED BLOG URLS -->.*?<!-- END GENERATED BLOG URLS -->\n",
        "\n",
        text,
        flags=re.S,
    )
    block = "  <!-- BEGIN GENERATED BLOG URLS -->\n" + "".join(entries) + "  <!-- END GENERATED BLOG URLS -->\n"
    text = text.replace("</urlset>", block + "</urlset>")
    sitemap_path.write_text(text, encoding="utf-8")


def find_new_drafts(manifest):
    known_slugs = {a["slug"] for a in manifest}
    drafts = []
    if not DRAFTS_DIR.exists():
        return drafts
    for txt_path in sorted(DRAFTS_DIR.glob("*.txt")):
        title, body_html = parse_draft(txt_path)
        if not title or title.startswith("<") or len(title) > 140:
            print(f"WARNING: '{txt_path.name}' doesn't start with a plain-text title line - skipping "
                  f"(expected line 1 = title, blank line, then the HTML body).")
            continue
        slug = slugify(title)
        if slug in known_slugs or (BLOG_DIR / f"{slug}.html").exists():
            continue
        drafts.append((txt_path, title, body_html, slug))
    return drafts


def main():
    BLOG_DIR.mkdir(exist_ok=True)
    manifest = load_manifest()

    for txt_path, title, body_html, slug in find_new_drafts(manifest):
        image_src = find_hero_image(txt_path, slug)
        if image_src is None:
            print(f"WARNING: no hero image found in blogentwürfe/ for draft '{txt_path.name}' (slug '{slug}') - skipping.")
            continue

        convert_hero_image(image_src, slug)
        now = datetime.now()
        article = {
            "slug": slug,
            "title": title,
            "iso_date": now.strftime("%Y-%m-%dT10:00:00.00+00:00"),
            "date_display": format_date_de(now),
            "excerpt": extract_excerpt(body_html),
        }
        page = render_article_page(article, body_html)
        (BLOG_DIR / f"{slug}.html").write_text(page, encoding="utf-8")
        manifest.append(article)
        print(f"wrote blog/{slug}.html")

    save_manifest(manifest)

    (ROOT / "blog.html").write_text(render_index(manifest), encoding="utf-8")
    print("wrote blog.html (static index)")

    update_sitemap(manifest)
    print("updated sitemap.xml")


if __name__ == "__main__":
    main()

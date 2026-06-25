#!/usr/bin/env python3
"""Generate static blog pages from the Soro embed feed.

Soro (app.trysoro.com) only renders blog content client-side, so the
articles are invisible to a first-pass crawl and never get individual
title/meta tags. This script pulls the article list + full content from
Soro's public embed API and writes them out as plain static HTML pages
under blog/, plus a static index on blog.html and entries in sitemap.xml.

Run after publishing new posts in Soro:
    python3 scripts/generate_blog.py
"""
import html
import json
import re
import urllib.request
from pathlib import Path

SORO_TOKEN = "943b7d5e-fd3e-4f5e-aac7-19f2485b5e20"
EMBED_URL = f"https://app.trysoro.com/api/embed/{SORO_TOKEN}"
ARTICLE_URL = f"https://app.trysoro.com/api/embed/{SORO_TOKEN}/article/{{id}}"

ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT / "blog"
IMAGES_DIR = ROOT / "images" / "blog"
SITE = "https://bmpubl.com"

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
        <p>&copy; 2025 Bernhard Müller · bmpubl.com</p>
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


def fetch(url):
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8")


def load_articles():
    js = fetch(EMBED_URL)
    match = re.search(r"var SORO_ARTICLES = (\[.*?\]);", js, re.S)
    if not match:
        raise RuntimeError("Could not find SORO_ARTICLES in embed script")
    return json.loads(match.group(1))


def localize_image(article):
    """Download the article's hero image so the site doesn't depend on Soro's storage."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    local_path = IMAGES_DIR / f"{article['slug']}.webp"
    if not local_path.exists():
        with urllib.request.urlopen(article["image"]) as resp:
            local_path.write_bytes(resp.read())
    article["image"] = f"{SITE}/images/blog/{article['slug']}.webp"


def truncate(text, length=160):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= length:
        return text
    return text[: length - 1].rsplit(" ", 1)[0] + "…"


def render_article_page(article, content_html):
    title = f"{article['title']} – Liederbücher für Alt und Jung Blog"
    description = truncate(article["excerpt"])
    url = f"{SITE}/blog/{article['slug']}.html"
    head = HEAD_TEMPLATE.format(
        title=html.escape(title),
        description=html.escape(description),
        css_path="../",
        image=article["image"],
        url=url,
        headline_json=json.dumps(article["title"]),
        iso_date=article["isoDate"],
        root="../",
    )
    footer = FOOTER_TEMPLATE.format(root="../")
    body = f"""
  <div class="contact-section">
    <div class="container">
      <article class="blog-article">
        <a href="../blog.html" class="blog-article-back">← Zurück zum Blog</a>
        <h1>{html.escape(article['title'])}</h1>
        <p class="blog-article-date">{html.escape(article['date'])}</p>
        <img class="blog-article-img" src="{article['image']}" alt="{html.escape(article['title'])}">
        <div class="blog-article-body">
          {content_html}
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
        iso_date=articles[0]["isoDate"] if articles else "",
        root="",
    )
    # plain head doesn't need the BlogPosting JSON-LD; swap to a simple page block instead
    head = head.replace(
        head[head.index('<script type="application/ld+json">'):head.index("</script>\n</head>") + len("</script>\n")],
        "",
    )
    footer = FOOTER_TEMPLATE.format(root="")

    cards = []
    for a in articles:
        cards.append(f"""
        <a class="blog-card" href="blog/{a['slug']}.html">
          <img class="blog-card-img" src="{a['image']}" alt="{html.escape(a['title'])}" loading="lazy">
          <div class="blog-card-body">
            <h2>{html.escape(a['title'])}</h2>
            <p>{html.escape(a['excerpt'])}</p>
            <span class="blog-card-date">{html.escape(a['date'])}</span>
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
    text = sitemap_path.read_text()
    entries = []
    for a in articles:
        entries.append(
            f"  <url>\n"
            f"    <loc>{SITE}/blog/{a['slug']}.html</loc>\n"
            f"    <lastmod>{a['isoDate'][:10]}</lastmod>\n"
            f"    <changefreq>yearly</changefreq>\n"
            f"    <priority>0.5</priority>\n"
            f"  </url>\n"
        )
    # remove any previously generated blog entries (marked with comment), then re-insert
    text = re.sub(
        r"\s*<!-- BEGIN GENERATED BLOG URLS -->.*?<!-- END GENERATED BLOG URLS -->\n",
        "\n",
        text,
        flags=re.S,
    )
    block = "  <!-- BEGIN GENERATED BLOG URLS -->\n" + "".join(entries) + "  <!-- END GENERATED BLOG URLS -->\n"
    text = text.replace("</urlset>", block + "</urlset>")
    sitemap_path.write_text(text)


def main():
    BLOG_DIR.mkdir(exist_ok=True)
    articles = load_articles()
    articles.sort(key=lambda a: a["isoDate"], reverse=True)

    for article in articles:
        localize_image(article)
        content_json = fetch(ARTICLE_URL.format(id=article["id"]))
        content_html = json.loads(content_json)["content"]
        page = render_article_page(article, content_html)
        (BLOG_DIR / f"{article['slug']}.html").write_text(page)
        print(f"wrote blog/{article['slug']}.html")

    (ROOT / "blog.html").write_text(render_index(articles))
    print("wrote blog.html (static index)")

    update_sitemap(articles)
    print("updated sitemap.xml")


if __name__ == "__main__":
    main()

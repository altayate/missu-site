#!/usr/bin/env python3
"""Build and validate the dependency-free GitHub Pages website."""
import argparse
import html
import json
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "site.json").read_text())
OUT = ROOT / "docs"
PAGES = {
    "": ("A little closer, every day.", "Small moments for two. Photos, a shared canvas, and a little reminder that you’re thinking of them."),
    "privacy": ("Privacy policy", "How Miss-U handles your information, shared moments, and choices."),
    "terms": ("Terms of use", "The terms for using Miss-U and its optional paid features."),
    "support": ("Here to help.", "A little guidance for your moments together."),
    "delete-account": ("Delete your account", "How to leave Miss-U and what happens to your data."),
}


def render(slug, title, description, content, missing=False):
    prefix = CONFIG["url"] if missing else ("../" if slug else "./")
    esc = html.escape
    nav = "".join(
        f'<a href="{prefix}{path}/"' + (' aria-current="page"' if slug == path else '') + f'>{label}</a>'
        for path, label in [("privacy", "Privacy"), ("terms", "Terms"), ("support", "Support")]
    )
    canonical = CONFIG["url"] + (slug + "/" if slug and not missing else "")
    content = content.replace("{{developer}}", esc(CONFIG["developer"])).replace("{{email}}", esc(CONFIG["email"]))
    content = content.replace("{{base}}", prefix)
    legal = slug in {"privacy", "terms"}
    updated = date.fromisoformat(CONFIG["updated"]).strftime("%d %B %Y").lstrip("0")
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · {esc(CONFIG["name"])}</title>
  <meta name="description" content="{esc(description, quote=True)}">
  <meta name="theme-color" content="#fff8f8">
  {('<meta name="robots" content="noindex">' if missing else f'<link rel="canonical" href="{canonical}">')}
  <meta property="og:title" content="{esc(title, quote=True)} · Miss-U">
  <meta property="og:description" content="{esc(description, quote=True)}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{CONFIG["url"]}assets/app-icon.png">
  <link rel="icon" type="image/png" href="{prefix}assets/app-icon.png">
  <link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header wrap">
    <a class="brand" href="{prefix}" aria-label="Miss-U home"><img src="{prefix}assets/app-icon.png" width="40" height="40" alt=""><span>Miss-U</span></a>
    <nav aria-label="Main navigation">{nav}</nav>
  </header>
  <main id="main" class="wrap {'legal' if legal else ''}">
    <div class="page-intro">
      <p class="eyebrow">{'OUR COMMITMENT TO YOU' if legal else 'LITTLE MOMENTS. JUST US.'}</p>
      <h1>{esc(title)}</h1>
      <p class="lede">{esc(description)}</p>
      {f'<p class="updated">Effective and last updated: <time datetime="{CONFIG["updated"]}">{updated}</time></p>' if legal else ''}
    </div>
    {content}
  </main>
  <footer class="site-footer wrap">
    <p>Made for a little more togetherness.</p>
    <nav aria-label="Footer navigation">
      <a href="{prefix}privacy/">Privacy</a><a href="{prefix}terms/">Terms</a><a href="{prefix}support/">Support</a><a href="{prefix}delete-account/">Account deletion</a>
    </nav>
    <p class="fine">© {CONFIG["updated"][:4]} {esc(CONFIG["developer"])} · <a href="mailto:{esc(CONFIG["email"])}">{esc(CONFIG["email"])}</a></p>
  </footer>
</body>
</html>
'''


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.headings = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.headings += 1
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])


def validate():
    pages = {}
    for path in OUT.rglob("*.html"):
        markup = path.read_text()
        assert "{{" not in markup and "}}" not in markup, f"Unresolved content in {path}"
        parser = Links()
        parser.feed(markup)
        assert parser.headings == 1, f"Expected one main heading in {path}"
        pages[path.resolve()] = parser
    for path, parser in pages.items():
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                assert url.scheme in {"https", "mailto"}, f"Unexpected URL: {link}"
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            assert target.is_relative_to(OUT.resolve()), f"Link escapes website: {link}"
            if target.is_dir():
                target /= "index.html"
            assert target.exists(), f"Broken link in {path}: {link}"
            if url.fragment:
                assert target in pages and url.fragment in pages[target].ids, f"Missing anchor: {link}"
    print(f"Validated {len(pages)} pages: local links, anchors, assets, headings, and content substitutions.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated pages are current without changing files")
    args = parser.parse_args()
    assert CONFIG["url"].startswith("https://") and CONFIG["url"].endswith("/")
    assert "@" in CONFIG["email"] and CONFIG["developer"]
    generated = {}
    for slug, (title, description) in PAGES.items():
        generated[OUT / slug / "index.html"] = render(slug, title, description, (ROOT / "content" / (slug or "home")).with_suffix(".html").read_text())
    generated[OUT / "404.html"] = render("404", "A little lost?", "This page isn’t here, but we can get you back.", '<p><a class="button" href="{{base}}">Back to Miss-U</a></p>', missing=True)
    generated[OUT / ".nojekyll"] = ""
    generated[OUT / "robots.txt"] = f'User-agent: *\nAllow: /\nSitemap: {CONFIG["url"]}sitemap.xml\n'
    urls = "".join(f'<url><loc>{CONFIG["url"]}{slug + "/" if slug else ""}</loc><lastmod>{CONFIG["updated"]}</lastmod></url>' for slug in PAGES)
    generated[OUT / "sitemap.xml"] = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'
    generated[OUT / "assets" / "style.css"] = (ROOT / "assets" / "style.css").read_text()
    for path, markup in generated.items():
        if args.check:
            assert path.exists() and path.read_text() == markup, f"Run python3 build.py to update {path}"
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(markup)
    validate()


if __name__ == "__main__":
    main()

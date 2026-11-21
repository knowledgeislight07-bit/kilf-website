#!/usr/bin/env python3
"""Tiny static-site builder for knowledgeislight.us — no dependencies.

    python3 build.py            # builds into ./dist
    python3 build.py --serve    # builds, then serves dist/ on http://localhost:8000

How it works
------------
* Every page lives in src/pages/ as an HTML fragment. It starts with a
  <!--meta { ...json... } --> block (title, description, URL path, etc.).
* Each fragment is wrapped in src/_layout.html (header, nav, footer, SEO tags).
* {{name}} placeholders are filled from site.json and the page's meta block,
  e.g. {{email}}, {{forms.year1}}, {{academic_year}}.
* {{#if name}} ... {{else}} ... {{/if}} shows a section only when a value is set.
* sitemap.xml and robots.txt are generated automatically.
"""
import json
import os
import re
from urllib.parse import urlparse
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "dist"

META_RE = re.compile(r"^\s*<!--meta\s*(\{.*?\})\s*-->", re.S)
IF_RE = re.compile(r"\{\{#if ([\w.]+)\}\}(.*?)(?:\{\{else\}\}(.*?))?\{\{/if\}\}", re.S)
VAR_RE = re.compile(r"\{\{([\w.]+)\}\}")
NAV_RE = re.compile(r"\{\{nav:(\w+)\}\}")

# The site's signature: a pointed (mihrab) arch drawn as one gold hairline.
# {{arch_line}} frames an arch image; {{arch_mark}} is the small inline mark.
ARCH_PATH = "M0 500V196C0 104 92 44 200 0c108 44 200 104 200 196v304"
ARCH_LINE = ('<svg class="arch-line" viewBox="0 0 400 500" preserveAspectRatio="none" aria-hidden="true">'
             f'<path d="{ARCH_PATH}"/></svg>')
ARCH_MARK = ('<svg class="arch-mark" viewBox="0 0 14 18" aria-hidden="true">'
             '<path d="M1 17.5V7.4C1 4.3 4 2.2 7 .8c3 1.4 6 3.5 6 6.6v10.1"/></svg>')


def lookup(ctx, key):
    cur = ctx
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def render(text, ctx):
    # conditionals first (non-nested), repeated until none remain
    while True:
        new = IF_RE.sub(lambda m: m.group(2) if lookup(ctx, m.group(1)) else (m.group(3) or ""), text)
        if new == text:
            break
        text = new

    def var(m):
        val = lookup(ctx, m.group(1))
        if val is None:
            raise KeyError(f"Unknown placeholder {{{{{m.group(1)}}}}}")
        return str(val)

    return VAR_RE.sub(var, text)


def asset_hash(rel):
    """Short content hash so browsers re-download CSS/JS whenever they change."""
    import hashlib
    return hashlib.sha1((SRC / rel).read_bytes()).hexdigest()[:8]


def breadcrumb_ld(site, crumbs):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": site["site_url"] + path}
            for i, (name, path) in enumerate(crumbs)
        ],
    }


def org_ld(site):
    return {
        "@context": "https://schema.org",
        "@type": ["EducationalOrganization", "NGO"],
        "@id": site["site_url"] + "/#organization",
        "name": site["site_name"],
        "alternateName": ["Knowledge Is Light", "KILF"],
        "url": site["site_url"] + "/",
        "logo": site["site_url"] + "/assets/img/logo-512.png",
        "image": site["site_url"] + "/assets/img/og-image.jpg",
        "description": "A Florida 501(c)(3) nonprofit offering online Quran and Islamic Studies "
                       "education, mentoring, and community programs for Muslim women and girls.",
        "email": site["email"],
        "telephone": site["phone_e164"],
        "foundingDate": "2023",
        "nonprofitStatus": "Nonprofit501c3",
        "areaServed": "United States",
        "address": {"@type": "PostalAddress", "addressRegion": "FL", "addressCountry": "US"},
        "founder": {"@type": "Person", "name": "Sabrina Ahmed"},
    }


def main():
    site = json.loads((ROOT / "site.json").read_text())
    layout = (SRC / "_layout.html").read_text()
    # Preview mode (e.g. GitHub Pages concept): PREVIEW_URL=https://user.github.io/repo
    # serves the site under that URL/subpath and tells search engines not to index it.
    preview_url = os.environ.get("PREVIEW_URL", "").rstrip("/")
    site_url = preview_url or site["site_url"].rstrip("/")
    site["site_url"] = site_url
    base = urlparse(site_url).path.rstrip("/") if preview_url else ""

    def rebase(html):
        if not base:
            return html
        html = re.sub(r'((?:href|src|action)=")/(?!/)', rf"\g<1>{base}/", html)

        def fix_srcset(m):
            entries = [e.strip() for e in m.group(1).split(",")]
            return 'srcset="' + ", ".join(base + e if e.startswith("/") else e for e in entries) + '"'

        return re.sub(r'srcset="([^"]*)"', fix_srcset, html)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    # static files
    shutil.copytree(SRC / "assets", OUT / "assets")
    for f in SRC.iterdir():  # favicon.ico, _redirects, _headers, etc.
        if f.is_file() and f.name != "_layout.html":
            shutil.copy2(f, OUT / f.name)

    sitemap = []
    for page_file in sorted((SRC / "pages").rglob("*.html")):
        raw = page_file.read_text()
        m = META_RE.match(raw)
        if not m:
            sys.exit(f"{page_file}: missing <!--meta {{...}} --> header")
        meta = json.loads(m.group(1))
        body = raw[m.end():]
        path = meta["path"]

        ctx = dict(site)
        ctx.update(meta)
        ctx["arch_line"] = ARCH_LINE
        ctx["arch_mark"] = ARCH_MARK
        ctx["today"] = date.today().isoformat()
        ctx["year"] = date.today().year

        canonical = site_url + (path if path != "/404.html" else "/")
        ld = [org_ld(site)] if path == "/" else []
        if path == "/":
            ld.append({
                "@context": "https://schema.org", "@type": "WebSite",
                "name": site["site_name"], "url": site_url + "/",
                "publisher": {"@id": site_url + "/#organization"},
            })
        if meta.get("breadcrumbs"):
            ld.append(breadcrumb_ld(site, [["Home", "/"]] + meta["breadcrumbs"]))
        for extra in meta.get("schema", []):
            extra = json.loads(render(json.dumps(extra), ctx))
            extra.setdefault("@context", "https://schema.org")
            ld.append(extra)

        ctx["content"] = render(body, ctx)
        ctx["canonical"] = canonical
        ctx["page_title"] = escape(meta["title"])
        ctx["page_description"] = escape(meta["description"])
        ctx["og_image"] = site_url + meta.get("image", "/assets/img/og-image.jpg")
        ctx["robots"] = "noindex" if meta.get("noindex") or preview_url else "index, follow, max-image-preview:large"
        ctx["json_ld"] = "\n".join(
            '<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>" for x in ld
        )
        ctx["body_class"] = meta.get("body_class", "")

        ctx["css_v"] = asset_hash("assets/css/site.css")
        ctx["js_v"] = asset_hash("assets/js/site.js")
        html = NAV_RE.sub(lambda m2: 'aria-current="page"' if meta.get("nav") == m2.group(1) else "", layout)
        # render layout; content is already rendered, protect it from a second pass
        html = html.replace("{{content}}", "\x00CONTENT\x00")
        html = render(html, ctx).replace("\x00CONTENT\x00", ctx["content"])

        dest = OUT / (path.lstrip("/") + "index.html" if path.endswith("/") else path.lstrip("/"))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rebase(html))

        if not meta.get("noindex"):
            sitemap.append((canonical, meta.get("priority", "0.7")))

    today = date.today().isoformat()
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>\n"
                  for u, p in sitemap)
        + "</urlset>\n"
    )
    if preview_url:
        (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
        (OUT / ".nojekyll").write_text("")
    else:
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n")
    print(f"Built {len(sitemap)} pages into {OUT.relative_to(ROOT)}/")

    if "--serve" in sys.argv:
        import http.server
        import functools
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print("Serving on http://localhost:8000  (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()


if __name__ == "__main__":
    main()

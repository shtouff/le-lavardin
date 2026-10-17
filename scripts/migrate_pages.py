#!/usr/bin/env python3
"""Migrate WordPress pages to Hugo content files."""

import json
import os
import re
import shutil
from base64 import b64encode
from pathlib import Path
from urllib import request
from urllib.parse import urlparse
from bs4 import BeautifulSoup

WP_BASE = os.environ.get("WP_BASE", "https://www-le-lavardin.kappa.lvrdn.name")
WP_USER = os.environ.get("WP_USER", "")
WP_PASS = os.environ.get("WP_PASS", "")

AUTH = b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
UPLOADS_DIR = Path("/home/shtouff/github/shtouff/le-lavardin/uploads")
CONTENT_DIR = Path("/home/shtouff/github/shtouff/le-lavardin/content")


def wp_get(path):
    url = f"{WP_BASE}/wp-json/wp/v2/{path}"
    req = request.Request(url, headers={"Authorization": f"Basic {AUTH}"})
    with request.urlopen(req) as r:
        return json.loads(r.read())


def find_in_uploads(filename):
    for p in UPLOADS_DIR.rglob(filename):
        return p
    return None


def extract_image_names(html):
    soup = BeautifulSoup(html, "html.parser")
    images = []
    seen = set()
    for img in soup.find_all("img"):
        src = img.get("src", "")
        parsed = urlparse(src)
        if "/uploads/" not in parsed.path:
            continue
        fn = Path(parsed.path).name
        base = re.sub(r"-\d+x\d+(\.[a-zA-Z]+)$", r"\1", fn)
        if base not in seen:
            seen.add(base)
            images.append(base)
    return images


def html_to_markdown(html):
    soup = BeautifulSoup(html, "html.parser")

    # Strip Jimdo/CC legacy wrappers
    for el in soup.find_all(class_=re.compile(r"cc-m|j-module|jimdo")):
        el.unwrap()

    def node_to_md(node):
        if isinstance(node, str):
            return node
        tag = node.name
        if tag is None:
            return ""
        children = "".join(node_to_md(c) for c in node.children)

        if tag in ("p",):
            text = children.strip()
            return f"\n\n{text}\n\n" if text else ""
        elif tag == "h1":
            return f"\n\n# {children.strip()}\n\n"
        elif tag == "h2":
            return f"\n\n## {children.strip()}\n\n"
        elif tag == "h3":
            return f"\n\n### {children.strip()}\n\n"
        elif tag == "h4":
            return f"\n\n#### {children.strip()}\n\n"
        elif tag in ("strong", "b"):
            t = children.strip()
            return f"**{t}**" if t else ""
        elif tag in ("em", "i"):
            return f"*{children.strip()}*"
        elif tag == "a":
            href = node.get("href", "")
            text = children.strip()
            if href and text and not href.startswith("mailto"):
                return f"[{text}]({href})"
            return text
        elif tag == "br":
            return "\n"
        elif tag == "ul":
            return "\n\n" + children + "\n\n"
        elif tag == "ol":
            return "\n\n" + children + "\n\n"
        elif tag == "li":
            return f"- {children.strip()}\n"
        elif tag == "blockquote":
            lines = children.strip().splitlines()
            return "\n\n" + "\n".join(f"> {l}" for l in lines) + "\n\n"
        elif tag == "img":
            return ""
        elif tag == "iframe":
            src = node.get("src", "")
            yt = re.search(r"youtube\.com/embed/([A-Za-z0-9_-]+)", src)
            if yt:
                return f"\n\n{{{{< youtube {yt.group(1)} >}}}}\n\n"
            return ""
        elif tag in ("script", "style", "head", "form", "input", "textarea", "button", "select"):
            return ""
        else:
            return children

    md = node_to_md(soup)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def migrate_page(slug, html, title, dest_path, bundle=False):
    md = html_to_markdown(html)
    images = extract_image_names(html)

    if bundle:
        dest_path.mkdir(parents=True, exist_ok=True)
        for img_name in images:
            src = find_in_uploads(img_name)
            if src:
                dest = dest_path / img_name
                if not dest.exists():
                    shutil.copy2(src, dest)
            else:
                print(f"  WARN image not found: {img_name}")
        if images:
            md = md.rstrip() + "\n\n{{< gallery >}}\n"
        out = dest_path / "index.fr.md"
    else:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        out = dest_path

    toml = f'+++\ntitle = "{title}"\n+++\n\n'
    out.write_text(toml + md, encoding="utf-8")
    print(f"  OK  {slug} → {out.relative_to(CONTENT_DIR)} ({len(images)} images)")


def main():
    print("Fetching pages from WordPress...")
    pages = wp_get("pages?per_page=50&_fields=slug,title,content")
    by_slug = {p["slug"]: p for p in pages}

    # Page d'accueil
    p = by_slug["le-lavardin"]
    migrate_page("le-lavardin", p["content"]["rendered"],
                 "Bienvenue au Lavardin",
                 CONTENT_DIR / "_index.fr.md")

    # Tarifs
    p = by_slug["les-disponibilites"]
    migrate_page("les-disponibilites", p["content"]["rendered"],
                 "Tarifs",
                 CONTENT_DIR / "tarifs.fr.md")

    # Chambres — section index
    p = by_slug.get("le-lavardin")  # réutilise le texte accueil pour l'intro chambres si besoin
    migrate_page("chambres", by_slug.get("le-lavardin", {}).get("content", {}).get("rendered", ""),
                 "Nos Chambres",
                 CONTENT_DIR / "chambres" / "_index.fr.md")

    # Chambre La Touline (Page Bundle)
    p = by_slug["la-touline"]
    migrate_page("la-touline", p["content"]["rendered"],
                 "La Touline",
                 CONTENT_DIR / "chambres" / "la-touline",
                 bundle=True)

    # Gîte Le Cabestan (Page Bundle)
    p = by_slug["le-cabestan"]
    migrate_page("le-cabestan", p["content"]["rendered"],
                 "Le Cabestan",
                 CONTENT_DIR / "chambres" / "le-cabestan",
                 bundle=True)

    # Contact
    p = by_slug["contact"]
    migrate_page("contact", p["content"]["rendered"],
                 "Contact",
                 CONTENT_DIR / "contact.fr.md")

    # Liens
    p = by_slug["liens"]
    migrate_page("liens", p["content"]["rendered"],
                 "Liens utiles",
                 CONTENT_DIR / "liens.fr.md")

    # Nos engagements
    p = by_slug["nos-engagements"]
    migrate_page("nos-engagements", p["content"]["rendered"],
                 "Nos engagements",
                 CONTENT_DIR / "nos-engagements.fr.md")

    print("\nDone.")


if __name__ == "__main__":
    main()

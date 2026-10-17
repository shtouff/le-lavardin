#!/usr/bin/env python3
"""Migrate all WordPress posts to Hugo Page Bundles."""

import json
import os
import re
import shutil
import unicodedata
from pathlib import Path
from urllib import request
from urllib.parse import urlparse
from base64 import b64encode
from bs4 import BeautifulSoup

WP_BASE = os.environ.get("WP_BASE", "https://www-le-lavardin.kappa.lvrdn.name")
WP_USER = os.environ.get("WP_USER", "")
WP_PASS = os.environ.get("WP_PASS", "")
UPLOADS_DIR = Path("/home/shtouff/github/shtouff/le-lavardin/static/images/uploads")
CONTENT_DIR = Path("/home/shtouff/github/shtouff/le-lavardin/content/posts")

AUTH = b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()


def wp_get(path):
    url = f"{WP_BASE}/wp-json/wp/v2/{path}"
    req = request.Request(url, headers={"Authorization": f"Basic {AUTH}"})
    with request.urlopen(req) as r:
        return json.loads(r.read())


def fetch_all_posts():
    posts = []
    page = 1
    while True:
        batch = wp_get(f"posts?per_page=100&page={page}&_fields=id,slug,date,title,content")
        if not batch:
            break
        posts.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return posts


def slugify(text):
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove WordPress gallery containers (we'll use {{< gallery >}})
    for el in soup.find_all(class_=re.compile(r"rl-gallery")):
        el.decompose()

    # Remove empty divs/spans left behind
    for el in soup.find_all(["div", "span"]):
        if not el.get_text(strip=True) and not el.find("img"):
            el.decompose()

    def process_node(node):
        if isinstance(node, str):
            return node

        tag = node.name
        children = "".join(process_node(c) for c in node.children)

        if tag in ("p",):
            return f"\n\n{children.strip()}\n\n"
        elif tag in ("h1",):
            return f"\n\n# {children.strip()}\n\n"
        elif tag in ("h2",):
            return f"\n\n## {children.strip()}\n\n"
        elif tag in ("h3",):
            return f"\n\n### {children.strip()}\n\n"
        elif tag in ("h4",):
            return f"\n\n#### {children.strip()}\n\n"
        elif tag in ("strong", "b"):
            return f"**{children}**"
        elif tag in ("em", "i"):
            return f"*{children}*"
        elif tag == "a":
            href = node.get("href", "")
            text = children.strip()
            if href and text:
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
            return ""  # images handled separately
        elif tag == "iframe":
            src = node.get("src", "")
            yt = re.search(r"youtube\.com/embed/([A-Za-z0-9_-]+)", src)
            if yt:
                return f"\n\n{{{{< youtube {yt.group(1)} >}}}}\n\n"
            return ""
        elif tag in ("figure", "figcaption"):
            return children
        elif tag in ("div", "section", "article", "span"):
            return children
        elif tag in ("script", "style", "head"):
            return ""
        else:
            return children

    md = process_node(soup)

    # Normalize whitespace
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def extract_image_names(html_content):
    """Extract WP upload image basenames from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        parsed = urlparse(src)
        path = parsed.path  # e.g. /wp-content/uploads/2019/01/Hermione-1-150x150.jpg
        if "/uploads/" in path:
            filename = Path(path).name  # Hermione-1-150x150.jpg
            # Find the original (no size suffix)
            base = re.sub(r"-\d+x\d+(\.[a-z]+)$", r"\1", filename)
            images.append(base)
    # Also check gallery link hrefs
    for a in soup.find_all("a", class_="rl-gallery-link"):
        href = a.get("href", "")
        if "/uploads/" in href:
            images.append(Path(urlparse(href).path).name)
    # Deduplicate preserving order
    seen = set()
    result = []
    for img in images:
        if img not in seen:
            seen.add(img)
            result.append(img)
    return result


def find_in_uploads(filename):
    """Search recursively in uploads for a file by name."""
    for p in UPLOADS_DIR.rglob(filename):
        return p
    return None


def migrate_post(post):
    slug = post["slug"]
    date = post["date"][:10]  # YYYY-MM-DD
    title = BeautifulSoup(post["title"]["rendered"], "html.parser").get_text()
    html = post["content"]["rendered"]

    bundle_dir = CONTENT_DIR / slug
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # Find and copy images
    images = extract_image_names(html)
    has_gallery = bool(images)
    copied = []
    for img_name in images:
        src = find_in_uploads(img_name)
        if src:
            dest = bundle_dir / img_name
            if not dest.exists():
                shutil.copy2(src, dest)
            copied.append(img_name)
        else:
            print(f"  WARN image not found in uploads: {img_name}")

    # Convert content
    md_body = html_to_markdown(html)

    # Append gallery shortcode if images present
    if copied:
        md_body = md_body.rstrip() + "\n\n{{< gallery >}}\n"

    # Write index.fr.md
    index_path = bundle_dir / "index.fr.md"
    # Skip if already exists (e.g. logo-sur-le-portail, visite-hermione)
    if index_path.exists():
        print(f"  SKIP {slug} (already exists)")
        return

    toml = f'+++\ntitle = "{title}"\ndate = "{date}"\ndraft = false\n+++\n\n'
    index_path.write_text(toml + md_body, encoding="utf-8")
    print(f"  OK  {date} {slug} ({len(copied)} images)")


def main():
    print("Fetching posts from WordPress...")
    posts = fetch_all_posts()
    print(f"Found {len(posts)} posts\n")

    for post in sorted(posts, key=lambda p: p["date"]):
        migrate_post(post)

    print("\nDone.")


if __name__ == "__main__":
    main()

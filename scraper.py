import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
from nltk.tokenize import sent_tokenize
import json
import re
import os
import dotenv
dotenv.load_dotenv()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CleanScraper/1.0)"
}

MAX_DEPTH = 2
MAX_PAGES = 30

OUTPUT_DIR_CLEANED = Path("cleaned_data")
OUTPUT_DIR_CLEANED.mkdir(exist_ok=True)

OUTPUT_DIR_BLOCK = Path("block_data")
OUTPUT_DIR_BLOCK.mkdir(exist_ok=True)

START_URLS = [os.getenv("START_URLS")]

visited = set()

DOC_KEYWORDS = [
    "docs", "documentation", "api", "reference", "guide",
    "manual", "developer", "sdk",
    "pricing", "plans", "billing", "cost", "subscription"
]

# ----------------------------
# Fetch
# ----------------------------

def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            return r.text
    except requests.RequestException:
        pass
    return None


def is_binary_spec(url: str) -> bool:
    return url.lower().endswith((".yaml", ".yml", ".json", ".zip"))


def download_file(url: str):
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code == 200:
        fname = url.split("/")[-1]
        with open(OUTPUT_DIR_BLOCK / fname, "wb") as f:
            f.write(r.content)
        print("Downloaded spec:", fname)


# ----------------------------
# HTML cleaning helpers
# ----------------------------

NOISE_TAGS = [
    "script", "style", "nav", "footer",
    "header", "aside", "noscript"
]

CONTENT_TAGS = [
    "h1","h2","h3","h4","h5",
    "p","li","pre","code","table","blockquote"
]


def remove_noise(soup: BeautifulSoup):
    for tag in soup(NOISE_TAGS):
        tag.decompose()


# ----------------------------
# Block-based extraction
# ----------------------------

def extract_blocks(html: str):
    soup = BeautifulSoup(html, "lxml")
    remove_noise(soup)

    blocks = []
    order = 0
    current_section = None

    for tag in soup.find_all(CONTENT_TAGS):
        text = tag.get_text(separator=" ", strip=True)
        if not text:
            continue

        order += 1

        if tag.name.startswith("h"):
            current_section = text
            blocks.append({
                "block_id": f"b{order}",
                "order": order,
                "section": current_section,
                "block_type": "section_header",
                "tag_name": tag.name,
                "text": text
            })
            continue

        if tag.name in ["pre", "code"]:
            block_type = "code_example"
        elif tag.name == "li":
            block_type = "list_item"
        elif tag.name == "table":
            block_type = "table_block"
        elif tag.name == "blockquote":
            block_type = "inline_note"
        else:
            block_type = "paragraph"

        blocks.append({
            "block_id": f"b{order}",
            "order": order,
            "section": current_section,
            "block_type": block_type,
            "tag_name": tag.name,
            "text": text
        })

    return blocks


# ----------------------------
# Cleaned HTML extraction
# ----------------------------

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    remove_noise(soup)

    new_soup = BeautifulSoup("<html><body></body></html>", "lxml")
    body = new_soup.body

    for tag in soup.find_all(CONTENT_TAGS):
        text = tag.get_text(separator=" ", strip=True)
        if not text:
            continue

        new_tag = new_soup.new_tag(tag.name)
        new_tag.string = text
        body.append(new_tag)

    return str(new_soup)


# ----------------------------
# Link extraction
# ----------------------------

def looks_like_docs_url(url: str) -> bool:
    u = url.lower()
    return any(k in u for k in DOC_KEYWORDS)


def extract_internal_links(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, "lxml")
    links = set()
    base_domain = urlparse(base_url).netloc

    sidebar = soup.select(
        "aside a[href], nav[class*='sidebar'] a[href], "
        "div[class*='sidebar'] a[href], div[class*='toc'] a[href]"
    )

    for a in sidebar:
        href = a["href"].strip()
        full = urljoin(base_url, href)
        parsed = urlparse(full)
        if parsed.scheme in ("http", "https") and parsed.netloc == base_domain:
            links.add(full.split("#")[0])

    main = soup.find("main") or soup.find("article") or soup.body
    for a in main.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#"):
            continue
        full = urljoin(base_url, href)
        parsed = urlparse(full)
        if parsed.scheme in ("http", "https") and parsed.netloc == base_domain:
            links.add(full.split("#")[0])

    return links


def extract_topbar_links(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, "lxml")
    links = set()
    base_domain = urlparse(base_url).netloc

    for a in soup.select("header a[href], nav a[href]"):
        href = a["href"].strip()
        full = urljoin(base_url, href)
        parsed = urlparse(full)

        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc != base_domain:
            continue

        full = full.split("#")[0]

        if looks_like_docs_url(full):
            links.add(full)

    return links


# ----------------------------
# Page processing
# ----------------------------

def process_page(url: str, html: str):
    # block-based JSON
    blocks = extract_blocks(html)
    block_obj = {
        "url": url,
        "blocks": blocks
    }

    fname_base = re.sub(r"[^\w\-]", "_", url)[:80]

    with open(OUTPUT_DIR_BLOCK / f"{fname_base}.json", "w", encoding="utf-8") as f:
        json.dump(block_obj, f, ensure_ascii=False, indent=2)

    # cleaned HTML
    cleaned = clean_html(html)
    with open(OUTPUT_DIR_CLEANED / f"{fname_base}.html", "w", encoding="utf-8") as f:
        f.write(cleaned)


# ----------------------------
# Crawl
# ----------------------------

def crawl(url: str, depth: int):
    if depth > MAX_DEPTH:
        return
    if url in visited or len(visited) >= MAX_PAGES:
        return

    print(f"[{depth}] {url}")
    visited.add(url)

    html = fetch_html(url)
    if not html:
        if is_binary_spec(url):
            download_file(url)
        return

    process_page(url, html)

    for link in extract_internal_links(html, url):
        crawl(link, depth + 1)

    for link in extract_topbar_links(html, url):
        crawl(link, depth + 1)


# ----------------------------
# Main
# ----------------------------

def main():
    for url in START_URLS:
        crawl(url, 0)


if __name__ == "__main__":
    main()
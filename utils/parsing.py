import traceback
from dataclasses import dataclass
from urllib.parse import urlparse
import re
from lxml import html
import tldextract


@dataclass
class PageElements:
    title: []
    headings: []
    paragraphs: []
    description: []


def reformat_html_tags(html_content):
    tree = html.fromstring(html_content)

    for bad in tree.xpath("//script | //style | //noscript | //nav | //footer | //header"):
        bad.getparent().remove(bad)

    title = []

    # <title>
    t = tree.xpath("string(//title)")
    if t:
        title.append(t.strip())

    # og:title (case-insensitive)
    title += tree.xpath("//meta[translate(@property,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='og:title']/@content")

    # twitter:title
    title += tree.xpath("//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='twitter:title']/@content")

    headings = []
    for level in range(1, 7):
        tags = tree.xpath(f"//h{level} | //H{level}")
        headings.append([
            " ".join(el.text_content().split())
            for el in tags
            if el.text_content().strip()
        ])

    # --- DESCRIPTION ---
    desc_xpath = [
        "//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='description']/@content",
        "//meta[translate(@property,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='og:description']/@content",
        "//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='twitter:description']/@content",
    ]
    desc = []
    for xp in desc_xpath:
        result = tree.xpath(xp)
        if result:
            desc = [" ".join(result[0].split())]
            break

    # --- PARAGRAPHS: extract all visible text from body ---
    body = tree.xpath("//body")
    paragraphs = []
    seen = set()

    if body:
        for element in body[0].iter():
            # Skip non-content tags
            if element.tag in ('script', 'style', 'noscript', 'meta', 'link', 'br', 'hr', 'img'):
                continue

            # Get direct text of this element (not children's text)
            texts = []
            if element.text and element.text.strip():
                texts.append(element.text.strip())
            for child in element:
                if child.tail and child.tail.strip():
                    texts.append(child.tail.strip())

            if not texts:
                continue

            text = " ".join(" ".join(texts).split())
            if len(text) < 5:
                continue

            # Deduplicate
            if text not in seen:
                seen.add(text)
                paragraphs.append(text)

    # Clean title
    title = [" ".join(t.split()) for t in title if t and t.strip()]

    page_elements = PageElements(title=title, headings=headings, description=desc, paragraphs=paragraphs)

    return page_elements


def html_to_clean(html):
    # Remove comments first

    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

    # Remove script and style tags (these are most important)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove head entirely
    html = re.sub(r'<head[^>]*>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove header, nav, footer, aside (run multiple times for nested)
    for _ in range(5):
        html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<aside[^>]*>.*?</aside>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove other junk tags
    html = re.sub(r'<(iframe|noscript|form|button|svg|input|select|textarea)[^>]*>.*?</\1>', '', html,
                  flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<(iframe|noscript|form|button|svg|input|select|textarea)[^>]*/>', '', html, flags=re.IGNORECASE)

    # Remove all remaining tags
    html = re.sub(r'<[^>]+>', ' ', html)

    # Remove HTML entities
    html = re.sub(r'&[a-zA-Z0-9#]+;', ' ', html)

    # Clean whitespace
    html = re.sub(r'\s+', ' ', html).strip()

    return html


def extract_anchors(html_content):
    html_content = html_content.lower()
    tree = html.fromstring(html_content)

    anchors = tree.xpath("//a")

    links = []
    values = []
    for a in anchors:
        href = a.get("href")
        text = a.text_content().strip()
        if href and text:
            links.append(href)
            values.append(text)

    return links, values


def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain


def get_tld(domain):
    parts = domain.split('.')
    if len(parts) >= 2:
        return parts[-1]
    return ''


def sanitize_route(url):
    if url.endswith('/'):
        return url[:-1]
    return url


def get_url_root(url: str) -> str:
    ext = tldextract.extract(url)
    return f"https://{ext.domain}.{ext.suffix}"

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
    tree = html.fromstring(html_content.lower())

    for bad in tree.xpath("//script | //style"):
        bad.getparent().remove(bad)

    title = []

    # <title>
    t = tree.xpath("string(//title)")
    if t:
        title.append(t.strip())

    # og:title
    title += tree.xpath("//meta[@property='og:title']/@content")

    # twitter:title
    title += tree.xpath("//meta[@name='twitter:title']/@content")

    headings = []
    for level in range(1, 7):
        headings.append(
            tree.xpath("//h" + str(level))
        )

    # --- PARAGRAPHS ---
    p = tree.xpath(
        "//p | //span | //li | //td | //th | //dd | //dt | //blockquote | //figcaption | //label | //a | //pre | //code")

    # --- DESCRIPTION ---
    desc = (
            tree.xpath("//meta[@name='description']/@content") or
            tree.xpath("//meta[@property='og:description']/@content") or
            tree.xpath("//meta[@name='twitter:description']/@content")
    )

    def clean_list(lst):
        result = []
        for item in lst:
            if not item:
                continue
            t = item.text_content() if hasattr(item, 'text_content') else str(item)
            t = " ".join(t.split())
            if t:
                result.append(t)
        return result

    title = clean_list(title)
    headings = [clean_list(h) for h in headings]
    p = clean_list(p)
    desc = clean_list(desc[:1])

    page_elements = PageElements(title=title, headings=headings, description=desc, paragraphs=p)

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
    links = [a.get("href") for a in anchors if a.get("href")]
    values = [a.text for a in anchors if a.text]

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

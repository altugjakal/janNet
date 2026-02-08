from urllib.parse import urlparse
import re

import tldextract


def reformat_html_tags(html_content):
    html = html_content

    title = re.findall(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title += re.findall(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
    title += re.findall(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', html, re.IGNORECASE)
    title += re.findall(r'<meta[^>]*name=["\']twitter:title["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
    title += re.findall(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']twitter:title["\']', html, re.IGNORECASE)

    h1 = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    h2 = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.IGNORECASE | re.DOTALL)
    h3 = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.IGNORECASE | re.DOTALL)
    h4 = re.findall(r'<h4[^>]*>(.*?)</h4>', html, re.IGNORECASE | re.DOTALL)
    h5 = re.findall(r'<h5[^>]*>(.*?)</h5>', html, re.IGNORECASE | re.DOTALL)
    h6 = re.findall(r'<h6[^>]*>(.*?)</h6>', html, re.IGNORECASE | re.DOTALL)
    p = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)

    desc = re.findall(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
        html, re.IGNORECASE)

    if not desc:
        desc = re.findall(
            r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\']',
            html, re.IGNORECASE)

    if not desc:
        desc = re.findall(
            r'<meta[^>]*name=["\']twitter:description["\'][^>]*content=["\']([^"\']*)["\']',
            html, re.IGNORECASE)

    def looks_like_garbage(t):
        if len(t) > 350:
            return True
        if re.search(r"[{}();=<>]|function|var\s", t):
            return True
        return False

    if desc:
        desc = [d.strip() for d in desc if not looks_like_garbage(d)]
        desc = desc[:1]
    else:
        desc = [""]

    texts = [title, h1, h2, h3, h4, h5, h6, p, desc]
    texts = [[re.sub(r'<[^>]+>', '', item) for item in sublist] for sublist in texts]
    texts = [[re.sub(r'&[a-zA-Z0-9#]+;', ' ', item) for item in sublist] for sublist in texts]
    texts = [[re.sub(r'\s+', ' ', item).strip() for item in sublist] for sublist in texts]

    return texts


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
    anchors = re.findall(r'href=[\'"]?([^\'" >]+)', html_content)

    return anchors


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

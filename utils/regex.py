from urllib.parse import urlparse
import re
import requests



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
    p  = re.findall(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)

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

    clean_html = lambda html: re.sub(
        r'<(header|nav|footer|aside|script|style|iframe|noscript|form|button|svg)[^>]*>.*?</\1>|<!--.*?-->',
        '',
        html,
        flags=re.DOTALL | re.IGNORECASE
    )

    html_out = clean_html(html_content)
    html_out = re.sub(r'\s+', ' ', html_out).strip()
    html_out = re.sub(r'<(script|style).*?>.*?</\1>', '', html_out, flags=re.DOTALL | re.IGNORECASE)
    html_out = re.sub(r'<[^>]+>', ' ', html_out)
    html_out = re.sub(r'&[a-zA-Z0-9#]+;', ' ', html_out)
    html_out = re.sub(r'\s+', ' ', html_out).strip()

    return html_out, texts


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


    


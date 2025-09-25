from urllib.parse import urlparse
import re


def reformat_html_tags(html_content):
    
    str = html_content.lower()
    title = re.findall(r'<title>(.*?)</title>', str)
    h1 = re.findall(r'<h1>(.*?)</h1>', str)
    h2 = re.findall(r'<h2>(.*?)</h2>', str)
    h3 = re.findall(r'<h3>(.*?)</h3>', str)
    h4 = re.findall(r'<h4>(.*?)</h4>', str)
    h5 = re.findall(r'<h5>(.*?)</h5>', str)
    h6 = re.findall(r'<h6>(.*?)</h6>', str)
    p = re.findall(r'<p>(.*?)</p>', str)
    texts = [title, h1, h2, h3, h4, h5, h6, p]

    clear_closing_tags = re.sub(r'</[^>]*>', '', html_content)
    handle_opening_tags = re.sub(r'<([^>]*)>', r'(\1): ', clear_closing_tags)
    return handle_opening_tags, texts

def extract_anchors(html_content):
    html_content = html_content.lower()
    anchors = re.findall(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"', html_content) 

    return anchors

def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

def sanitize_route(url):
    if url.endswith('/'):
        return url[:-1]
    return url


    


from urllib.parse import urlparse
import re
import requests



def reformat_html_tags(html_content):
    
    str = html_content #dont lover, site details uses orig case
    title = re.findall(r'<title>(.*?)</title>', str)
    h1 = re.findall(r'<h1>(.*?)</h1>', str)
    h2 = re.findall(r'<h2>(.*?)</h2>', str)
    h3 = re.findall(r'<h3>(.*?)</h3>', str)
    h4 = re.findall(r'<h4>(.*?)</h4>', str)
    h5 = re.findall(r'<h5>(.*?)</h5>', str)
    h6 = re.findall(r'<h6>(.*?)</h6>', str)
    p = re.findall(r'<p>(.*?)</p>', str)
    desc = re.findall(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', str)


    texts = [title, h1, h2, h3, h4, h5, h6, p, desc]

    #clean html and unicode in all items

    texts = [[re.sub(r'<[^>]+>', '', item) for item in sublist] for sublist in texts]
    texts = [[re.sub(r'&[a-z]+;', ' ', item) for item in sublist] for sublist in texts]
    texts = [[re.sub(r'\s+', ' ', item).strip() for item in sublist] for sublist in texts]

    clean_html = lambda html: re.sub(r'<(header|nav|footer|aside|script|style|iframe|noscript|form|button|svg)[^>]*>.*?</\1>|<!--.*?-->', '', html, flags=re.DOTALL|re.IGNORECASE)
    html_content = clean_html(html_content)
    html_content = html_content = re.sub(r'\s+', ' ', html_content).strip()
    html_content = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<[^>]+>', ' ', html_content)
    html_content = re.sub(r'&[a-z]+;', ' ', html_content)
    html_content = re.sub(r'\s+', ' ', html_content).strip()
    


    return html_content, texts

def extract_anchors(html_content):
    html_content = html_content.lower()
    anchors = re.findall(r'href=[\'"]?([^\'" >]+)', html_content) 

    return anchors

def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

def sanitize_route(url):
    if url.endswith('/'):
        return url[:-1]
    return url


    


import random
from math import log1p
import time

from constants import html_importance_map
import requests

from core.vectordb.vectordb import VectorDB
from utils.regex import extract_anchors, get_domain, reformat_html_tags
from utils.misc import extract_keywords
import tldextract
from utils.data_handling import *
from urllib.parse import urljoin, urlparse




def assign_importance(content, keyword, element_type):
    tf = content.lower().count(keyword.lower())

    tf = 1 + log1p(tf)

    tf_capped = min(tf, 3)


    phrase_bonus = len(keyword.split()) * 0.5




    
    base_importance = html_importance_map.get(element_type, 1) * tf_capped * (1 + phrase_bonus)
    
    return base_importance


def crawl(url, sleep_median, sleep_padding, domain_list, url_queue_list, new_url_list, url_list, db=None):

    if db is None:
        db = VectorDB()

    if url not in url_list:
            url_list.append(url)
            add_url(url)
    else:
            print('Already in list')
            return url_queue_list, domain_list, new_url_list

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    if url.startswith("https"):
        url = url
    else:
        url = "https://" + url

    url = url.rstrip("/")

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    except requests.RequestException as e:
        print(f"Request failed for {url}")
        return url_queue_list, domain_list, new_url_list

    if response.status_code == 200:
        content = response.text


        anchors = extract_anchors(content)

        
        if url in url_queue_list:
            url_queue_list.remove(url)
            drop_from_queue(url)

        for anchor in anchors:
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(url, anchor)

            # Skip non-http protocols like mailto:, javascript:, etc.
            if not absolute_url.startswith(("http://", "https://")):
                continue


            absolute_url = absolute_url.rstrip("/")

            # Track domain
            domain = get_domain(absolute_url)
            if domain not in domain_list:
                domain_list.append(domain)

            # Add URL to queue (avoid duplicates)
            if absolute_url not in url_queue_list and absolute_url not in url_list:
                new_url_list.append(absolute_url)
                url_queue_list.append(absolute_url)



        
        
        
            
        

        print(f"Found {len(anchors)} anchors ({len(url_queue_list)} urls in store, {len(domain_list)} domains in store)")
        content, texts = reformat_html_tags(content)


        vector = db.text_vectoriser(content)
        id = np.random.randint(9999)
        db.insert(vector=vector, id=id)
        manage_vector_for_index(url= url, emb_id=id)


# Extract keywords from different HTML tags, get a proper extractor ERROR ABOUT INDEX IS HERE -fixed
        url_obj = urlparse(url)

        domain = tldextract.extract(url).domain
        paths = [p for p in url_obj.path.split('/') if p]
        subdomains = url_obj.netloc.split('.')[:-2]
        params = [p for p in url_obj.query.split('&') if p] if url_obj.query else []

#idiot you skipped anchor titles -thats not necesarry rn
        text_list = [
            (texts[0] if len(texts) > 0 else [], "title"),
            (texts[1] if len(texts) > 1 else [], "h1"),
            (texts[2] if len(texts) > 2 else [], "h2"),
            (texts[3] if len(texts) > 3 else [], "h3"),
            (texts[4] if len(texts) > 4 else [], "h4"),
            (texts[5] if len(texts) > 5 else [], "h5"),
            (texts[6] if len(texts) > 6 else [], "h6"),
            (texts[7] if len(texts) > 7 else [], "p"),
            (texts[8] if len(texts) > 8 else [], "description"),
            ([domain] if domain else [], "domain"),
            (subdomains if len(subdomains) > 0 else [], "subdomain"),
            (paths if len(paths) > 0 else [], "path"),
            (params if len(params) > 0 else [], "param")
        ]

        for text_items, element_type in text_list:
            keyword_scores = {}

            for text in text_items:
                for word in extract_keywords(text):


                    importance = assign_importance(text, word, element_type)
                    keyword_scores[word] = keyword_scores.get(word, 0) + importance



            if keyword_scores:
                manage_for_index(url=url, pairs=keyword_scores)

             

        print(f"200: {url}")
    else:
        print(f"Could not find url: {url}")

    time.sleep(sleep_median + random.uniform(-sleep_padding, sleep_padding))

    return url_queue_list, domain_list, new_url_list



    


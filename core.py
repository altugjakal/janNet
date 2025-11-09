import random
from math import log1p
import time
import traceback
from constants import html_importance_map
import requests

from utils.regex import extract_anchors, get_domain, reformat_html_tags, get_tld
from utils.misc import extract_keywords, clamp_search_term
import tldextract
from utils.data_handling import *
import json
import urllib.parse




def assign_importance(content, keyword, element_type):
    tf = content.lower().count(keyword.lower())

    tf = 1 + log1p(tf)

    tf_capped = min(tf, 3)


    phrase_bonus = len(keyword.split()) * 0.5




    
    base_importance = html_importance_map.get(element_type, 1) * tf_capped * (1 + phrase_bonus)
    
    return base_importance


def crawl(url, sleep_median, sleep_padding, domain_list, url_queue_list, new_url_list, url_list):



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
            if not anchor.startswith("https"):
                continue


            # Track domain
            domain = get_domain(anchor)
            if domain not in domain_list:
                domain_list.append(domain)


            # Add URL to queue (avoid duplicates)
            if anchor not in url_queue_list and anchor not in url_list:
                new_url_list.append(anchor)
                url_queue_list.append(anchor)

        
        
        
            
        

        print(f"Found {len(anchors)} anchors ({len(url_queue_list)} urls in store, {len(domain_list)} domains in store)")
        content, texts = reformat_html_tags(content)


# Extract keywords from different HTML tags, get a proper extractor ERROR ABOUT INDEX IS HERE -fixed
        url_obj = urllib.parse.urlparse(url)

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


def search(term):

    terms = extract_keywords(term)
    terms += clamp_search_term(term)
    terms = list(set(terms))
    

    results = []

    url_scores = {}


    initials = search_index(terms)


    for url, importance in initials.items():

        url_obj = urllib.parse.urlparse(url)

        paths = [p for p in url_obj.path.split('/') if p]
        subdomains = url_obj.netloc.split('.')[:-2]
        params = url_obj.query.split('&') if url_obj.query else []


        path_depth = len(paths)
        param_count = len(params)
        subdomain_count = len(subdomains)

        total_depth = path_depth + param_count + subdomain_count

        path_length_penalty = 1 / (1 + total_depth)

        print('path_depth for url' + url + str(path_length_penalty))


        tld = get_tld(get_domain(url))
        tld_popularity_penalty = 1.0 if tld in ['com', 'org', 'net'] else 0.7

        #we pay our respects to web 1
        tld_multiplier = 1.2 if tld == 'edu' else 1.0

        base_score = log1p(importance) * tld_popularity_penalty * path_length_penalty * tld_multiplier


        if url in url_scores:

            url_scores[url] += base_score
        else:
            url_scores[url] = base_score


    sorted_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)

    #test

    


    for url, score in sorted_urls:


        if len(results) >= 20:
            break
        results.append(url)


     
    print(f"Search for '{term}' yielded {len(results)} results.")
    print("\nDebug - Sorted URLs and Scores:")
    for url, score in sorted_urls:
        print(f"{url}: {score:.2f}")
    return results
    


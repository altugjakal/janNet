import urllib.parse
from utils.regex import get_domain, get_tld
from utils.misc import extract_keywords, clamp_search_term
from utils.data_handling import *
from math import log1p



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

        # we pay our respects to web 1
        tld_multiplier = 1.2 if tld == 'edu' else 1.0

        base_score = log1p(importance) * tld_popularity_penalty * path_length_penalty * tld_multiplier

        if url in url_scores:

            url_scores[url] += base_score
        else:
            url_scores[url] = base_score

    sorted_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)

    # test

    for url, score in sorted_urls:

        if len(results) >= 20:
            break
        results.append(url)

    print(f"Search for '{term}' yielded {len(results)} results.")
    print("\nDebug - Sorted URLs and Scores:")
    for url, score in sorted_urls:
        print(f"{url}: {score:.2f}")
    return results
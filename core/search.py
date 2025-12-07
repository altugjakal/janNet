import urllib.parse
from utils.regex import get_domain, get_tld
from utils.misc import extract_keywords, clamp_search_term
from utils.data_handling import *
from utils.misc import rank



def search(term):
    terms = extract_keywords(term)
    terms += clamp_search_term(term)
    terms = list(set(terms))

    results = []

    url_scores = {}

    initials = search_index(terms)

    for url, importance in initials.items():

        base_score = rank(url, importance)

        if url in url_scores:

            url_scores[url] += base_score
        else:
            url_scores[url] = base_score

    sorted_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)

    # test

    for url, score in sorted_urls:

        if len(results) >= 5:
            break
        results.append(url)

    print(f"Search for '{term}' yielded {len(results)} results.")
    print("\nDebug - Sorted URLs and Scores:")
    for url, score in sorted_urls:
        print(f"{url}: {score:.2f}")
    return results
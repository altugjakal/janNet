import requests
from utils.regex import reformat_html_tags, extract_anchors, get_domain
from utils.data_handling import write_to_csv, read_from_csv
import time 
from utils.data_handling import manage_for_index
import re
import json
from utils.misc import extract_keywords

visited_urls = read_from_csv("./csv/urls.csv")
stored_domains = read_from_csv("./csv/domains.csv")
indexes = read_from_csv("./csv/indexes.csv")
first_item = visited_urls[-1] if visited_urls else "https://alltop.com/"
url_list = [first_item]
domain_list = []


def search(term):
    terms = extract_keywords(term)
    results = []


    data = read_from_csv("./csv/indexes.csv")

    for keyword, url in data:
        if keyword in terms:
            result_url = json.loads(url)
            result_url = next(iter(result_url.keys()))
            results.append(result_url)
    
    return results
        

    

def crawl(url, sleep_median=3, sleep_padding=1):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    if url.startswith("http"):
        url = url
    else:

        url = "http://" + url

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    except requests.RequestException as e:
        print(f"Request failed for {url}")
        return

    if response.status_code == 200:
        content = response.text
        
        anchors = extract_anchors(content)

        for anchor in anchors:
            if anchor.startswith("http"):

                
                if get_domain(anchor) not in domain_list and [get_domain(anchor)] not in stored_domains:
                    domain_list.append(get_domain(anchor))
                    write_to_csv("./csv/domains.csv", [get_domain(anchor)])
                if anchor not in url_list and [get_domain(anchor), anchor] not in visited_urls:
                    url_list.append(anchor)
                    write_to_csv("./csv/urls.csv", [get_domain(anchor), anchor])


        print(f"Found {len(anchors)} anchors ({len(url_list)} urls in store, {len(domain_list)} domains in store)")
        content, texts = reformat_html_tags(content)
        
# Extract keywords from different HTML tags

        element_types = [
            (texts[0], 8, "title"),    # title
            (texts[1], 2, "h1"),       # h1
            (texts[2], 3, "h2"),       # h2
            (texts[3], 4, "h3"),       # h3
            (texts[4], 5, "h4"),       # h4
            (texts[5], 6, "h5"),       # h5
            (texts[6], 7, "h6"),       # h6
            (texts[7], 1, "p")         # paragraphs
        ]

        for text_list, importance, element_type in element_types:
            keywords = []
            for text in text_list:
                keywords += extract_keywords(text)
            manage_for_index(url=url, keywords=keywords, importance=importance)

        

#-----------------------        

        print(f"200: {url}")
    else:
        print(f"Could not find url: {url}")

    time.sleep(sleep_median + (sleep_padding * (2 * (0.5 - time.time() % 1))))

def main():
    

    
    for url in url_list:
        if url in visited_urls:
            continue
        try:
            crawl(url, sleep_median=3, sleep_padding=1)
        except Exception as e:
            print(f"Error occurred while crawling {url}: {e}")
            continue


    print(f"Total unique URLs found: {len(url_list)}")
    print(f"Total unique domains found: {len(domain_list)}")


if __name__ == "__main__":
    main()

import time
import traceback
import requests
from utils.regex import extract_anchors, get_domain, reformat_html_tags
from utils.misc import extract_keywords

from utils.data_handling import write_to_csv, manage_for_index, remove_from_csv, read_from_csv
import json


def summarize_content(content):
    print("Summarizing content...")

def assign_importance(content, keyword, element_type):

    html_importance_map = {
        "title": 8,
        "h1": 7,
        "h2": 6,
        "h3": 5,
        "h4": 4,
        "h5": 3,
        "h6": 2,
        "p": 1,
        "description": 7
        
    }


    return html_importance_map.get(element_type, 1)



def crawl(url, sleep_median, sleep_padding, domain_list, url_queue_list, new_url_list, url_list):



    if url not in url_list:
            url_list.append(url)
            write_to_csv("./csv/urls.csv", [url])
    else:
            print('Already in list')
            return url_queue_list, domain_list, new_url_list

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    if url.startswith("http"):
        url = url
    else:
        url = "http://" + url

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
            remove_from_csv("./csv/queue.csv", [url])

        for anchor in anchors:
            if anchor.startswith("http"):

                
                if get_domain(anchor) not in domain_list:
                    domain_list.append(get_domain(anchor))
                    write_to_csv("./csv/domains.csv", [get_domain(anchor)])
                if anchor not in url_queue_list:
                    url_queue_list.append(anchor)
                    new_url_list.append(anchor)
                    write_to_csv("./csv/queue.csv", [anchor])

        
        
        
            
        

        print(f"Found {len(anchors)} anchors ({len(url_queue_list)} urls in store, {len(domain_list)} domains in store)")
        content, texts = reformat_html_tags(content)


# Extract keywords from different HTML tags, get a proper extractor ERROR ABOUT INDEX IS HERE


#idiot you skipped anchor titles
        text_list = [
            (texts[0] if len(texts) > 0 else [], "title"),
            (texts[1] if len(texts) > 0 else [], "h1"),       
            (texts[2] if len(texts) > 0 else [], "h2"),       
            (texts[3] if len(texts) > 0 else [], "h3"),      
            (texts[4] if len(texts) > 0 else [], "h4"),       
            (texts[5] if len(texts) > 0 else [], "h5"),      
            (texts[6] if len(texts) > 0 else [], "h6"),     
            (texts[7] if len(texts) > 0 else [], "p"),
            (texts[8] if len(texts) > 0 else [], "description")
            ]

        for text_items, element_type in text_list:
            keywords = []

            for text in text_items:
                importance = assign_importance(content, text, element_type)
                if text:    
                    keywords += extract_keywords(text) #there is the issue

            if keywords:
                manage_for_index(url=url, keywords=keywords, importance=importance)

             

        print(f"200: {url}")
    else:
        print(f"Could not find url: {url}")

    time.sleep(sleep_median + (sleep_padding * (2 * (0.5 - time.time() % 1))))

    return url_queue_list, domain_list, new_url_list


def search(term):
    
    terms = extract_keywords(term)

    results = []

    url_scores = {}

    indexes = read_from_csv("./csv/indexes.csv")

    for keyword, url in indexes:


        if keyword in terms:
            result_url = json.loads(url)
            
            for single_url, value in result_url.items():
                if single_url in url_scores:
                    url_scores[single_url] = 2**value
                else:
                    url_scores[single_url] = value

                

    sorted_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)
    


    for url, score in sorted_urls:
        if len(results) >= 5:
            break
        results.append(url)
     
    print(f"Search for '{term}' yielded {len(results)} results.")
    return results
    

def reasoner(query, contents, urls=None, client=None):
    if not contents:
        return "No content to analyze"
    
    cleaned_contents = []
    for content in contents[:5]:
        words = content.split()
        if len(words) > 200:
            content = ' '.join(words[:200])
        cleaned_contents.append(content)
    
    combined = " ".join(cleaned_contents)
    
    if len(combined.split()) < 30:
        return combined  # Too short to summarize
    
    try:
        result = client.summarization(
            combined[:800],  # Shorter to avoid timeout
            model="google/pegasus-cnn_dailymail"  # Smaller, faster model
        )
        return result["summary_text"]
    except Exception as e:
        import traceback
        print(f"Summarization failed:")
        traceback.print_exc()

        return f"Summarization failed: {e}"
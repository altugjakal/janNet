from math import log1p
import time
import traceback
import requests
from utils.regex import extract_anchors, get_domain, reformat_html_tags, get_tld
from utils.misc import extract_keywords, clamp_search_term
import tldextract
from utils.data_handling import write_to_csv, manage_for_index, remove_from_csv, read_from_csv
import json
import urllib.parse




def assign_importance(content, keyword, element_type):
    tf = content.lower().count(keyword.lower())
    
    keyword_specificity = len(keyword.split())
    
    tf_idf = (1 + tf) * keyword_specificity
    
    html_importance_map = {
        "title": 10, 
        "h1": 9,
        "h2": 8,
        "h3": 7,
        "h4": 6,
        "h5": 5,
        "h6": 4,
        "p": 2,
        "description": 9,
        "domain": 3,
        "subdomain": 2,
        "path": 2,
        "param": 3

    }
    
    base_importance = html_importance_map.get(element_type, 1) * tf_idf
    
    return base_importance


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
                    root_site_url = 'https://' + get_domain(anchor) 

                    if root_site_url not in url_queue_list:
                        url_queue_list.append(root_site_url)
                        new_url_list.append(root_site_url)
                        write_to_csv("./csv/queue.csv", [root_site_url])
                    
                    else:
                        url_queue_list.append(anchor)
                        new_url_list.append(anchor)
                        write_to_csv("./csv/queue.csv", [anchor])

        
        
        
            
        

        print(f"Found {len(anchors)} anchors ({len(url_queue_list)} urls in store, {len(domain_list)} domains in store)")
        content, texts = reformat_html_tags(content)


# Extract keywords from different HTML tags, get a proper extractor ERROR ABOUT INDEX IS HERE -fixed
        url_obj = urllib.parse.urlparse(url)

        domain = tldextract.extract(url).domain
        paths = url_obj.path.split('/')
        subdomains = url_obj.netloc.split('.')[:-2]
        params = url_obj.params.split('&')

#idiot you skipped anchor titles -thats not necesarry rn
        text_list = [
            (texts[0] if len(texts) > 0 else [], "title"),
            (texts[1] if len(texts) > 0 else [], "h1"),       
            (texts[2] if len(texts) > 0 else [], "h2"),       
            (texts[3] if len(texts) > 0 else [], "h3"),      
            (texts[4] if len(texts) > 0 else [], "h4"),       
            (texts[5] if len(texts) > 0 else [], "h5"),      
            (texts[6] if len(texts) > 0 else [], "h6"),     
            (texts[7] if len(texts) > 0 else [], "p"),
            (texts[8] if len(texts) > 0 else [], "description"),
            ([domain] if domain else [], "domain"),
            (subdomains if len(subdomains) > 0 else [], "subdomain"),
            (paths if len(paths) > 0 else [], "path"),
            (params if len(params) > 0 else [], "param")
        ]

        for text_items, element_type in text_list:
            keywords = []
            importances = []

            for text in text_items:
                for word in extract_keywords(text):

                    if word not in keywords:
                        keywords.append(word)
                        importance = assign_importance(text, word, element_type)
                        importances.append(importance)
                    else:
                        old_word_index = keywords.index(word)
                        old_importance = importances[old_word_index]
                        new_importance = assign_importance(content, word, element_type)
                        even_newer_importance = old_importance + new_importance
                        importances[old_word_index] = even_newer_importance
                        print(f"Updated importance for '{word}' in {element_type}")


            if keywords:
                manage_for_index(url=url, keywords=keywords, importances=importances)

             

        print(f"200: {url}")
    else:
        print(f"Could not find url: {url}")

    time.sleep(sleep_median + (sleep_padding * ((0.5 - time.time() % 1))))

    return url_queue_list, domain_list, new_url_list


def search(term):

    terms = extract_keywords(term)
    terms += clamp_search_term(term)
    

    results = []

    url_scores = {}

    indexes = read_from_csv("./csv/indexes.csv")

    for keyword, url in indexes:


        if keyword in terms:
            result_url = json.loads(url)
            
            for single_url, value in result_url.items():

                url_obj = urllib.parse.urlparse(single_url)

                paths = url_obj.path.split('/')
                subdomains = url_obj.netloc.split('.')[:-2]
                params = url_obj.params

                path_depth = len(paths)
                subdomain_depth = len(subdomains)
                param_count = len(params.split('&'))

                total_depth = path_depth + subdomain_depth + param_count

                path_length_penalty = 1 / (1 + total_depth)  
            

                tld = get_tld(get_domain(single_url))
                tld_popularity_penalty = 1.0 if tld in ['com', 'org', 'net'] else 0.7

                #we pay our respects to web 1
                tld_multiplier = 1.2 if tld == 'edu' else 1.0

                base_score = log1p(value) * tld_popularity_penalty * path_length_penalty * tld_multiplier


                if single_url in url_scores:

                    url_scores[single_url] += base_score
                else:
                    url_scores[single_url] = base_score


    sorted_urls = sorted(url_scores.items(), key=lambda x: x[1], reverse=True)
    


    for url, score in sorted_urls:
        if len(results) >= 20:
            break
        results.append(url)

     
    print(f"Search for '{term}' yielded {len(results)} results.")
    print("\nDebug - Sorted URLs and Scores:")
    for url, score in sorted_urls:
        print(f"{url}: {score:.2f}")
    return results
    

def reasoner(query, contents, urls=None, client=None):
    if not contents:
        return "No content to analyze"

    query = 'revise the contents of the webpages, and form a concise summary answering the question from the perspective of a friendly assistant: ' + query

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
            model="facebook/bart-large-cnn"
        )
        return result["summary_text"]
    except Exception as e:
        import traceback
        print(f"Summarization failed:")
        traceback.print_exc()

        return f"Summarization failed: {e}"
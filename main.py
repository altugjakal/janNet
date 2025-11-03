import requests
from utils.regex import reformat_html_tags, extract_anchors, get_domain
from utils.data_handling import remove_from_csv, write_to_csv, read_from_csv
import time 
from utils.data_handling import manage_for_index
import re
import json
from utils.misc import extract_keywords, site_details
from flask import Flask
from flask import render_template, jsonify
from core import crawl, search, reasoner
from huggingface_hub import InferenceClient
import threading
import traceback
from constants import first_urls

app = Flask(__name__)

host = 'localhost'
port = 8080

client = InferenceClient(
provider="hf-inference",
api_key="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"
)

urls_to_visit = read_from_csv("./csv/queue.csv")
visited_urls = read_from_csv("./csv/urls.csv")
stored_domains = read_from_csv("./csv/domains.csv")



first_items = first_urls.copy()
visited_urls = [row[0] for row in visited_urls] if visited_urls else []
url_list = visited_urls
url_queue_list = [row[0] for row in urls_to_visit] if urls_to_visit else first_items
new_url_list = []
domain_list = [row[0] for row in stored_domains] if stored_domains else [get_domain(url) for url in first_items]







    



def main():
    
    global url_queue_list, domain_list, new_url_list, url_list, visited_urls

    print("Starting crawler...")
    print('Want to add new url to starting batch? (y/n): ')
    add_url = input()
    if add_url.lower() == 'y':
        new_url = input('Enter the new URL: ')
        url_queue_list.append(new_url)
        write_to_csv("./csv/queue.csv", new_url)
        print(f"Added {new_url} to the queue.")

    for url in url_queue_list:
        if url in url_list:
            continue
        try:
            url_queue_list, domain_list, new_url_list = crawl(url, sleep_median=3, sleep_padding=1, domain_list=domain_list, url_queue_list=url_queue_list, new_url_list=new_url_list, url_list=url_list)
        except Exception as e:
            traceback.print_exc()
            continue



    print(f"Total unique URLs found: {len(url_list)}")
    print(f"Total unique domains found: {len(domain_list)}")




@app.route("/search/<term>")
def searchRoute(term):
    
     #keep here indexes are always updated
    results = search(term)
    site_data  = []
    contents = []

    
    

    for result in results:
        title, description, content = site_details(result)
        contents.append(content)


        site_data.append({
            'url': result,
            'title': title,
            'description': description,
            'domain': get_domain(result),
            'favicon': f"https://www.google.com/s2/favicons?domain={get_domain(result)}"

        })

    if contents:
        summary = reasoner(term, contents, urls=results, client=client)
        return jsonify({
            'results': site_data,
            'summary': summary
        })

    else: 
        return jsonify({
            'results': site_data
        })


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    crawler_thread = threading.Thread(target=main)
    crawler_thread.start()
    time.sleep(5)
    app.run(host=host, port=port, debug=False)

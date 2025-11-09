from utils.regex import get_domain
from utils.data_handling import *
import time
from utils.misc import site_details
from flask import Flask
from flask import render_template, jsonify
from core.crawl import crawl
from core.search import search
import threading
import traceback
from constants import first_urls

app = Flask(__name__)

host = 'localhost'
port = 8080

initialize_database()


urls_to_visit = get_queue()
visited_urls = get_all_urls()
stored_domains = get_domains()




first_items = first_urls.copy()
visited_urls = [row[0] for row in visited_urls] if visited_urls else []
url_list = visited_urls
url_queue_list = [row[0] for row in urls_to_visit] if urls_to_visit else first_items
new_url_list = []
domain_list = [row[0] for row in stored_domains] if stored_domains else [get_domain(url) for url in first_items]








def main():
    
    global url_queue_list, domain_list, new_url_list, url_list, visited_urls


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

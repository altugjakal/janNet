from core.vectordb.vectordb import VectorDB
from utils.regex import get_domain

from utils.data_handling import *
import time
from flask import Flask
from core.crawl import crawl
import threading
import traceback
from constants import first_urls
from api.routes.search import search_bp
from api.routes.markup import markup_bp

app = Flask(__name__)
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(markup_bp, url_prefix='/')

host = 'localhost'
port = 5004

initialize_vector_database()
initialize_database()

crawler_running = True
MAX_CRAWLS = 1000
db = VectorDB()




def main():
    global crawler_running, MAX_CRAWLS, db

    if get_queue_size() == 0:
        add_to_queue_batch(first_urls)

    crawl_count = 0



    while crawler_running and crawl_count < MAX_CRAWLS:
        queue = get_queue()

        if not queue:
            print("Queue empty!")
            break

        url = queue[0][0]

        if is_url_visited(url):
            drop_from_queue(url)
            continue

        if url in get_all_urls():
            continue
        try:
            crawl(url, sleep_median=3, sleep_padding=1, db=db)

        except Exception as e:
            traceback.print_exc()
            continue

        crawl_count += 1

    



if __name__ == "__main__":
    crawler_thread = threading.Thread(target=main)
    crawler_thread.start()
    time.sleep(5)
    app.run(host=host, port=port, debug=False)

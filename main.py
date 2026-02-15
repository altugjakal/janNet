import time
from concurrent.futures import ThreadPoolExecutor

from managers.db_manager import get_db, get_vdb
from utils.config import Config
from flask import Flask
from core.crawl import Crawl
from api.routes.search import search_bp
from api.routes.markup import markup_bp

app = Flask(__name__)
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(markup_bp, url_prefix='/')

host = '0.0.0.0'
port = 5004
_vdb = get_vdb()


def main(thread_id):
    global _vdb
    db = get_db()

    crawler = Crawl(sleep_median=0.400, sleep_padding=0.200, db=db, vdb=_vdb, thread_id=thread_id)

    #problem here

    if db.get_queue_size(thread_id=thread_id) == 0:
        db.add_to_queue_batch(Config.SEED_URLS[thread_id], thread_id)

    crawl_count = 0

    while crawl_count < Config.MAX_CRAWLS:

        queue = db.get_queue_batch(thread_id=thread_id)

        if not queue:
            print("Queue empty!")
            break

        url = queue[0][0]

        crawler.crawl(url)

        crawl_count += 1

    _vdb.save_to_disk()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nogui', action='store_true', help='Disable Web UI')

    args = parser.parse_args()

    with ThreadPoolExecutor(max_workers=Config.THREAD_COUNT) as exe:
        for t_id in range(Config.THREAD_COUNT):
            exe.submit(main, t_id)

        if not args.nogui:

            try:
                app.run(host=host, port=port, debug=False)
            finally:
                print("Shutting down crawlers...")
                exe.shutdown(wait=True)

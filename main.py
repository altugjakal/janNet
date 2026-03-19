from concurrent.futures import ThreadPoolExecutor
from time import sleep

from flask_cors import CORS

from api.routes.similar import similar_bp
from src.jannet.core.process.index import Index
from src.jannet.managers.db_manager import get_db, get_vdb
from src.jannet.utils.config import Config
from flask import Flask
from src.jannet.core.crawl import Crawl
from api.routes.search import search_bp
from api.routes.markup import markup_bp

from huggingface_hub import login

login(token=Config.HF_TOKEN)
app = Flask(__name__)
CORS(app)
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(similar_bp, url_prefix='/requery')
app.register_blueprint(markup_bp, url_prefix='/')

host = '0.0.0.0'
port = 5004
_vdb = get_vdb()


def crawl(thread_id):
    global _vdb
    db = get_db()

    crawler = Crawl(sleep_median=Config.SLEEP_M, sleep_padding=Config.SLEEP_P, db=db, vdb=_vdb, thread_id=thread_id)

    if db.get_queue_size(thread_id=thread_id) == 0:

        db.add_to_queue_batch([(hash(url) % (10 ** 9), url) for url in Config.SEED_URLS[thread_id]], thread_id)

    crawl_count = 0

    while crawl_count < Config.MAX_CRAWLS:

        queue = db.get_queue_next(thread_id=thread_id)


        if len(queue) == 0:
            print("Crawled all, sleeping...")
            sleep(10)
            continue

        url = queue[0]
        id = queue[1]

        crawler.crawl(url, id)
        crawl_count += 1

def process():
    global _vdb
    db = get_db()

    indexer = Index(db=db, vdb=_vdb)


    while True:

        queue = db.get_process_queue_next()
        print("Next: ", queue[0])



        if len(queue) == 0:
            print("Processed all, sleeping...")
            sleep(10)
            continue

        url = queue[0]
        content = queue[1]
        id = queue[2]

        indexer.process(url, content, id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nogui', action='store_true', help='Disable Web UI')

    args = parser.parse_args()

    with ThreadPoolExecutor() as exe:
        for t_id in range(Config.CRAWL_THREAD_COUNT):
            exe.submit(crawl, t_id)
        for _ in range(Config.PROCESS_THREAD_COUNT):
            exe.submit(process)

        if not args.nogui:

            try:
                app.run(host=host, port=port, debug=False, use_reloader=False)
            finally:
                _vdb.save_to_disk()
                print("Shutting down crawlers...")
                exe.shutdown(wait=True)

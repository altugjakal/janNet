from managers.db_manager import get_db, get_vdb
from utils.config import Config
from flask import Flask
from core.crawl import Crawl
import threading
from api.routes.search import search_bp
from api.routes.markup import markup_bp




app = Flask(__name__)
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(markup_bp, url_prefix='/')

host = 'localhost'
port = 5004


crawler_running = True

db = get_db()
vdb = get_vdb()
crawler = Crawl(sleep_median=3, sleep_padding=1, db=db, vdb=vdb)




def main():
    global crawler_running, db, vdb

    if db.get_queue_size() == 0:
        db.add_to_queue_batch(Config.SEED_URLS)

    crawl_count = 0



    while crawler_running and crawl_count < Config.MAX_CRAWLS:
        queue = db.get_queue_batch()

        if not queue:
            print("Queue empty!")
            break

        url = queue[0][0]

        if db.is_url_visited(url):
            db.drop_from_queue(url)
            continue



        crawler.crawl(url)



        crawl_count += 1




if __name__ == "__main__":
    crawler_thread = threading.Thread(target=main)
    crawler_thread.start()
    app.run(host=host, port=port, debug=False)



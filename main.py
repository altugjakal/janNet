import concurrent

from concurrent.futures import ThreadPoolExecutor


from flask_cors import CORS

from src.jannet.core.process.reverse_index import ReverseIndexCommunicator
from src.jannet.core.process.robots_cache import RobotsCache
from src.jannet.core.workers.crawl import crawl
from src.jannet.core.workers.process import process
from src.jannet.managers.db_manager import get_vdb
from src.jannet.utils.config import Config
from flask import Flask
from api.routes.search import search_bp
from api.routes.markup import markup_bp

from huggingface_hub import login

login(token=Config.HF_TOKEN)
app = Flask(__name__)
CORS(app)
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(markup_bp, url_prefix='/')

host = '0.0.0.0'
port = 5004
_vdb = get_vdb()
_rc = RobotsCache(100)

if __name__ == "__main__":

    ri_client = ReverseIndexCommunicator()
    datalist = []
    with ThreadPoolExecutor() as exe:
        futures = []
        for t_id in range(Config.CRAWL_THREAD_COUNT):
            futures.append(exe.submit(crawl, t_id, _vdb, _rc))
        for _ in range(Config.PROCESS_THREAD_COUNT):
            futures.append(exe.submit(process, _vdb))



        concurrent.futures.wait(futures)
        for f in futures: datalist.append(f.result())


    _vdb.save_to_disk()
    ri_client.commit()


    print(f"Starting Flask server on http://{host}:{port}...")
    app.run(host=host, port=port, debug=False, use_reloader=False)
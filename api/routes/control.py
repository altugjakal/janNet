from src.jannet.managers.worker_controller_manager import get_worker_controller
from flask import jsonify, Blueprint


control_bp = Blueprint('control_bp', __name__)
worker_controller = get_worker_controller()

@control_bp.route("/kill/crawl_workers")
def kill_crawl_workers():
    worker_controller.kill_crawl_workers()

@control_bp.route("/kill/process_workers")
def kill_process_workers():
    worker_controller.kill_process_workers()



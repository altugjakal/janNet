
from huggingface_hub import login

from src.jannet.core.workers.worker_controller.worker_controller import WorkerController
from src.jannet.managers.worker_controller_manager import set_worker_controller
from src.jannet.utils.config import Config
from src.jannet.utils import logging_config # noqa

login(token=Config.HF_TOKEN)

from src.jannet.core.process.reverse_index import ReverseIndexCommunicator
from src.jannet.managers.db_manager import get_vdb, get_db
vdb = get_vdb()
db = get_db()


if __name__ == "__main__":

    ri_client = ReverseIndexCommunicator()
    worker_controller = WorkerController(db, vdb)
    set_worker_controller(worker_controller)
    worker_controller.start_worker_pipeline()




import traceback
from time import sleep

from src.jannet.core.process.index import Index
from src.jannet.core.process.queuers.process_queuer import ProcessQueuer
from src.jannet.managers.db_manager import get_db
from src.jannet.utils.config import Config


def process(vdb, db, pc):



    indexer = Index(db=db, vdb=vdb)

    process_count = 0

    while process_count < Config.MAX_PROCESS:
        try:
            queue = pc.get()

            if not queue:
                print("Processed all, sleeping...")
                sleep(10)
                continue

            url = queue[0]
            content = queue[1]
            id = queue[2]

            print("Next: ", url)

            indexer.process(url, content, id)
            process_count += 1

        except Exception:
            print(f"[process] Exception:")
            traceback.print_exc()
            sleep(5)

    print(f"[process] Process queue cleared, completed iterations: {process_count}")
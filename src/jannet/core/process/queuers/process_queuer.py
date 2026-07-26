import queue
import threading
import time


class ProcessQueuer:
    def __init__(self, db):
        self.db = db
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.running = True
        self.refill_thread = threading.Thread(target=self._refill_loop, daemon=True)
        self.refill_thread.start()



    def _refill_loop(self):
        while self.running:
            if self.queue.qsize() > 0:
                time.sleep(0.1)
                continue

            items = list(self.db.get_process_queue(100))



            if items:
                for item in set(items):
                    self.queue.put(item)
            else:
                time.sleep(1.0)


    def get(self):

        try:
            return self.queue.get(timeout=1.0)
        except queue.Empty:
            return None




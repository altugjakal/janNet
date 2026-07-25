
class ProcessQueuer:
    def __init__(self, db):
        self.db = db
        self.queue = []

    def get(self):
        return self.queue.pop(0)

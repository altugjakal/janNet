_worker_controller = None

def get_worker_controller():
    global _worker_controller
    if _worker_controller is None:
        Exception("Worker Controller not initialized")
        return None
    else:
        return _worker_controller

def set_worker_controller(worker_controller):
    global _worker_controller
    _worker_controller = worker_controller

#TODO: upgrade to Redis+RQ
from datetime import datetime
from queue import Queue, Empty
from time import sleep
from uuid import uuid4

job_queue = Queue(maxsize=1000)


def new_job(job_id: str, model_id: str):
    return{
        "job_id": job_id,
        "model_id": model_id,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "ciphertext_b64": None,
        "error_message": None
    }
jobs = {}

def enqueue_job(model_id: str, ciphertext_b64: str) -> str:
    job_id = uuid4().hex
    if job_queue.full():
        raise RuntimeError(f"Failed to enqueue job {job_id}: Queue Full")

    try:
        job_queue.put(job_id)
    except Exception as e:
        raise RuntimeError(f"Failed to enqueue job {job_id}")

    jobs[job_id] = new_job(job_id,model_id)
    jobs[job_id]["ciphertext_b64"] = ciphertext_b64
    return job_id

def dequeue_worker():
    try:
        current_job = job_queue.get_nowait()
    except Empty:
        sleep(0.1)
        return
    jobs[current_job]["status"]="running"
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

jobs: dict[str, dict] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def reset_jobs() -> None:
    jobs.clear()


def create_job(
        tenant_id: str,
        model_id: str,
        version: str,
        requested_batch_size: int,
) -> str:
    job_id = uuid4().hex
    jobs[job_id] = {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "model_id": model_id,
        "version": version,
        "status": "queued",
        "requested_batch_size": requested_batch_size,
        "created_at": _utc_now_iso(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error_message": None,
    }
    return job_id


def start_job(job_id: str) -> None:
    jobs[job_id]["status"] = "running"
    jobs[job_id]["started_at"] = _utc_now_iso()


def complete_job(
        job_id: str,
        payload: str,
        requested_batch_size: int,
        processed_batch_size: int,
) -> None:
    job = jobs[job_id]
    job["status"] = "completed"
    job["completed_at"] = _utc_now_iso()
    job["result"] = {
        "model_id": job["model_id"],
        "version": job["version"],
        "payload": payload,
        "diagnostics": {
            "requested_batch_size": requested_batch_size,
            "processed_batch_size": processed_batch_size,
            "batch_truncated": processed_batch_size < requested_batch_size,
        },
    }


def fail_job(job_id: str, error_message: str) -> None:
    job = jobs[job_id]
    job["status"] = "failed"
    job["completed_at"] = _utc_now_iso()
    job["error_message"] = error_message


def get_job(job_id: str) -> dict | None:
    return jobs.get(job_id)
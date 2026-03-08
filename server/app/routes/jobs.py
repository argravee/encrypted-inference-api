from fastapi import APIRouter, Depends, HTTPException

from server.core.jobs.queue import get_job
from server.core.security.tenanting import get_tenant_id

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str, tenant_id: str = Depends(get_tenant_id)):
    job = get_job(job_id)
    if job is None or job.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=404, detail="Unknown job")

    status = job["status"]

    if status == "completed":
        return {
            "status": "completed",
            "result": job["result"],
        }

    if status == "failed":
        return {
            "job_id": job["job_id"],
            "model_id": job["model_id"],
            "version": job["version"],
            "status": "failed",
            "error": job.get("error_message") or "Unknown error",
        }

    return {
        "job_id": job["job_id"],
        "model_id": job["model_id"],
        "version": job["version"],
        "status": status,
    }
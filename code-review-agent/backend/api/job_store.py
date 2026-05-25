import uuid
from datetime import datetime
from backend.utils.logger import get_logger
logger = get_logger(__name__)
# Day 21 move this to a database
_jobs: dict[str, dict] = {}


def create_job(job_type: str, metadata: dict) -> str:
    """Create a new job and return its ID"""
    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {
        "id": job_id,
        "type": job_type,     
        "status": "pending",   
        "metadata": metadata,
        "result": None,
        "error": None,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
    }
    logger.info(f"Job created: {job_id} ({job_type})")
    return job_id


def update_job(job_id: str, status: str, result=None, error=None):
    """Update job status"""
    if job_id not in _jobs:
        logger.warning(f"Job not found: {job_id}")
        return
    _jobs[job_id]["status"] = status
    _jobs[job_id]["result"] = result
    _jobs[job_id]["error"] = error
    if status in ("done", "failed"):
        _jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
    logger.info(f"Job {job_id} updated: {status}")


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def get_all_jobs() -> list[dict]:
    return list(_jobs.values())
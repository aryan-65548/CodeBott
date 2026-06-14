from fastapi import APIRouter, HTTPException, Depends, Request
from backend.api.schemas import (
    PRReviewRequest, PRReviewResponse,
    CommitReviewRequest, CommitReviewResponse,
    IssueReviewRequest, IssueReviewResponse,
    HealthResponse,
)
from backend.api.rate_limiter import check_rate_limit
from backend.github.pr_fetcher import get_pr_diff
from backend.github.commit_fetcher import get_commit_diff
from backend.github.issue_fetcher import get_issue_detail
from backend.agent.reviewer import reviewer
from backend.config.settings import settings
from backend.utils.logger import get_logger
from backend.github.pr_fetcher import get_pr_diff, get_pull_requests
from fastapi import Query
from fastapi import Request, Header
from backend.github.webhook_handler import (
    verify_webhook_signature,
    parse_pr_event,
    parse_push_event,
    parse_issue_event,
)
from backend.github.pr_commenter import post_pr_comment
from backend.github.pr_fetcher import get_pr_diff
from backend.github.commit_fetcher import get_commit_diff
from backend.github.issue_fetcher import get_issue_detail
from fastapi import BackgroundTasks
from backend.api.background_tasks import run_pr_review, run_commit_review, run_issue_review
from backend.api.job_store import create_job, update_job, get_job, get_all_jobs
from backend.db.database import get_reviews, get_review_by_id, get_stats, save_review


logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "model": settings.groq_model,
    }

@router.post("/review/pr", response_model=PRReviewResponse, dependencies=[Depends(check_rate_limit)])
async def review_pr(request: PRReviewRequest):
    logger.info(f"POST /review/pr — {request.repo} #{request.pr_number}")
    try:
        pr_data = get_pr_diff(request.repo, request.pr_number)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"PR not found: {e}")

    try:
        result = reviewer.review_pr(pr_data)
        await save_review(
            review_type="pr_review",
            repo=request.repo,
            reference=str(request.pr_number),
            title=pr_data.get("title", f"PR #{request.pr_number}"),
            result=result,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {e}")


@router.post("/review/commit", response_model=CommitReviewResponse, dependencies=[Depends(check_rate_limit)])
async def review_commit(request: CommitReviewRequest):
    logger.info(f"POST /review/commit — {request.repo} {request.sha}")
    try:
        commit_data = get_commit_diff(request.repo, request.sha)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Commit not found: {e}")

    try:
        result = reviewer.review_commit(commit_data)
        await save_review(
            review_type="commit_review",
            repo=request.repo,
            reference=request.sha,
            title=commit_data.get("message", request.sha)[:80],
            result=result,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {e}")


@router.post("/review/issue", response_model=IssueReviewResponse, dependencies=[Depends(check_rate_limit)])
async def review_issue(request: IssueReviewRequest):
    logger.info(f"POST /review/issue — {request.repo} #{request.issue_number}")
    try:
        issue_data = get_issue_detail(request.repo, request.issue_number)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Issue not found: {e}")

    try:
        result = reviewer.review_issue(issue_data)
        await save_review(
            review_type="issue_review",
            repo=request.repo,
            reference=str(request.issue_number),
            title=issue_data.get("title", f"Issue #{request.issue_number}"),
            result=result,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {e}")

@router.get("/test-limit", dependencies=[Depends(check_rate_limit)])
def test_limit():
    return {"ok": True}

@router.get("/pr-files")
def get_pr_files(repo: str = Query(...), pr_number: int = Query(...)):
    """Fetch raw PR files for the DiffViewer"""
    try:
        data = get_pr_diff(repo, pr_number)
        return {"files": data["files"]}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.post("/webhook/github", status_code=202)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
):
    payload_bytes = await request.body()

    if not verify_webhook_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    import json
    try:
        payload = json.loads(payload_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    logger.info(f"Webhook received — event: {x_github_event}")

    if x_github_event == "pull_request":
        pr_info = parse_pr_event(payload)
        if not pr_info:
            return {"status": "ignored", "reason": "action not reviewable"}

        job_id = create_job("pr_review", pr_info)

        async def pr_task():
            update_job(job_id, "running")
            try:
                result = await run_pr_review(
                    pr_info["repo_full_name"],
                    pr_info["pr_number"],
                    post_comment=True,
                )
                update_job(job_id, "done", result=result)
            except Exception as e:
                update_job(job_id, "failed", error=str(e))

        background_tasks.add_task(pr_task)
        return {"status": "accepted", "job_id": job_id}

    elif x_github_event == "push":
        push_info = parse_push_event(payload)
        if not push_info:
            return {"status": "ignored", "reason": "not a main branch push"}

        job_id = create_job("commit_review", push_info)

        async def commit_task():
            update_job(job_id, "running")
            try:
                result = await run_commit_review(
                    push_info["repo_full_name"],
                    push_info["sha"],
                )
                update_job(job_id, "done", result=result)
            except Exception as e:
                update_job(job_id, "failed", error=str(e))

        background_tasks.add_task(commit_task)
        return {"status": "accepted", "job_id": job_id}

    elif x_github_event == "issues":
        issue_info = parse_issue_event(payload)
        if not issue_info:
            return {"status": "ignored", "reason": "action not reviewable"}

        job_id = create_job("issue_review", issue_info)

        async def issue_task():
            update_job(job_id, "running")
            try:
                result = await run_issue_review(
                    issue_info["repo_full_name"],
                    issue_info["issue_number"],
                )
                update_job(job_id, "done", result=result)
            except Exception as e:
                update_job(job_id, "failed", error=str(e))

        background_tasks.add_task(issue_task)
        return {"status": "accepted", "job_id": job_id}

    elif x_github_event == "ping":
        return {"status": "pong"}

    else:
        return {"status": "ignored", "event": x_github_event}
# ─── Job Status ──────────────────────────────────────────────

@router.get("/jobs")
def list_jobs():
    """List all background jobs"""
    return {"jobs": get_all_jobs()}


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Get status of a specific job"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job

# ─── Review History ──────────────────────────────────────────

@router.get("/history")
async def get_review_history(
    repo: str = None,
    type: str = None,
    limit: int = 50,
):
    """Get past reviews with optional filters"""
    reviews = await get_reviews(repo=repo, review_type=type, limit=limit)
    return {"reviews": reviews, "total": len(reviews)}


@router.get("/history/{review_id}")
async def get_review_detail(review_id: int):
    """Get full detail of a specific review"""
    review = await get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"Review {review_id} not found")
    return review


@router.get("/stats")
async def get_dashboard_stats(repo: str = None):
    """Get aggregate stats for dashboard"""
    stats = await get_stats(repo=repo)
    return stats


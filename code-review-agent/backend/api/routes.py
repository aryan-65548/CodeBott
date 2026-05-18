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

logger = get_logger(__name__)
router = APIRouter()


# ─── Health ─────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "model": settings.groq_model,
    }


# ─── PR Review ───────────────────────────────────────────────

@router.post("/review/pr", response_model=PRReviewResponse, dependencies=[Depends(check_rate_limit)])
def review_pr(request: PRReviewRequest):
    logger.info(f"POST /review/pr — {request.repo} #{request.pr_number}")
    try:
        pr_data = get_pr_diff(request.repo, request.pr_number)
    except Exception as e:
        logger.error(f"Failed to fetch PR: {e}")
        raise HTTPException(status_code=404, detail=f"PR not found: {e}")

    try:
        result = reviewer.review_pr(pr_data)
    except Exception as e:
        logger.error(f"Review failed: {e}")
        raise HTTPException(status_code=500, detail=f"Review failed: {e}")

    return result


# ─── Commit Review ───────────────────────────────────────────

@router.post("/review/commit", response_model=CommitReviewResponse, dependencies=[Depends(check_rate_limit)])
def review_commit(request: CommitReviewRequest):
    logger.info(f"POST /review/commit — {request.repo} {request.sha}")
    try:
        commit_data = get_commit_diff(request.repo, request.sha)
    except Exception as e:
        logger.error(f"Failed to fetch commit: {e}")
        raise HTTPException(status_code=404, detail=f"Commit not found: {e}")

    try:
        result = reviewer.review_commit(commit_data)
    except Exception as e:
        logger.error(f"Review failed: {e}")
        raise HTTPException(status_code=500, detail=f"Review failed: {e}")

    return result


# ─── Issue Review ────────────────────────────────────────────

@router.post("/review/issue", response_model=IssueReviewResponse, dependencies=[Depends(check_rate_limit)])
def review_issue(request: IssueReviewRequest):
    logger.info(f"POST /review/issue — {request.repo} #{request.issue_number}")
    try:
        issue_data = get_issue_detail(request.repo, request.issue_number)
    except Exception as e:
        logger.error(f"Failed to fetch issue: {e}")
        raise HTTPException(status_code=404, detail=f"Issue not found: {e}")

    try:
        result = reviewer.review_issue(issue_data)
    except Exception as e:
        logger.error(f"Review failed: {e}")
        raise HTTPException(status_code=500, detail=f"Review failed: {e}")

    return result

@router.get("/test-limit", dependencies=[Depends(check_rate_limit)])
def test_limit():
    return {"ok": True}
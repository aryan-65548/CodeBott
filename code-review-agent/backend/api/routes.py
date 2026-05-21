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

@router.get("/pr-files")
def get_pr_files(repo: str = Query(...), pr_number: int = Query(...)):
    """Fetch raw PR files for the DiffViewer"""
    try:
        data = get_pr_diff(repo, pr_number)
        return {"files": data["files"]}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
):
    payload_bytes = await request.body()

    # step 1 — verify signature
    if not verify_webhook_signature(payload_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    logger.info(f"Webhook received — event: {x_github_event}")

    # step 2 — route by event type
    if x_github_event == "pull_request":
        pr_info = parse_pr_event(payload)
        if not pr_info:
            return {"status": "ignored", "reason": "action not reviewable"}

        logger.info(
            f"Auto-reviewing PR #{pr_info['pr_number']} "
            f"in {pr_info['repo_full_name']} "
            f"(action: {pr_info['action']})"
        )

        try:
            pr_data = get_pr_diff(pr_info["repo_full_name"], pr_info["pr_number"])
            review = reviewer.review_pr(pr_data)
            posted = post_pr_comment(
                pr_info["repo_full_name"],
                pr_info["pr_number"],
                review,
            )
            return {
                "status": "reviewed",
                "pr_number": pr_info["pr_number"],
                "verdict": review.get("verdict"),
                "score": review.get("score"),
                "comment_posted": posted,
            }
        except Exception as e:
            logger.error(f"Auto PR review failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    elif x_github_event == "push":
        push_info = parse_push_event(payload)
        if not push_info:
            return {"status": "ignored", "reason": "not a main branch push"}

        logger.info(f"Auto-reviewing commit {push_info['sha']} in {push_info['repo_full_name']}")

        try:
            commit_data = get_commit_diff(push_info["repo_full_name"], push_info["sha"])
            review = reviewer.review_commit(commit_data)
            return {
                "status": "reviewed",
                "sha": push_info["sha"],
                "score": review.get("score"),
            }
        except Exception as e:
            logger.error(f"Auto commit review failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    elif x_github_event == "issues":
        issue_info = parse_issue_event(payload)
        if not issue_info:
            return {"status": "ignored", "reason": "action not reviewable"}

        logger.info(
            f"Auto-analyzing issue #{issue_info['issue_number']} "
            f"in {issue_info['repo_full_name']}"
        )

        try:
            issue_data = get_issue_detail(
                issue_info["repo_full_name"],
                issue_info["issue_number"],
            )
            review = reviewer.review_issue(issue_data)
            return {
                "status": "analyzed",
                "issue_number": issue_info["issue_number"],
                "priority": review.get("priority"),
                "category": review.get("category"),
            }
        except Exception as e:
            logger.error(f"Auto issue analysis failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    else:
        logger.info(f"Unhandled webhook event type: {x_github_event}")
        return {"status": "ignored", "event": x_github_event}
import asyncio
from backend.github.pr_fetcher import get_pr_diff
from backend.github.commit_fetcher import get_commit_diff
from backend.github.issue_fetcher import get_issue_detail
from backend.github.pr_commenter import post_pr_comment
from backend.agent.reviewer import reviewer
from backend.db.database import save_review
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def run_pr_review(repo_full_name: str, pr_number: int, post_comment: bool = True):
    logger.info(f"[BG] Starting PR review: {repo_full_name} #{pr_number}")
    loop = asyncio.get_event_loop()

    pr_data = await loop.run_in_executor(None, get_pr_diff, repo_full_name, pr_number)
    logger.info(f"[BG] PR data fetched: {len(pr_data['files'])} files")

    review = await loop.run_in_executor(None, reviewer.review_pr, pr_data)
    logger.info(f"[BG] PR #{pr_number} done — verdict: {review.get('verdict')} score: {review.get('score')}")

    # save to database
    await save_review(
        review_type="pr_review",
        repo=repo_full_name,
        reference=str(pr_number),
        title=pr_data.get("title", f"PR #{pr_number}"),
        result=review,
    )

    if post_comment:
        posted = await loop.run_in_executor(
            None, post_pr_comment, repo_full_name, pr_number, review
        )
        if posted:
            logger.info(f"[BG] Comment posted on PR #{pr_number}")

    return review


async def run_commit_review(repo_full_name: str, sha: str):
    logger.info(f"[BG] Starting commit review: {repo_full_name} {sha}")
    loop = asyncio.get_event_loop()

    commit_data = await loop.run_in_executor(None, get_commit_diff, repo_full_name, sha)

    review = await loop.run_in_executor(None, reviewer.review_commit, commit_data)
    logger.info(f"[BG] Commit {sha} done — score: {review.get('score')}")

    await save_review(
        review_type="commit_review",
        repo=repo_full_name,
        reference=sha,
        title=commit_data.get("message", sha)[:80],
        result=review,
    )

    return review


async def run_issue_review(repo_full_name: str, issue_number: int):
    logger.info(f"[BG] Starting issue review: {repo_full_name} #{issue_number}")
    loop = asyncio.get_event_loop()

    issue_data = await loop.run_in_executor(None, get_issue_detail, repo_full_name, issue_number)

    review = await loop.run_in_executor(None, reviewer.review_issue, issue_data)
    logger.info(f"[BG] Issue #{issue_number} done — priority: {review.get('priority')}")

    await save_review(
        review_type="issue_review",
        repo=repo_full_name,
        reference=str(issue_number),
        title=issue_data.get("title", f"Issue #{issue_number}"),
        result=review,
    )

    return review
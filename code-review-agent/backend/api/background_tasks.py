import asyncio
from backend.github.pr_fetcher import get_pr_diff
from backend.github.commit_fetcher import get_commit_diff
from backend.github.issue_fetcher import get_issue_detail
from backend.agent.reviewer import reviewer
from backend.utils.logger import get_logger
from backend.github.pr_commenter import post_pr_comment

logger = get_logger(__name__)

async def run_pr_review(repo_full_name: str, pr_number: int, post_comment: bool = True):
    logger.info(f"[BG] Starting PR review: {repo_full_name} #{pr_number}")
    try:
        loop = asyncio.get_event_loop()

        pr_data = await loop.run_in_executor(
            None, get_pr_diff, repo_full_name, pr_number
        )
        logger.info(f"[BG] PR data fetched: {len(pr_data['files'])} files")

        review = await loop.run_in_executor(
            None, reviewer.review_pr, pr_data
        )
        logger.info(
            f"[BG] PR #{pr_number} review done — "
            f"verdict: {review.get('verdict')} score: {review.get('score')}"
        )

        if post_comment:
            posted = await loop.run_in_executor(
                None, post_pr_comment, repo_full_name, pr_number, review
            )
            if posted:
                logger.info(f"[BG] Comment posted on PR #{pr_number}")
            else:
                logger.warning(f"[BG] Failed to post comment on PR #{pr_number}")

        return review
    except Exception as e:
        logger.error(f"[BG] PR review failed for {repo_full_name} #{pr_number}: {e}")
        raise
async def run_commit_review(repo_full_name: str, sha: str):
    logger.info(f"[BG] Starting commit review: {repo_full_name} {sha}")
    try:
        loop = asyncio.get_event_loop()

        commit_data = await loop.run_in_executor(
            None, get_commit_diff, repo_full_name, sha
        )
        logger.info(f"[BG] Commit data fetched for {sha}")

        review = await loop.run_in_executor(
            None, reviewer.review_commit, commit_data
        )
        logger.info(
            f"[BG] Commit {sha} review done — score: {review.get('score')}"
        )

        return review
    except Exception as e:
        logger.error(f"[BG] Commit review failed for {repo_full_name} {sha}: {e}")
        raise
async def run_issue_review(repo_full_name: str, issue_number: int):
    logger.info(f"[BG] Starting issue analysis: {repo_full_name} #{issue_number}")

    try:
        loop = asyncio.get_event_loop()

        issue_data = await loop.run_in_executor(
            None, get_issue_detail, repo_full_name, issue_number
        )

        review = await loop.run_in_executor(
            None, reviewer.review_issue, issue_data
        )
        logger.info(
            f"[BG] Issue #{issue_number} analysis done — "
            f"priority: {review.get('priority')}"
        )

        return review

    except Exception as e:
        logger.error(f"[BG] Issue review failed for #{issue_number}: {e}")
        raise

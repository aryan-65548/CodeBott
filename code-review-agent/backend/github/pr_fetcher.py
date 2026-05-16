from backend.github.client import github_client
from backend.utils.logger import get_logger

logger = get_logger(__name__)

def get_pull_requests(repo_full_name: str, state: str = "open") -> list[dict]:
    """Fetch all PRs from a repo. state = open | closed | all"""
    repo = github_client.get_repo(repo_full_name)
    prs = repo.get_pulls(state=state, sort="created", direction="desc")

    result = []
    for pr in prs:
        result.append({
            "number": pr.number,
            "title": pr.title,
            "author": pr.user.login,
            "state": pr.state,
            "body": pr.body,
            "created_at": str(pr.created_at),
            "updated_at": str(pr.updated_at),
            "base_branch": pr.base.ref,
            "head_branch": pr.head.ref,
            "url": pr.html_url,
        })

    logger.info(f"Fetched {len(result)} PRs from {repo_full_name}")
    return result


def get_pr_diff(repo_full_name: str, pr_number: int) -> dict:
    """Fetch a single PR with its full file diffs"""
    repo = github_client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    files = pr.get_files()

    changed_files = []
    for f in files:
        changed_files.append({
            "filename": f.filename,
            "status": f.status,           # added | modified | removed
            "additions": f.additions,
            "deletions": f.deletions,
            "changes": f.changes,
            "patch": f.patch or "",       # the actual diff/patch
        })

    return {
        "number": pr.number,
        "title": pr.title,
        "author": pr.user.login,
        "body": pr.body,
        "base_branch": pr.base.ref,
        "head_branch": pr.head.ref,
        "files": changed_files,
        "total_additions": sum(f["additions"] for f in changed_files),
        "total_deletions": sum(f["deletions"] for f in changed_files),
    }


def get_pr_comments(repo_full_name: str, pr_number: int) -> list[dict]:
    """Fetch all comments on a PR"""
    repo = github_client.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    comments = pr.get_issue_comments()

    result = []
    for c in comments:
        result.append({
            "author": c.user.login,
            "body": c.body,
            "created_at": str(c.created_at),
        })

    logger.info(f"Fetched {len(result)} comments on PR #{pr_number}")
    return result
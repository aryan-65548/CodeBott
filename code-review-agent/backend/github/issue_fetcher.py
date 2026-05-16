from backend.github.client import github_client
from backend.utils.logger import get_logger

logger = get_logger(__name__)

def get_issues(repo_full_name: str, state: str = "open") -> list[dict]:
    """Fetch all issues from a repo"""
    repo = github_client.get_repo(repo_full_name)
    issues = repo.get_issues(state=state)

    result = []
    for issue in issues:
        if issue.pull_request:
            continue  # skip PRs that show up as issues
        result.append({
            "number": issue.number,
            "title": issue.title,
            "author": issue.user.login,
            "state": issue.state,
            "body": issue.body,
            "labels": [l.name for l in issue.labels],
            "created_at": str(issue.created_at),
            "url": issue.html_url,
        })

    logger.info(f"Fetched {len(result)} issues from {repo_full_name}")
    return result


def get_issue_detail(repo_full_name: str, issue_number: int) -> dict:
    """Fetch a single issue with all its comments"""
    repo = github_client.get_repo(repo_full_name)
    issue = repo.get_issue(issue_number)
    comments = issue.get_comments()

    return {
        "number": issue.number,
        "title": issue.title,
        "author": issue.user.login,
        "state": issue.state,
        "body": issue.body,
        "labels": [l.name for l in issue.labels],
        "created_at": str(issue.created_at),
        "comments": [
            {
                "author": c.user.login,
                "body": c.body,
                "created_at": str(c.created_at),
            }
            for c in comments
        ],
    }
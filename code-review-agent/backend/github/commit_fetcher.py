from backend.github.client import github_client
from backend.utils.logger import get_logger

logger = get_logger(__name__)

def get_commits(repo_full_name: str, branch: str = None, limit: int = 10) -> list[dict]:
    repo = github_client.get_repo(repo_full_name)
    
    # auto-detect default branch if not specified
    if branch is None:
        branch = repo.default_branch
    
    commits = repo.get_commits(sha=branch)

    result = []
    for i, commit in enumerate(commits):
        if i >= limit:
            break
        result.append({
            "sha": commit.sha[:7],
            "full_sha": commit.sha,
            "message": commit.commit.message,
            "author": commit.commit.author.name,
            "date": str(commit.commit.author.date),
            "url": commit.html_url,
        })

    logger.info(f"Fetched {len(result)} commits from {repo_full_name}@{branch}")
    return result


def get_commit_diff(repo_full_name: str, sha: str) -> dict:
    """Fetch a single commit with its full file diffs"""
    repo = github_client.get_repo(repo_full_name)
    commit = repo.get_commit(sha)

    changed_files = []
    for f in commit.files:
        changed_files.append({
            "filename": f.filename,
            "status": f.status,
            "additions": f.additions,
            "deletions": f.deletions,
            "patch": f.patch or "",
        })

    return {
        "sha": commit.sha[:7],
        "message": commit.commit.message,
        "author": commit.commit.author.name,
        "date": str(commit.commit.author.date),
        "files": changed_files,
        "total_additions": sum(f["additions"] for f in changed_files),
        "total_deletions": sum(f["deletions"] for f in changed_files),
    }
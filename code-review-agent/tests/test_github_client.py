from backend.github.pr_fetcher import get_pull_requests, get_pr_diff
from backend.github.issue_fetcher import get_issues
from backend.github.commit_fetcher import get_commits

REPO = "tiangolo/fastapi"   # change this to any public repo

def test_fetch_prs():
    prs = get_pull_requests(REPO, state="open")
    print(f"\nPRs fetched: {len(prs)}")
    for pr in prs[:2]:
        print(f"  #{pr['number']} — {pr['title']}")

def test_fetch_pr_diff():
    prs = get_pull_requests(REPO, state="open")
    if prs:
        diff = get_pr_diff(REPO, prs[0]["number"])
        print(f"\nPR diff — files changed: {len(diff['files'])}")
        for f in diff["files"][:2]:
            print(f"  {f['status']} {f['filename']}")

def test_fetch_issues():
    issues = get_issues(REPO, state="open")
    print(f"\nIssues fetched: {len(issues)}")

def test_fetch_commits():
    commits = get_commits(REPO, limit=5)   # no branch arg, auto-detects
    print(f"\nCommits fetched: {len(commits)}")
    for c in commits:
        print(f"  {c['sha']} — {c['message'][:50]}")

if __name__ == "__main__":
    test_fetch_prs()
    test_fetch_pr_diff()
    test_fetch_issues()
    test_fetch_commits()
import json
from backend.github.pr_fetcher import get_pr_diff
from backend.github.commit_fetcher import get_commits, get_commit_diff
from backend.github.issue_fetcher import get_issues, get_issue_detail
from backend.agent.reviewer import reviewer

REPO = "tiangolo/fastapi"


def test_review_pr():
    print("\n" + "="*60)
    print("TEST: PR REVIEW")
    print("="*60)

    # grab the first open PR
    from backend.github.pr_fetcher import get_pull_requests
    prs = get_pull_requests(REPO, state="open")
    pr_data = get_pr_diff(REPO, prs[0]["number"])

    result = reviewer.review_pr(pr_data)
    print(json.dumps(result, indent=2))


def test_review_commit():
    print("\n" + "="*60)
    print("TEST: COMMIT REVIEW")
    print("="*60)

    commits = get_commits(REPO, limit=1)
    commit_data = get_commit_diff(REPO, commits[0]["full_sha"])

    result = reviewer.review_commit(commit_data)
    print(json.dumps(result, indent=2))


def test_review_issue():
    print("\n" + "="*60)
    print("TEST: ISSUE REVIEW")
    print("="*60)

    issues = get_issues(REPO, state="open")
    if issues:
        issue_data = get_issue_detail(REPO, issues[0]["number"])
        result = reviewer.review_issue(issue_data)
        print(json.dumps(result, indent=2))
    else:
        print("No open issues found")


if __name__ == "__main__":
    test_review_pr()
    test_review_commit()
    test_review_issue()
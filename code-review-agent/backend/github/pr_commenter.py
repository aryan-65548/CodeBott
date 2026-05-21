from backend.github.client import github_client
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def format_review_comment(review: dict) -> str:
    """Format the AI review as a markdown comment for GitHub"""

    verdict_label = {
        "approve": "APPROVE",
        "request_changes": "REQUEST CHANGES",
        "needs_discussion": "NEEDS DISCUSSION",
    }.get(review.get("verdict"), "NEEDS DISCUSSION")

    score = review.get("score", 0)
    score_bar = "█" * score + "░" * (10 - score)

    lines = [
        f"## AI Code Review",
        f"",
        f"**Verdict:** `{verdict_label}`  ",
        f"**Score:** `{score}/10` `{score_bar}`",
        f"",
        f"### Summary",
        f"{review.get('summary', '')}",
        f"",
    ]

    security_flags = review.get("security_flags", [])
    if security_flags:
        lines += [
            f"### Security Flags",
            *[f"- {flag}" for flag in security_flags],
            f"",
        ]

    issues = review.get("issues", [])
    if issues:
        lines.append(f"### Issues Found ({len(issues)})")
        lines.append("")
        for issue in issues:
            lines += [
                f"#### [{issue.get('severity', '').upper()}] {issue.get('title', '')}",
                f"**File:** `{issue.get('file', 'unknown')}`  ",
                f"**Severity:** `{issue.get('severity', '')}`",
                f"",
                f"{issue.get('description', '')}",
                f"",
            ]
            if issue.get("suggestion"):
                lines += [
                    f"> **Suggestion:** {issue.get('suggestion')}",
                    f"",
                ]

    positives = review.get("positives", [])
    if positives:
        lines += [
            f"### What's Good",
            *[f"- {p}" for p in positives],
            f"",
        ]

    budget = review.get("budget_summary", {})
    if budget:
        lines += [
            f"---",
            f"*{budget.get('included', 0)}/{budget.get('total_files', 0)} files reviewed · "
            f"{review.get('estimated_review_time', 'N/A')} · "
            f"Powered by Groq AI*",
        ]

    return "\n".join(lines)


def post_pr_comment(repo_full_name: str, pr_number: int, review: dict) -> bool:
    """Post the formatted review as a comment on the PR"""
    try:
        repo = github_client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        comment_body = format_review_comment(review)
        pr.create_issue_comment(comment_body)
        logger.info(f"Posted review comment on {repo_full_name} PR #{pr_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to post PR comment: {e}")
        return False
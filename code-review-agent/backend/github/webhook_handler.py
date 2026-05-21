import hmac
import hashlib
from backend.config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def verify_webhook_signature(payload_bytes: bytes, signature_header: str) -> bool:
    if not signature_header:
        logger.warning("Webhook received with no signature header")
        return False
    if not signature_header.startswith("sha256="):
        logger.warning(f"Unexpected signature format: {signature_header[:20]}")
        return False
    expected_signature = "sha256=" + hmac.new(
        key=settings.github_webhook_secret.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()
    is_valid = hmac.compare_digest(expected_signature, signature_header)
    if not is_valid:
        logger.warning("Webhook signature verification FAILED — possible spoofed request")
    else:
        logger.info("Webhook signature verified ✓")

    return is_valid


def parse_pr_event(payload: dict) -> dict | None:
    action = payload.get("action")
    reviewable_actions = ["opened", "synchronize", "reopened"]
    if action not in reviewable_actions:
        logger.info(f"Ignoring PR event with action: {action}")
        return None

    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})

    return {
        "action": action,
        "pr_number": pr.get("number"),
        "pr_title": pr.get("title"),
        "author": pr.get("user", {}).get("login"),
        "repo_full_name": repo.get("full_name"),
        "base_branch": pr.get("base", {}).get("ref"),
        "head_branch": pr.get("head", {}).get("ref"),
        "pr_url": pr.get("html_url"),
    }


def parse_push_event(payload: dict) -> dict | None:
    ref = payload.get("ref", "")
    if not any(ref.endswith(b) for b in ["main", "master", "develop"]):
        logger.info(f"Ignoring push to ref: {ref}")
        return None

    repo = payload.get("repository", {})
    commits = payload.get("commits", [])
    if not commits:
        return None
    
    latest = commits[-1]
    return {
        "sha": latest.get("id"),
        "message": latest.get("message"),
        "author": latest.get("author", {}).get("name"),
        "repo_full_name": repo.get("full_name"),
        "ref": ref,
    }

def parse_issue_event(payload: dict) -> dict | None:
    action = payload.get("action")
    if action != "opened":
        logger.info(f"Ignoring issue event with action: {action}")
        return None
    issue = payload.get("issue", {})
    repo = payload.get("repository", {})
    if issue.get("pull_request"):
        return None

    return {
        "action": action,
        "issue_number": issue.get("number"),
        "title": issue.get("title"),
        "author": issue.get("user", {}).get("login"),
        "repo_full_name": repo.get("full_name"),
        "issue_url": issue.get("html_url"),
    }
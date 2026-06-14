import pytest
import hmac
import hashlib
import json
import httpx
from backend.config.settings import settings

BASE_URL = "http://localhost:8000/api"


def make_signature(payload: bytes) -> str:
    return "sha256=" + hmac.new(
        settings.github_webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()


def make_pr_payload(action: str = "opened", pr_number: int = 1) -> dict:
    return {
        "action": action,
        "pull_request": {
            "number": pr_number,
            "title": "Test PR",
            "user": {"login": "testuser"},
            "base": {"ref": "main"},
            "head": {"ref": "feature/test"},
            "html_url": f"https://github.com/test/repo/pull/{pr_number}",
        },
        "repository": {"full_name": "tiangolo/fastapi"},
    }


@pytest.mark.asyncio
async def test_webhook_ping():
    payload = json.dumps({"zen": "Keep it logically awesome."}).encode()
    sig = make_signature(payload)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/webhook/github",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": sig,
                "X-GitHub-Event": "ping",
            },
        )
    assert response.status_code == 202
    assert response.json()["status"] == "pong"
    print(f"\n Webhook ping passed")


@pytest.mark.asyncio
async def test_webhook_invalid_signature():
    payload = json.dumps({"test": True}).encode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/webhook/github",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": "sha256=invalidsignature",
                "X-GitHub-Event": "ping",
            },
        )
    assert response.status_code == 401
    print(f"\n Invalid signature returns 401")


@pytest.mark.asyncio
async def test_webhook_pr_opened():
    payload_dict = make_pr_payload(action="opened", pr_number=15545)
    payload = json.dumps(payload_dict).encode()
    sig = make_signature(payload)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/webhook/github",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": sig,
                "X-GitHub-Event": "pull_request",
            },
        )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert "job_id" in data
    print(f"\n PR webhook accepted — job_id: {data['job_id']}")


@pytest.mark.asyncio
async def test_webhook_pr_ignored_action():
    payload_dict = make_pr_payload(action="labeled")
    payload = json.dumps(payload_dict).encode()
    sig = make_signature(payload)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/webhook/github",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": sig,
                "X-GitHub-Event": "pull_request",
            },
        )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "ignored"
    print(f"\n Ignored PR action returns ignored status")


@pytest.mark.asyncio
async def test_webhook_unknown_event():
    payload = json.dumps({"test": True}).encode()
    sig = make_signature(payload)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/webhook/github",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": sig,
                "X-GitHub-Event": "star",
            },
        )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "ignored"
    print(f"\n Unknown event type ignored correctly")
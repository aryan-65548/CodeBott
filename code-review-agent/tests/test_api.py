import pytest
import httpx

BASE_URL = "http://localhost:8000/api"


@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data
    assert "version" in data
    print(f"\n Health check passed — model: {data['model']}")


@pytest.mark.asyncio
async def test_review_pr():
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{BASE_URL}/review/pr",
            json={"repo": "tiangolo/fastapi", "pr_number": 15545},
        )
    assert response.status_code == 200
    data = response.json()
    assert "verdict" in data
    assert "score" in data
    assert "summary" in data
    assert "issues" in data
    assert "positives" in data
    assert data["score"] >= 1 and data["score"] <= 10
    assert data["verdict"] in ["approve", "request_changes", "needs_discussion"]
    print(f"\n PR review passed — verdict: {data['verdict']} score: {data['score']}")


@pytest.mark.asyncio
async def test_review_pr_invalid_repo():
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/review/pr",
            json={"repo": "nonexistent/repo-xyz-123", "pr_number": 1},
        )
    assert response.status_code == 404
    print(f"\n Invalid repo returns 404")


@pytest.mark.asyncio
async def test_review_pr_missing_fields():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/review/pr",
            json={"repo": "tiangolo/fastapi"},  # missing pr_number
        )
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "details" in data
    print(f"\n Missing field returns 422 with details")


@pytest.mark.asyncio
async def test_review_issue():
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{BASE_URL}/review/issue",
            json={"repo": "tiangolo/fastapi", "issue_number": 13045},
        )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "priority" in data
    assert "category" in data
    assert "clarity_score" in data
    assert data["priority"] in ["critical", "high", "medium", "low"]
    print(f"\n Issue review passed — priority: {data['priority']} category: {data['category']}")


@pytest.mark.asyncio
async def test_history_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/history")
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "total" in data
    assert isinstance(data["reviews"], list)
    print(f"\n History endpoint passed — {data['total']} reviews found")


@pytest.mark.asyncio
async def test_history_with_filter():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/history?type=pr_review")
    assert response.status_code == 200
    data = response.json()
    for review in data["reviews"]:
        assert review["type"] == "pr_review"
    print(f"\n History filter passed — {data['total']} PR reviews")


@pytest.mark.asyncio
async def test_stats_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_reviews" in data
    assert "average_score" in data
    assert "by_verdict" in data
    assert "by_type" in data
    print(f"\n Stats endpoint passed — {data['total_reviews']} total reviews")


@pytest.mark.asyncio
async def test_rate_limit():
    async with httpx.AsyncClient() as client:
        responses = []
        for _ in range(22):
            r = await client.get(
                f"{BASE_URL}/test-limit",
                headers={"X-Forwarded-For": "10.0.0.55"}
            )
            responses.append(r.status_code)

    status_codes = set(responses)
    assert 429 in status_codes, "Rate limit should trigger after 20 requests"
    print(f"\n Rate limit passed — 429 triggered correctly")
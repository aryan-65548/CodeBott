import pytest
import asyncio
from backend.db.database import init_db, save_review, get_reviews, get_review_by_id, get_stats

SAMPLE_PR_REVIEW = {
    "verdict": "approve",
    "score": 8,
    "summary": "Clean implementation with good test coverage.",
    "issues": [],
    "positives": ["Good naming", "Well structured"],
    "security_flags": [],
    "pr_number": 999,
    "pr_title": "Test PR",
}

SAMPLE_ISSUE_REVIEW = {
    "summary": "Bug report missing reproduction steps.",
    "category": "bug",
    "priority": "high",
    "clarity_score": 5,
    "is_reproducible": False,
    "missing_info": ["Steps to reproduce", "Expected behavior"],
    "suggested_labels": ["bug", "needs-info"],
    "suggested_approach": "Request more info from reporter.",
    "issue_number": 999,
}


@pytest.mark.asyncio
async def test_init_db():
    await init_db()
    print("\n DB initialized successfully")


@pytest.mark.asyncio
async def test_save_and_fetch_pr_review():
    await init_db()
    review_id = await save_review(
        review_type="pr_review",
        repo="test/repo",
        reference="999",
        title="Test PR",
        result=SAMPLE_PR_REVIEW,
    )
    assert isinstance(review_id, int)
    assert review_id > 0

    review = await get_review_by_id(review_id)
    assert review is not None
    assert review["type"] == "pr_review"
    assert review["repo"] == "test/repo"
    assert review["verdict"] == "approve"
    assert review["score"] == 8
    assert review["result"]["summary"] == SAMPLE_PR_REVIEW["summary"]
    print(f"\n Save and fetch PR review passed — id: {review_id}")


@pytest.mark.asyncio
async def test_save_and_fetch_issue_review():
    await init_db()
    review_id = await save_review(
        review_type="issue_review",
        repo="test/repo",
        reference="999",
        title="Test Issue",
        result=SAMPLE_ISSUE_REVIEW,
    )
    assert isinstance(review_id, int)

    review = await get_review_by_id(review_id)
    assert review["type"] == "issue_review"
    assert review["priority"] == "high"
    print(f"\n Save and fetch issue review passed — id: {review_id}")


@pytest.mark.asyncio
async def test_get_reviews_filter():
    await init_db()
    reviews = await get_reviews(repo="test/repo", review_type="pr_review")
    assert isinstance(reviews, list)
    for r in reviews:
        assert r["type"] == "pr_review"
        assert r["repo"] == "test/repo"
    print(f"\n Filter reviews passed — {len(reviews)} found")

@pytest.mark.asyncio
async def test_get_stats():
    await init_db()
    stats = await get_stats()
    assert "total_reviews" in stats
    assert "average_score" in stats
    assert "by_verdict" in stats
    assert "by_type" in stats
    assert stats["total_reviews"] >= 0
    print(f"\n Stats passed — {stats['total_reviews']} total reviews")


@pytest.mark.asyncio
async def test_get_review_not_found():
    await init_db()
    review = await get_review_by_id(999999)
    assert review is None
    print(f"\n Not found returns None correctly")
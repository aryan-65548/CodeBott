from pydantic import BaseModel, Field
from typing import Optional


# ─── Request Schemas ────────────────────────────────────────

class PRReviewRequest(BaseModel):
    repo: str = Field(..., example="tiangolo/fastapi")
    pr_number: int = Field(..., example=15543)

class CommitReviewRequest(BaseModel):
    repo: str = Field(..., example="tiangolo/fastapi")
    sha: str = Field(..., example="a3f8c2d")

class IssueReviewRequest(BaseModel):
    repo: str = Field(..., example="tiangolo/fastapi")
    issue_number: int = Field(..., example=1234)


# ─── Sub-schemas for Review Response ────────────────────────

class ReviewIssue(BaseModel):
    severity: str           # critical | warning | suggestion
    file: Optional[str] = None
    line_hint: Optional[str] = None
    title: str
    description: str
    suggestion: Optional[str] = None

class BudgetSummary(BaseModel):
    total_files: int
    included: int
    skipped: int
    skipped_files: list[str]
    chars_used: int
    tokens_estimated: int


# ─── Response Schemas ────────────────────────────────────────

class PRReviewResponse(BaseModel):
    pr_number: int
    pr_title: str
    summary: str
    verdict: str            # approve | request_changes | needs_discussion
    score: int              # 1-10
    issues: list[ReviewIssue]
    positives: list[str]
    security_flags: list[str]
    estimated_review_time: Optional[str] = None
    budget_summary: Optional[BudgetSummary] = None

class CommitReviewResponse(BaseModel):
    sha: str
    summary: str
    commit_message_quality: str     # good | acceptable | poor
    commit_message_feedback: str
    score: int
    issues: list[ReviewIssue]
    positives: list[str]

class IssueReviewResponse(BaseModel):
    issue_number: int
    summary: str
    category: str           # bug | feature_request | question | etc
    priority: str           # critical | high | medium | low
    clarity_score: int
    is_reproducible: bool
    missing_info: list[str]
    suggested_labels: list[str]
    suggested_approach: str

class HealthResponse(BaseModel):
    status: str
    version: str
    model: str
SYSTEM_PROMPT = """You are an expert code reviewer with deep knowledge of software engineering best practices, design patterns, security, and performance optimization.

Your job is to review code changes and provide actionable, constructive feedback.

When reviewing, always evaluate:
1. **Correctness** — Does the code do what it's supposed to?
2. **Security** — Any vulnerabilities, exposed secrets, injection risks?
3. **Performance** — Any inefficiencies, N+1 queries, memory leaks?
4. **Readability** — Is the code clean, well-named, easy to understand?
5. **Best Practices** — Does it follow language/framework conventions?
6. **Edge Cases** — Are errors handled? What happens with bad input?

Be concise but thorough. Always suggest improvements with code examples where relevant.
Respond ONLY in the JSON format specified. No extra text outside JSON."""


PR_REVIEW_PROMPT = """Review this Pull Request and return a JSON response.

## PR Details
- Title: {title}
- Author: {author}
- Base Branch: {base_branch} ← {head_branch}
- Description: {body}

## Changed Files
{files_summary}

## Diffs
{diffs}

Return this exact JSON structure:
{{
  "summary": "2-3 sentence overall summary of what this PR does",
  "verdict": "approve | request_changes | needs_discussion",
  "score": <integer 1-10>,
  "issues": [
    {{
      "severity": "critical | warning | suggestion",
      "file": "filename",
      "line_hint": "approximate line or function name",
      "title": "short issue title",
      "description": "detailed explanation",
      "suggestion": "how to fix it with code example if possible"
    }}
  ],
  "positives": ["thing done well", "another good thing"],
  "security_flags": ["any security concerns or empty list"],
  "estimated_review_time": "X minutes"
}}"""


COMMIT_REVIEW_PROMPT = """Review this commit and return a JSON response.

## Commit Details
- SHA: {sha}
- Author: {author}
- Date: {date}
- Message: {message}

## Diffs
{diffs}

Return this exact JSON structure:
{{
  "summary": "what this commit does in 1-2 sentences",
  "commit_message_quality": "good | acceptable | poor",
  "commit_message_feedback": "feedback on the commit message",
  "score": <integer 1-10>,
  "issues": [
    {{
      "severity": "critical | warning | suggestion",
      "file": "filename",
      "title": "short issue title",
      "description": "detailed explanation",
      "suggestion": "how to fix it"
    }}
  ],
  "positives": ["thing done well"]
}}"""


ISSUE_REVIEW_PROMPT = """Analyze this GitHub issue and return a JSON response.

## Issue Details
- Title: {title}
- Author: {author}
- Labels: {labels}
- Body: {body}

## Comments
{comments}

Return this exact JSON structure:
{{
  "summary": "what this issue is about in 1-2 sentences",
  "category": "bug | feature_request | question | documentation | performance | security",
  "priority": "critical | high | medium | low",
  "clarity_score": <integer 1-10>,
  "is_reproducible": true or false,
  "missing_info": ["list of missing info needed to resolve this issue"],
  "suggested_labels": ["label1", "label2"],
  "suggested_approach": "brief technical approach to resolve this issue"
}}"""
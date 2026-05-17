import json
from groq import Groq
from backend.config.settings import settings
from backend.agent.prompts import (
    SYSTEM_PROMPT,
    PR_REVIEW_PROMPT,
    COMMIT_REVIEW_PROMPT,
    ISSUE_REVIEW_PROMPT,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class CodeReviewer:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        logger.info(f"CodeReviewer initialized with model: {self.model}")

    def _call_llm(self, user_prompt: str) -> dict:
        """Send prompt to Groq and parse JSON response"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,     
                max_tokens=4096,
            )

            raw = response.choices[0].message.content.strip()
            logger.debug(f"Raw LLM response: {raw[:200]}...")

            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            return json.loads(raw)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            return {"error": "Failed to parse review", "raw": raw}
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def _format_diffs(self, files: list[dict]) -> str:
        """Format file diffs into a readable string for the prompt"""
        output = []
        for f in files:
            output.append(f"### {f['status'].upper()}: {f['filename']}")
            output.append(f"+{f['additions']} additions, -{f['deletions']} deletions")
            if f.get("patch"):
                patch = f["patch"]
                if len(patch) > 3000:
                    patch = patch[:3000] + "\n... [truncated for length]"
                output.append(f"```diff\n{patch}\n```")
            output.append("")
        return "\n".join(output)

    def _format_files_summary(self, files: list[dict]) -> str:
        """Short summary of changed files"""
        lines = []
        for f in files:
            lines.append(f"- {f['status']}: {f['filename']} (+{f['additions']}/-{f['deletions']})")
        return "\n".join(lines)

    def review_pr(self, pr_data: dict) -> dict:
        """Review a pull request"""
        logger.info(f"Reviewing PR #{pr_data['number']}: {pr_data['title']}")

        diffs = self._format_diffs(pr_data["files"])
        files_summary = self._format_files_summary(pr_data["files"])

        prompt = PR_REVIEW_PROMPT.format(
            title=pr_data["title"],
            author=pr_data["author"],
            base_branch=pr_data["base_branch"],
            head_branch=pr_data["head_branch"],
            body=pr_data.get("body") or "No description provided.",
            files_summary=files_summary,
            diffs=diffs,
        )

        result = self._call_llm(prompt)
        result["pr_number"] = pr_data["number"]
        result["pr_title"] = pr_data["title"]
        logger.info(f"PR #{pr_data['number']} review complete — verdict: {result.get('verdict')} score: {result.get('score')}")
        return result

    def review_commit(self, commit_data: dict) -> dict:
        """Review a commit"""
        logger.info(f"Reviewing commit {commit_data['sha']}: {commit_data['message'][:50]}")

        diffs = self._format_diffs(commit_data["files"])

        prompt = COMMIT_REVIEW_PROMPT.format(
            sha=commit_data["sha"],
            author=commit_data["author"],
            date=commit_data["date"],
            message=commit_data["message"],
            diffs=diffs,
        )

        result = self._call_llm(prompt)
        result["sha"] = commit_data["sha"]
        logger.info(f"Commit {commit_data['sha']} review complete — score: {result.get('score')}")
        return result

    def review_issue(self, issue_data: dict) -> dict:
        """Review/analyze a GitHub issue"""
        logger.info(f"Analyzing issue #{issue_data['number']}: {issue_data['title']}")

        comments_text = ""
        for c in issue_data.get("comments", []):
            comments_text += f"**{c['author']}**: {c['body']}\n\n"

        prompt = ISSUE_REVIEW_PROMPT.format(
            title=issue_data["title"],
            author=issue_data["author"],
            labels=", ".join(issue_data.get("labels", [])) or "none",
            body=issue_data.get("body") or "No description provided.",
            comments=comments_text or "No comments yet.",
        )

        result = self._call_llm(prompt)
        result["issue_number"] = issue_data["number"]
        logger.info(f"Issue #{issue_data['number']} analysis complete — priority: {result.get('priority')}")
        return result


reviewer = CodeReviewer()
from backend.utils.logger import get_logger
from backend.utils.diff_parser import diff_parser

logger = get_logger(__name__)

# rough estimate: 1 token ≈ 4 characters for code
CHARS_PER_TOKEN = 4

# token budgets
TOTAL_TOKEN_BUDGET = 10_000
SYSTEM_PROMPT_TOKENS = 500
METADATA_TOKENS = 300
RESPONSE_TOKENS = 2_000
SAFETY_BUFFER = 500

# what's left for diffs
DIFF_TOKEN_BUDGET = TOTAL_TOKEN_BUDGET - SYSTEM_PROMPT_TOKENS - METADATA_TOKENS - RESPONSE_TOKENS - SAFETY_BUFFER
DIFF_CHAR_BUDGET = DIFF_TOKEN_BUDGET * CHARS_PER_TOKEN  # ~28,000 chars


class CodeFormatter:

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate — 1 token per 4 chars"""
        return len(text) // CHARS_PER_TOKEN

    def truncate_patch(self, patch: str, max_chars: int) -> str:
        """Truncate a single file's patch to max_chars"""
        if len(patch) <= max_chars:
            return patch
        truncated = patch[:max_chars]
        # cut at last newline so we don't cut mid-line
        last_newline = truncated.rfind("\n")
        if last_newline > 0:
            truncated = truncated[:last_newline]
        return truncated + f"\n... [truncated — {len(patch) - max_chars} chars omitted]"

    def prioritize_files(self, files: list[dict]) -> list[dict]:
        """
        Sort files by risk score — most important files reviewed first.
        Auto-generated files are removed entirely.
        """
        # filter out auto-generated files
        reviewable = [
            f for f in files
            if not diff_parser.is_auto_generated(f.get("filename", ""))
        ]

        skipped = len(files) - len(reviewable)
        if skipped > 0:
            logger.info(f"Skipped {skipped} auto-generated files")

        # sort by risk score descending
        reviewable.sort(
            key=lambda f: diff_parser.get_file_risk_score(f),
            reverse=True
        )

        return reviewable

    def build_diff_context(self, files: list[dict]) -> tuple[str, dict]:
        """
        Build the best possible diff context within the token budget.
        Returns the formatted diff string and a summary of what was included.

        Strategy:
        1. Filter auto-generated files
        2. Sort by risk score
        3. Add files one by one until budget is exhausted
        4. Truncate the last file that partially fits
        """
        prioritized = self.prioritize_files(files)
        
        output = []
        chars_used = 0
        included_files = []
        skipped_files = []

        for file in prioritized:
            filename = file.get("filename", "unknown")
            status = file.get("status", "modified")
            additions = file.get("additions", 0)
            deletions = file.get("deletions", 0)
            patch = file.get("patch", "")

            # file header always included
            header = f"### {status.upper()}: {filename} (+{additions}/-{deletions})\n"
            
            # get function names changed in this file
            functions = diff_parser.extract_function_names(patch)
            if functions:
                header += f"Changed functions: {', '.join(functions)}\n"

            chars_remaining = DIFF_CHAR_BUDGET - chars_used

            # not enough room even for header
            if len(header) > chars_remaining:
                skipped_files.append(filename)
                continue

            chars_used += len(header)
            output.append(header)

            if patch:
                chars_for_patch = chars_remaining - len(header)
                
                if len(patch) <= chars_for_patch:
                    # full patch fits
                    output.append(f"```diff\n{patch}\n```\n")
                    chars_used += len(patch)
                    included_files.append({"file": filename, "coverage": "full"})
                else:
                    # partial patch
                    truncated = self.truncate_patch(patch, chars_for_patch - 20)
                    output.append(f"```diff\n{truncated}\n```\n")
                    chars_used += len(truncated)
                    included_files.append({"file": filename, "coverage": "partial"})
                    
                    # budget exhausted after this file
                    remaining = [f["filename"] for f in prioritized if f["filename"] not in [i["file"] for i in included_files]]
                    skipped_files.extend(remaining)
                    break
            else:
                included_files.append({"file": filename, "coverage": "no_patch"})

        summary = {
            "total_files": len(files),
            "included": len(included_files),
            "skipped": len(skipped_files),
            "skipped_files": skipped_files,
            "chars_used": chars_used,
            "tokens_estimated": self.estimate_tokens("".join(output)),
        }

        if skipped_files:
            logger.warning(f"Budget exceeded — skipped files: {skipped_files}")

        logger.debug(f"Diff context: {summary}")
        return "\n".join(output), summary

    def format_files_summary(self, files: list[dict]) -> str:
        """Short one-line summary of every changed file"""
        lines = []
        for f in files:
            risk = diff_parser.get_file_risk_score(f)
            auto = " [auto-generated, skipped]" if diff_parser.is_auto_generated(f["filename"]) else ""
            lines.append(
                f"- {f['status']}: {f['filename']} "
                f"(+{f['additions']}/-{f['deletions']}, risk score: {risk}){auto}"
            )
        return "\n".join(lines)


code_formatter = CodeFormatter()
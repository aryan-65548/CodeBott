import json
from backend.utils.diff_parser import diff_parser
from backend.utils.code_formatter import code_formatter
from backend.github.pr_fetcher import get_pull_requests, get_pr_diff

REPO = "tiangolo/fastapi"


def test_parse_diff():
    print("\n" + "="*60)
    print("TEST: DIFF PARSER")
    print("="*60)

    prs = get_pull_requests(REPO, state="open")
    pr_data = get_pr_diff(REPO, prs[0]["number"])

    for file in pr_data["files"][:2]:
        if file["patch"]:
            print(f"\nFile: {file['filename']}")
            hunks = diff_parser.parse(file["patch"])
            print(f"Hunks found: {len(hunks)}")
            for hunk in hunks[:1]:
                print(f"  Header: {hunk['header']}")
                print(f"  Additions: {hunk['additions']}")
                print(f"  Deletions: {hunk['deletions']}")
                print(f"  Lines: {len(hunk['lines'])}")

            functions = diff_parser.extract_function_names(file["patch"])
            print(f"Changed functions: {functions}")

            risk = diff_parser.get_file_risk_score(file)
            print(f"Risk score: {risk}")


def test_token_budget():
    print("\n" + "="*60)
    print("TEST: TOKEN BUDGET MANAGER")
    print("="*60)

    prs = get_pull_requests(REPO, state="open")
    pr_data = get_pr_diff(REPO, prs[0]["number"])

    diffs, summary = code_formatter.build_diff_context(pr_data["files"])

    print(f"\nBudget Summary:")
    print(json.dumps(summary, indent=2))
    print(f"\nFormatted diff preview (first 500 chars):")
    print(diffs[:500])


def test_auto_generated_detection():
    print("\n" + "="*60)
    print("TEST: AUTO-GENERATED FILE DETECTION")
    print("="*60)

    test_files = [
        "package-lock.json",
        "yarn.lock",
        "dist/bundle.min.js",
        "backend/main.py",
        "frontend/src/App.jsx",
        "__pycache__/settings.cpython-311.pyc",
    ]

    for f in test_files:
        is_auto = diff_parser.is_auto_generated(f)
        status = "SKIP" if is_auto else "REVIEW"
        print(f"  [{status}] {f}")


if __name__ == "__main__":
    test_auto_generated_detection()
    test_parse_diff()
    test_token_budget()
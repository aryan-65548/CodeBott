import pytest
from backend.utils.diff_parser import diff_parser
from backend.utils.code_formatter import code_formatter

SAMPLE_PATCH = """@@ -1,6 +1,8 @@
 def hello():
-    print("hi")
+    print("hello world")
+    return True
 
 def goodbye():
-    pass
+    print("bye")
"""


def test_parse_basic_patch():
    hunks = diff_parser.parse(SAMPLE_PATCH)
    assert len(hunks) == 1
    assert hunks[0]["additions"] == 3
    assert hunks[0]["deletions"] == 2
    print(f"\n Patch parsing passed — {len(hunks)} hunk found")


def test_get_changed_lines():
    lines = diff_parser.get_changed_lines(SAMPLE_PATCH)
    additions = [l for l in lines if l.startswith("+")]
    deletions = [l for l in lines if l.startswith("-")]
    assert len(additions) == 3
    assert len(deletions) == 2
    print(f"\n Changed lines — {len(additions)} additions, {len(deletions)} deletions")


def test_extract_function_names():
    patch = """@@ -1,3 +1,3 @@
+def my_function():
+    pass
+class MyClass:
"""
    names = diff_parser.extract_function_names(patch)
    assert "my_function" in names
    assert "MyClass" in names
    print(f"\n Function extraction passed — found: {names}")


def test_auto_generated_detection():
    assert diff_parser.is_auto_generated("package-lock.json") == True
    assert diff_parser.is_auto_generated("yarn.lock") == True
    assert diff_parser.is_auto_generated("dist/bundle.min.js") == True
    assert diff_parser.is_auto_generated("backend/main.py") == False
    assert diff_parser.is_auto_generated("frontend/src/App.jsx") == False
    print(f"\n Auto-generated detection passed")


def test_file_risk_score():
    auth_file   = {"filename": "auth/login.py",       "additions": 10, "deletions": 5, "patch": ""}
    test_file   = {"filename": "tests/test_login.py", "additions": 10, "deletions": 5, "patch": ""}
    config_file = {"filename": "config/settings.py",  "additions": 5,  "deletions": 2, "patch": ""}

    auth_score   = diff_parser.get_file_risk_score(auth_file)
    test_score   = diff_parser.get_file_risk_score(test_file)
    config_score = diff_parser.get_file_risk_score(config_file)

    # auth scores highest — security sensitive filename
    assert auth_score > test_score
    assert auth_score > config_score
    # all scores are positive
    assert auth_score > 0
    assert config_score > 0
    print(f"\n Risk scoring — auth: {auth_score}, config: {config_score}, test: {test_score}")


def test_token_budget():
    files = [
        {"filename": "main.py", "status": "modified", "additions": 10,
         "deletions": 5, "patch": SAMPLE_PATCH},
        {"filename": "package-lock.json", "status": "modified",
         "additions": 100, "deletions": 50, "patch": "huge content"},
    ]
    diffs, summary = code_formatter.build_diff_context(files)
    assert summary["total_files"] == 2
    assert "package-lock.json" not in diffs
    print(f"\n Token budget passed — {summary['included']}/{summary['total_files']} files included")
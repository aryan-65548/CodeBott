import re
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class DiffParser:

    def parse(self, raw_patch: str) -> list[dict]:
        """
        Parse a raw git patch into a list of hunks.
        Each hunk is a changed block within a file.
        """
        if not raw_patch:
            return []

        hunks = []
        current_hunk = None

        for line in raw_patch.splitlines():
            # hunk header like @@ -1,4 +1,6 @@
            if line.startswith("@@"):
                if current_hunk:
                    hunks.append(current_hunk)
                current_hunk = {
                    "header": line,
                    "lines": [],
                    "additions": 0,
                    "deletions": 0,
                }
            elif current_hunk is not None:
                if line.startswith("+"):
                    current_hunk["lines"].append({
                        "type": "addition",
                        "content": line[1:], 
                    })
                    current_hunk["additions"] += 1
                elif line.startswith("-"):
                    current_hunk["lines"].append({
                        "type": "deletion",
                        "content": line[1:],
                    })
                    current_hunk["deletions"] += 1
                else:
                    current_hunk["lines"].append({
                        "type": "context",
                        "content": line[1:] if line.startswith(" ") else line,
                    })

        if current_hunk:
            hunks.append(current_hunk)

        return hunks

    def get_changed_lines(self, raw_patch: str) -> list[str]:
        """Extract only the added and removed lines — no context lines"""
        changed = []
        for line in raw_patch.splitlines():
            if line.startswith("+") or line.startswith("-"):
                if not line.startswith("+++") and not line.startswith("---"):
                    changed.append(line)
        return changed

    def extract_function_names(self, raw_patch: str) -> list[str]:
        """
        Try to extract function/class names that were changed.
        Looks for def, class, function, const, async def patterns.
        """
        names = []
        patterns = [
            r"^[+-]?\s*def\s+(\w+)",           
            r"^[+-]?\s*async def\s+(\w+)",      
            r"^[+-]?\s*class\s+(\w+)",          
            r"^[+-]?\s*function\s+(\w+)",        
            r"^[+-]?\s*const\s+(\w+)\s*=",     
            r"^[+-]?\s*export\s+function\s+(\w+)", 
        ]
        for line in raw_patch.splitlines():
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    name = match.group(1)
                    if name not in names:
                        names.append(name)
        return names

    def is_auto_generated(self, filename: str) -> bool:
        """Detect auto-generated files that shouldn't be reviewed"""
        auto_gen_patterns = [
            "package-lock.json",
            "poetry.lock",
            ".lock",           
            ".min.js",        
            ".min.css",        
            "dist/",          
            "build/",          
            "__pycache__/",  
            ".pyc",           
            "migration",       
            ".map",             
        ]
        return any(pattern in filename for pattern in auto_gen_patterns)

    def get_file_risk_score(self, file: dict) -> int:
        """
        Score a file by how risky/important its changes are.
        Higher score = review this file first.
        """
        score = 0
        filename = file.get("filename", "")
        patch = file.get("patch", "")

        score += file.get("deletions", 0) * 2
        score += file.get("additions", 0)

        # security sensitive files
        security_patterns = [
            "auth", "login", "password", "token", "secret",
            "permission", "admin", "security", "crypto", "jwt"
        ]
        if any(p in filename.lower() for p in security_patterns):
            score += 50


        config_patterns = [".env", "config", "settings", "docker", "nginx"]
        if any(p in filename.lower() for p in config_patterns):
            score += 30

       
        if filename.endswith((".py", ".js", ".ts", ".go", ".rs", ".java")):
            score += 20

        # test files are lower priority
        if "test" in filename.lower() or "spec" in filename.lower():
            score -= 10

        
        risky_patterns = [
            "eval(", "exec(", "shell=True", "subprocess",
            "password", "secret", "api_key", "token",
            "TODO", "FIXME", "HACK", "XXX",
        ]
        if patch:
            for pattern in risky_patterns:
                if pattern in patch:
                    score += 15

        return score


diff_parser = DiffParser()
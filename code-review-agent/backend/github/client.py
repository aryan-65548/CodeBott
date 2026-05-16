from github import Github
from backend.config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class GitHubClient:
    def __init__(self):
        self.client = Github(settings.github_token)
        logger.info("GitHub client initialized")

    def get_repo(self, repo_full_name: str):
        """
        repo_full_name: 'owner/repo-name'
        example: 'torvalds/linux'
        """
        try:
            repo = self.client.get_repo(repo_full_name)
            logger.info(f"Fetched repo: {repo_full_name}")
            return repo
        except Exception as e:
            logger.error(f"Failed to fetch repo {repo_full_name}: {e}")
            raise

github_client = GitHubClient()
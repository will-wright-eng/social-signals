from ..utils.gh_analyzer import RepositoryAnalyzer
from ..utils.gh_repo_dao import RepositoryDAO
from ..utils.gh_repo_service import RepositoryService


def _init_services():
    """Initialize services"""
    repository_dao = RepositoryDAO()
    analyzer = RepositoryAnalyzer(repository_dao)
    return RepositoryService(repository_dao, analyzer)

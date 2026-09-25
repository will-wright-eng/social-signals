import pytest

from sosig.utils.gh_utils import (
    GitHubAPIError,
    GitCommandError,
    GitHubAnalyzerImpl,
    DefaultCommandRunner,
)


class FailingCommandRunner:
    def run_command(self, command, cwd):
        raise GitCommandError(message="Command execution failed", command=" ".join(command), returncode=1)


@pytest.fixture
def analyzer(tmp_path):
    return GitHubAnalyzerImpl(str(tmp_path), command_runner=FailingCommandRunner())


def test_open_issues_falls_back_to_zero_when_gh_fails(analyzer):
    assert analyzer.get_open_issues() == 0


def test_stars_raises_github_api_error_when_gh_fails(analyzer):
    with pytest.raises(GitHubAPIError) as exc_info:
        analyzer.get_stars()
    assert exc_info.value.status_code == 1


def test_username_raises_github_api_error_when_gh_fails(analyzer):
    with pytest.raises(GitHubAPIError):
        analyzer.get_repo_username()


def test_missing_executable_raises_git_command_error(tmp_path):
    with pytest.raises(GitCommandError):
        DefaultCommandRunner().run_command(["sosig-test-no-such-command"], str(tmp_path))

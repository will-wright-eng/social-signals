import os

import pytest
from sosig.main import app
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def temp_workspace(tmp_path):
    """Provide a temporary workspace directory"""
    return tmp_path / "workspace"


@pytest.fixture
def mock_db(mocker, tmp_path):
    """Mock database interactions with a temporary database"""
    import sosig
    from sosig.core.db import Database

    test_db_path = tmp_path / "test.db"
    # Delete the file if it exists
    if test_db_path.exists():
        test_db_path.unlink()

    # Create a unique database URL for each test worker
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "")
    db_path = f"sqlite:///{test_db_path}{worker_id}"

    db = Database(db_path=db_path)

    # Patch get_db at the module level where it's imported
    mock = mocker.patch("sosig.core.db.get_db", return_value=db)
    # Also patch where it's used in commands
    mocker.patch("sosig.commands.db_cmds.get_db", return_value=db)
    mocker.patch("sosig.commands.config_cmds.get_db", return_value=db)

    # Also patch the main db instance to avoid conflicts
    sosig.db = db

    yield mock

    # Cleanup after test
    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture
def mock_repo_service(mocker):
    """Mock repository service"""
    mock = mocker.patch("sosig.commands.gh_cmds._init_services")
    return mock


@pytest.fixture
def mock_display(mocker):
    """Mock display service"""
    return mocker.patch("sosig.utils.display_service.display")


def test_main_help():
    """Test main help command"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "config" in result.stdout
    assert "gh" in result.stdout
    assert "db" in result.stdout


def test_config_show(mock_db):
    """Test config show command"""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "Config directory" in result.stdout


def test_gh_analyze(temp_workspace, mock_repo_service, mock_db):
    """Test gh analyze command"""
    mock_service = mock_repo_service.return_value
    mock_service.analyze_repositories.return_value = []

    result = runner.invoke(app, ["gh", "analyze", "test/repo", "--workspace", str(temp_workspace)])
    assert result.exit_code == 0
    mock_service.analyze_repositories.assert_called_once()


def test_invalid_sort_field(mock_db):
    """Test db list command with invalid sort field"""
    result = runner.invoke(app, ["db", "list", "--sort", "invalid_field"])
    assert result.exit_code == 1
    assert "Invalid sort field" in result.stdout


def test_db_remove_without_confirmation(mock_db):
    """Test db remove command without confirmation"""
    result = runner.invoke(app, ["db", "remove"])
    assert result.exit_code == 1
    assert "Include --drop-db flag" in result.stdout


def test_db_remove_with_confirmation(mocker, mock_db):
    """Test db remove command with confirmation"""
    mock_db_instance = mock_db.return_value
    mock_db_instance.remove_db = mocker.Mock(return_value=True)

    result = runner.invoke(app, ["db", "remove", "--drop-db"], input="y\n")
    assert result.exit_code == 0
    assert "Successfully dropped database file" in result.stdout

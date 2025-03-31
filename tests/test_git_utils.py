"""
Tests for the git utilities module
"""
import pytest
from auto_commit_bot.git_utils import (
    run_git_command,
    get_git_diff,
    stage_all_changes,
    commit_changes,
    is_git_repo,
    has_staged_changes,
    get_changed_files
)

@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess.Popen"""
    mock = mocker.patch("subprocess.Popen")
    mock.return_value.communicate.return_value = ("output", "error")
    mock.return_value.returncode = 0
    return mock

def test_run_git_command_success(mock_subprocess):
    """Test successful git command execution"""
    stdout, stderr, code = run_git_command(["git", "status"])
    assert stdout == "output"
    assert stderr == "error"
    assert code == 0
    mock_subprocess.assert_called_once()

def test_run_git_command_failure(mock_subprocess):
    """Test failed git command execution"""
    mock_subprocess.return_value.returncode = 1
    stdout, stderr, code = run_git_command(["git", "invalid"])
    assert code == 1

def test_run_git_command_exception(mock_subprocess):
    """Test git command execution with exception"""
    mock_subprocess.side_effect = Exception("Command failed")
    stdout, stderr, code = run_git_command(["git", "status"])
    assert code == 1
    assert "Command failed" in stderr

def test_get_git_diff_staged(mocker):
    """Test getting staged git diff"""
    mock_run = mocker.patch("auto_commit_bot.git_utils.run_git_command")
    mock_run.return_value = ("diff output", "", 0)
    
    diff = get_git_diff(staged=True)
    assert diff == "diff output"
    mock_run.assert_called_with(["git", "diff", "--staged"])

def test_get_git_diff_unstaged(mocker):
    """Test getting unstaged git diff"""
    mock_run = mocker.patch("auto_commit_bot.git_utils.run_git_command")
    mock_run.return_value = ("diff output", "", 0)
    
    diff = get_git_diff(staged=False)
    assert diff == "diff output"
    mock_run.assert_called_with(["git", "diff"])

def test_stage_all_changes(mocker):
    """Test staging all changes"""
    mock_run = mocker.patch("auto_commit_bot.git_utils.run_git_command")
    mock_run.return_value = ("", "", 0)
    
    assert stage_all_changes() is True
    mock_run.assert_called_with(["git", "add", "."])

def test_commit_changes(mocker):
    """Test committing changes"""
    mock_run = mocker.patch("auto_commit_bot.git_utils.run_git_command")
    mock_run.return_value = ("", "", 0)
    
    message = "test commit"
    assert commit_changes(message) is True
    mock_run.assert_called_with(["git", "commit", "-m", message])

def test_is_git_repo(mocker):
    """Test git repository check"""
    mock_run = mocker.patch("auto_commit_bot.git_utils.run_git_command")
    
    # Test valid git repo
    mock_run.return_value = ("", "", 0)
    assert is_git_repo() is True
    
    # Test invalid git repo
    mock_run.return_value = ("", "", 1)
    assert is_git_repo() is False

def test_has_staged_changes(mocker):
    """Test staged changes check"""
    mock_run = mocker.patch("auto_commit_bot.git_utils.run_git_command")
    
    # Test with staged changes
    mock_run.return_value = ("file1.py\nfile2.py", "", 0)
    assert has_staged_changes() is True
    
    # Test without staged changes
    mock_run.return_value = ("", "", 0)
    assert has_staged_changes() is False

def test_get_changed_files(mocker):
    """Test getting changed files"""
    mock_run = mocker.patch("auto_commit_bot.git_utils.run_git_command")
    mock_run.return_value = ("file1.py\nfile2.py", "", 0)
    
    # Test staged files
    files = get_changed_files(staged=True)
    assert files == ["file1.py", "file2.py"]
    mock_run.assert_called_with(["git", "diff", "--name-only", "--staged"])
    
    # Test unstaged files
    files = get_changed_files(staged=False)
    assert files == ["file1.py", "file2.py"]
    mock_run.assert_called_with(["git", "diff", "--name-only"]) 
"""
Tests for the CLI module
"""
import pytest
from click.testing import CliRunner
from auto_commit_bot.cli import cli, commit, configure

@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()

@pytest.fixture
def mock_git_utils(mocker):
    """Mock git utilities"""
    mocker.patch("auto_commit_bot.cli.is_git_repo", return_value=True)
    mocker.patch("auto_commit_bot.cli.has_staged_changes", return_value=True)
    mocker.patch("auto_commit_bot.cli.get_git_diff", return_value="test diff")
    mocker.patch("auto_commit_bot.cli.stage_all_changes", return_value=True)
    mocker.patch("auto_commit_bot.cli.commit_changes", return_value=True)
    return mocker

@pytest.fixture
def mock_llm_provider(mocker):
    """Mock LLM provider"""
    mock = mocker.patch("auto_commit_bot.cli.LLMProvider")
    mock.return_value.generate_commit_message.return_value = "feat(test): add new feature"
    return mock

def test_commit_success(runner, mock_git_utils, mock_llm_provider):
    """Test successful commit command"""
    mock_git_utils.patch("auto_commit_bot.cli.get_changed_files",
                        return_value=["file1.py", "file2.py"])
    result = runner.invoke(cli, ["commit"])
    
    assert result.exit_code == 0
    assert "✅ Analyzing changes..." in result.output
    assert "file1.py" in result.output
    assert "file2.py" in result.output
    assert "feat(test): add new feature" in result.output
    assert "✅ Changes committed successfully!" in result.output

def test_commit_not_git_repo(runner, mock_git_utils, mock_llm_provider):
    """Test commit in non-git repository"""
    mock_git_utils.patch("auto_commit_bot.cli.is_git_repo", return_value=False)
    result = runner.invoke(cli, ["commit"])
    
    assert result.exit_code == 1
    assert "Error: Not a git repository" in result.output

def test_commit_no_staged_changes(runner, mock_git_utils, mock_llm_provider):
    """Test commit with no staged changes"""
    mock_git_utils.patch("auto_commit_bot.cli.has_staged_changes", return_value=False)
    result = runner.invoke(cli, ["commit"])
    
    assert result.exit_code == 1
    assert "Error: No staged changes to commit" in result.output

def test_commit_stage_all_failure(runner, mock_git_utils, mock_llm_provider):
    """Test commit with stage-all failure"""
    mock_git_utils.patch("auto_commit_bot.cli.stage_all_changes", return_value=False)
    result = runner.invoke(cli, ["commit", "--stage-all"])
    
    assert result.exit_code == 1
    assert "Error: Failed to stage changes" in result.output

def test_commit_message_generation_failure(runner, mock_git_utils, mock_llm_provider):
    """Test commit with message generation failure"""
    mock_git_utils.patch("auto_commit_bot.cli.get_changed_files",
                        return_value=["file1.py", "file2.py"])
    mock_llm_provider.return_value.generate_commit_message.return_value = None
    result = runner.invoke(cli, ["commit"])
    
    assert result.exit_code == 1
    assert "Error: Failed to generate commit message" in result.output

def test_commit_dry_run(runner, mock_git_utils, mock_llm_provider):
    """Test commit in dry-run mode"""
    mock_git_utils.patch("auto_commit_bot.cli.get_changed_files",
                        return_value=["file1.py", "file2.py"])
    result = runner.invoke(cli, ["commit", "--dry-run"])
    
    assert result.exit_code == 0
    assert "✅ Generated commit message:" in result.output
    assert "feat(test): add new feature" in result.output
    assert "✅ Changes committed successfully!" not in result.output

def test_configure_provider(runner, mocker):
    """Test configure command with provider"""
    mock_config = mocker.patch("auto_commit_bot.cli.config")
    result = runner.invoke(cli, ["configure", "--provider", "api"])
    
    assert result.exit_code == 0
    assert "Set provider type to: api" in result.output
    mock_config.set.assert_called_with("provider_type", "api")

def test_configure_api_key(runner, mocker):
    """Test configure command with API key"""
    mock_config = mocker.patch("auto_commit_bot.cli.config")
    result = runner.invoke(cli, [
        "configure",
        "--provider", "api",
        "--api-key", "test-key"
    ])
    
    assert result.exit_code == 0
    assert "Updated Hugging Face API key" in result.output
    mock_config.set.assert_called_with("huggingface_api_key", "test-key")

def test_configure_model(runner, mocker):
    """Test configure command with model"""
    mock_config = mocker.patch("auto_commit_bot.cli.config")
    result = runner.invoke(cli, [
        "configure",
        "--provider", "api",
        "--model", "gpt2"
    ])
    
    assert result.exit_code == 0
    assert "Set model to: gpt2" in result.output
    mock_config.set.assert_called_with("model_name", "gpt2") 
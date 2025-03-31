"""
Tests for the LLM utilities module
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from auto_commit_bot.llm_utils import LLMProvider, DEFAULT_PROMPT_TEMPLATE

@pytest.fixture
def mock_config(mocker):
    """Mock configuration"""
    mock = mocker.patch("auto_commit_bot.llm_utils.config")
    mock.get.side_effect = lambda key, default=None: {
        "provider_type": "api",
        "model_name": "gpt2",
        "huggingface_api_key": "test-key"
    }.get(key, default)
    return mock

@pytest.fixture
def mock_requests(mocker):
    """Mock requests for Hugging Face API"""
    mock = mocker.patch("auto_commit_bot.llm_utils.requests")
    mock.post.return_value.json.return_value = [
        {"generated_text": "feat(test): add new feature"}
    ]
    return mock

@pytest.fixture
def mock_transformers(mocker):
    """Mock transformers components"""
    mock_tokenizer = MagicMock()
    mock_tokenizer.eos_token_id = 50256
    mocker.patch("auto_commit_bot.llm_utils.AutoTokenizer.from_pretrained",
                return_value=mock_tokenizer)
    
    mock_model = MagicMock()
    mocker.patch("auto_commit_bot.llm_utils.AutoModelForCausalLM.from_pretrained",
                return_value=mock_model)
    
    mock_pipeline = mocker.patch("auto_commit_bot.llm_utils.pipeline")
    mock_pipeline.return_value.return_value = [
        {"generated_text": "feat(test): add new feature"}
    ]
    return mock_pipeline

def test_llm_provider_init_api(mock_config):
    """Test LLMProvider initialization with API"""
    provider = LLMProvider()
    assert provider.provider_type == "api"
    assert "gpt2" in provider.api_url

def test_llm_provider_init_local(mock_config, mock_transformers):
    """Test LLMProvider initialization with local model"""
    mock_config.get.side_effect = lambda key, default=None: {
        "provider_type": "local",
        "model_name": "gpt2"
    }.get(key, default)
    
    provider = LLMProvider()
    assert provider.provider_type == "local"
    mock_transformers.assert_called_once()

def test_generate_commit_message_api(mock_config, mock_requests):
    """Test commit message generation with API"""
    provider = LLMProvider()
    message = provider.generate_commit_message("test diff")
    
    assert message == "feat(test): add new feature"
    mock_requests.post.assert_called_once_with(
        provider.api_url,
        headers=provider.headers,
        json={"inputs": provider._get_prompt_template().format(diff="test diff"),
              "parameters": {"max_length": 128}}
    )

def test_generate_commit_message_local(mock_config, mock_transformers):
    """Test commit message generation with local model"""
    mock_config.get.side_effect = lambda key, default=None: {
        "provider_type": "local",
        "model_name": "gpt2"
    }.get(key, default)
    
    provider = LLMProvider()
    message = provider.generate_commit_message("test diff")
    
    assert message == "feat(test): add new feature"
    assert mock_transformers.return_value.call_count == 1

def test_generate_commit_message_error(mock_config, mock_requests):
    """Test commit message generation with error"""
    mock_requests.post.side_effect = Exception("API Error")
    
    provider = LLMProvider()
    message = provider.generate_commit_message("test diff")
    
    assert message is None

def test_get_prompt_template_default(mock_config):
    """Test getting default prompt template"""
    provider = LLMProvider()
    template = provider._get_prompt_template()
    
    assert template == DEFAULT_PROMPT_TEMPLATE

def test_get_prompt_template_custom(mock_config, tmp_path):
    """Test getting custom prompt template"""
    custom_template = "Custom template {diff}"
    template_path = tmp_path / "template.txt"
    with open(template_path, "w") as f:
        f.write(custom_template)
    
    mock_config.get.side_effect = lambda key, default=None: {
        "provider_type": "api",
        "prompt_template": str(template_path)
    }.get(key, default)
    
    provider = LLMProvider()
    template = provider._get_prompt_template()
    
    assert template == custom_template 
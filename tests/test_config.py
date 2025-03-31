"""
Tests for the configuration module
"""
import os
from pathlib import Path
import pytest
import yaml
from auto_commit_bot.config import Config, DEFAULT_CONFIG

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file"""
    config_path = tmp_path / ".acbconfig"
    return config_path

@pytest.fixture
def config_with_file(temp_config_file):
    """Create a Config instance with a temporary config file"""
    config = Config()
    config.config_path = temp_config_file
    return config

def test_default_config():
    """Test default configuration values"""
    config = Config()
    assert config.get("provider_type") == "api"
    assert config.get("model_name") == "gpt2"
    assert config.get("commit_format") == "conventional"

def test_load_config_file(config_with_file, temp_config_file):
    """Test loading configuration from file"""
    test_config = {
        "provider_type": "local",
        "model_name": "test-model"
    }
    
    with open(temp_config_file, "w") as f:
        yaml.dump(test_config, f)
    
    config_with_file._load_config()
    
    assert config_with_file.get("provider_type") == "local"
    assert config_with_file.get("model_name") == "test-model"
    # Default values should still be present
    assert config_with_file.get("commit_format") == "conventional"

def test_load_env_vars(monkeypatch):
    """Test loading configuration from environment variables"""
    test_api_key = "test-api-key"
    monkeypatch.setenv("HUGGINGFACE_API_KEY", test_api_key)
    
    config = Config()
    assert config.get("huggingface_api_key") == test_api_key

def test_save_config(config_with_file, temp_config_file):
    """Test saving configuration to file"""
    config_with_file.set("provider_type", "local")
    config_with_file.set("model_name", "test-model")
    config_with_file.save()
    
    # Read the saved file
    with open(temp_config_file) as f:
        saved_config = yaml.safe_load(f)
    
    assert saved_config["provider_type"] == "local"
    assert saved_config["model_name"] == "test-model"

def test_get_all_config():
    """Test getting all configuration values"""
    config = Config()
    all_config = config.get_all()
    
    assert isinstance(all_config, dict)
    assert id(all_config) != id(config.config)  # Should be a copy
    assert all_config["provider_type"] == config.get("provider_type") 
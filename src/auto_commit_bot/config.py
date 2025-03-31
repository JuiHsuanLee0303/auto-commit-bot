"""
Configuration settings for Auto Commit Bot
"""
import os
from pathlib import Path
from typing import Dict, Optional
import yaml
import click
from dotenv import load_dotenv

# Load environment variables from .env file
click.echo("🔄 Loading environment variables...")
load_dotenv()
click.echo("✓ Environment variables loaded")

DEFAULT_CONFIG = {
    "provider_type": "api",  # 'api' or 'local'
    "model_name": "deepseek-ai/DeepSeek-V3-0324-fast",  # Default chat model
    "huggingface_api_key": None,
    "commit_format": "conventional",  # conventional, angular, or gitmoji
    "prompt_template": None,  # Path to custom prompt template
}

class Config:
    def __init__(self):
        click.echo("\n⚙️ Initializing configuration...")
        self.config_path = Path(".acbconfig")
        self.config = DEFAULT_CONFIG.copy()
        click.echo("✓ Default configuration loaded")
        self._load_config()
        self._load_env_vars()

    def _load_config(self):
        """Load configuration from .acbconfig file if it exists"""
        if self.config_path.exists():
            click.echo(f"📂 Loading configuration from {self.config_path}...")
            try:
                with open(self.config_path) as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self.config.update(user_config)
                        click.echo("✓ Configuration file loaded successfully")
                    else:
                        click.echo("ℹ️ Configuration file is empty")
            except Exception as e:
                click.echo(f"❌ Error loading configuration file: {str(e)}", err=True)
        else:
            click.echo("ℹ️ No configuration file found, using defaults")

    def _load_env_vars(self):
        """Load configuration from environment variables"""
        click.echo("\n🔐 Loading API keys from environment...")
        
        # Hugging Face
        if os.getenv("HUGGINGFACE_API_KEY"):
            self.config["huggingface_api_key"] = os.getenv("HUGGINGFACE_API_KEY")
            click.echo("✓ Hugging Face API key loaded")
        else:
            click.echo("ℹ️ No Hugging Face API key found in environment")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value"""
        value = self.config.get(key, default)
        if key != "huggingface_api_key":  # Don't print API key
            click.echo(f"📖 Config get: {key} = {value}")
        return value

    def get_all(self) -> Dict:
        """Get all configuration values"""
        click.echo("📖 Getting all configuration values")
        # Create a copy without sensitive data
        safe_config = self.config.copy()
        if "huggingface_api_key" in safe_config:
            safe_config["huggingface_api_key"] = "***" if safe_config["huggingface_api_key"] else None
        return safe_config

    def set(self, key: str, value: str):
        """Set a configuration value"""
        self.config[key] = value
        if key != "huggingface_api_key":  # Don't print API key
            click.echo(f"✏️ Config set: {key} = {value}")
        else:
            click.echo(f"✏️ Config set: {key} = ***")

    def save(self):
        """Save configuration to file"""
        click.echo(f"\n💾 Saving configuration to {self.config_path}...")
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f)
            click.echo("✓ Configuration saved successfully")
        except Exception as e:
            click.echo(f"❌ Error saving configuration: {str(e)}", err=True)

# Global config instance
config = Config() 
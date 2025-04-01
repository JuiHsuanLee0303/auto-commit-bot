# Auto Commit Bot 🤖

A Python package that automates Git commit message generation using Large Language Models (LLM). It analyzes your git diff and generates structured, meaningful commit messages following the Conventional Commits format.

## Features ✨

- 🔄 Automatic commit message generation
- 🎯 Support for multiple LLM providers (OpenAI, Hugging Face, Local models)
- 📝 Conventional Commits format
- 🔍 Dry-run mode for message preview
- ⚙️ Configurable settings

## Installation 📦

### 1. Install PyTorch

First, install PyTorch according to your CUDA version:

1. Visit https://pytorch.org
2. Select your preferences:
   - PyTorch Build: Stable
   - Your OS
   - Package Manager: Pip
   - CUDA Version: (Check your CUDA version or select CPU only)
3. Run the provided command, for example:

```bash
# For Windows with CUDA 11.8
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CPU only
pip3 install torch torchvision torchaudio
```

### 2. Install Auto Commit Bot

```bash
# Clone the repository
git clone https://github.com/JuiHsuanLee/auto-commit-bot.git
cd auto-commit-bot

# Install dependencies and package
pip install -e .
```

### 3. Verify Installation

```bash
# Run using Python module
python -m auto_commit_bot --help

# Or use the command directly (if Python Scripts directory is in PATH)
auto-commit --help
```

## Quick Start 🚀

1. Configure your preferred LLM provider:

```bash
# For OpenAI
auto-commit configure --provider openai --api-key your-api-key

# For Hugging Face
auto-commit configure --provider huggingface --api-key your-api-key --model your-model-name

# For local models
auto-commit configure --provider local --model path/to/your/model
```

2. Stage your changes:

```bash
git add .  # or stage specific files
```

3. Generate commit message and commit:

```bash
auto-commit commit
```

## Usage 📖

### Basic Commands

```bash
# Generate commit message and commit staged changes
auto-commit commit

# Preview commit message without committing (dry-run)
auto-commit commit --dry-run

# Stage all changes and commit
auto-commit commit --stage-all

# Override LLM provider for a single commit
auto-commit commit --provider openai
```

### Configuration

The tool can be configured using the `configure` command or by creating a `.acbconfig` file:

```bash
# Set LLM provider
auto-commit configure --provider openai

# Set API key
auto-commit configure --api-key your-api-key

# Set model
auto-commit configure --model gpt-3.5-turbo
```

Example `.acbconfig`:

```yaml
llm_provider: openai
openai_api_key: your-api-key
openai_model: gpt-3.5-turbo
commit_format: conventional
```

## Custom Prompt Templates 📝

You can customize the prompt template by creating a file and setting its path in the configuration:

```bash
auto-commit configure --prompt-template path/to/template.txt
```

## Development 🛠

1. Clone the repository
2. Install dependencies:

```bash
poetry install
```

3. Run tests:

```bash
poetry run pytest
```

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

MIT License

## Examples 📝

### 1. Basic Usage

```python
from auto_commit_bot.llm_utils import LLMProvider
from auto_commit_bot.git_utils import get_git_diff

# Initialize the LLM provider
llm = LLMProvider()

# Get git diff
diff = get_git_diff(staged=True)

# Generate commit message
message = llm.generate_commit_message(diff)
print(f"Generated commit message: {message}")
```

### 2. Custom Configuration

```python
from auto_commit_bot.config import Config

# Initialize configuration
config = Config()

# Set up Hugging Face API
config.set("provider_type", "api")
config.set("model_name", "gpt2")
config.set("huggingface_api_key", "your-api-key")
config.save()

# Use local model
config.set("provider_type", "local")
config.set("model_name", "path/to/your/model")
config.save()
```

### 3. Custom Prompt Template

```python
# Create a custom prompt template
template = """
Analyze the following git diff and generate a commit message.
Focus on the main changes and keep it concise.

Git diff:
{diff}

Generate a commit message following this format:
type(scope): description
"""

# Save the template
with open("custom_template.txt", "w") as f:
    f.write(template)

# Configure to use the custom template
config.set("prompt_template", "custom_template.txt")
config.save()
```

### 4. Command Line Usage

```bash
# Stage and commit with default settings
git add .
auto-commit commit

# Preview commit message
auto-commit commit --dry-run

# Use specific provider
auto-commit commit --provider api

# Configure settings
auto-commit configure --provider api --model gpt2 --api-key your-api-key
```

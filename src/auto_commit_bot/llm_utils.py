"""
LLM integration utilities for Auto Commit Bot using Hugging Face models
"""
import os
import re
from typing import Optional
import requests
import click
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from .config import config

# Valid commit types for filtering
VALID_COMMIT_TYPES = [
    "feat", "fix", "docs", "style", "refactor",
    "perf", "test", "chore", "revert", "build", "ci"
]

DEFAULT_PROMPT_TEMPLATE = """
You are a commit message generator that follows the Conventional Commits specification and best practices for Git commit messages.

Your task is to analyze the git diff and generate a commit message that follows the Conventional Commits format.

Rules:
1. The message MUST start with a type (feat, fix, docs, etc.)
2. The type MAY have a scope in parentheses
3. The type is followed by a colon and space
4. The subject line describes the change concisely

Valid Types:
- feat: New features or modifications
- fix: Bug fixes
- docs: Documentation changes
- style: Code style/format changes (no code change)
- refactor: Code refactoring (no feature/fix changes)
- perf: Performance improvements
- test: Adding/modifying tests
- chore: Build process or tool changes
- revert: Revert previous commits

Example Good Messages:
- feat(auth): add OAuth2 authentication
- fix(api): handle null response from server
- docs(readme): update installation instructions
- style(lint): format code according to new rules
- refactor(core): simplify error handling logic

Now, analyze this git diff and generate a commit message in the {format_type} format:

Git diff:
{diff}

IMPORTANT: Return ONLY the commit message between <commit> and </commit> tags.
Example response format:
<commit>
feat(api): implement user authentication
</commit>
"""

class LLMProvider:
    def __init__(self):
        click.echo("\n🤖 Initializing LLM Provider...")
        self.provider_type = config.get("provider_type", "api")
        click.echo(f"✓ Using provider type: {self.provider_type}")
        self._setup_provider()

    def _setup_provider(self):
        """Setup the selected LLM provider"""
        if self.provider_type == "api":
            click.echo("🌐 Setting up API provider...")
            model_name = config.get("model_name", "deepseek-ai/DeepSeek-V3-0324-fast")
            self.api_url = "https://router.huggingface.co/nebius/v1/chat/completions"
            self.headers = {"Authorization": f"Bearer {config.get('huggingface_api_key')}"}
            self.model = model_name
            click.echo(f"✓ API configured for model: {model_name}")
        else:
            click.echo("💻 Setting up local provider...")
            model_name = config.get("model_name", "gpt2")
            click.echo("📥 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            click.echo("📥 Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            click.echo("🔧 Setting up pipeline...")
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=128
            )
            click.echo(f"✓ Local model setup complete: {model_name}")

    def _clean_commit_message(self, message: str, format_type: str = "short") -> str:
        """
        Clean and validate the commit message output.
        
        Args:
            message (str): Raw message from LLM
            format_type (str): Format type ('short' or 'detailed')
            
        Returns:
            str: Cleaned commit message
        """
        # Try to extract message between tags first
        match = re.search(r"<commit>(.*?)</commit>", message, re.DOTALL)
        if match:
            message = match.group(1).strip()

        # Split into lines and process
        lines = message.splitlines()
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            return ""
            
        # Validate first line follows conventional commit format
        first_line = lines[0]
        if not any(first_line.startswith(t) for t in VALID_COMMIT_TYPES):
            # Try to find a valid commit message in other lines
            for line in lines[1:]:
                if any(line.startswith(t) for t in VALID_COMMIT_TYPES):
                    first_line = line
                    break
        
        if format_type == "short":
            return first_line
            
        # For detailed format, include body and footer if present
        result = [first_line]
        if len(lines) > 1:
            current_section = []
            for line in lines[1:]:
                # Skip lines that look like new commit messages
                if any(line.startswith(t) for t in VALID_COMMIT_TYPES):
                    continue
                current_section.append(line)
            
            if current_section:
                result.extend([""] + current_section)
        
        return "\n".join(result)

    def _generate_prompt(self, diff: str, format_type: str = "short") -> str:
        """Generate prompt with appropriate format type and template."""
        detailed_format = """
Header: <type>(<scope>): <subject>
[blank line]
Body: Detailed explanation of changes
[blank line]
Footer: Issue references, breaking changes
"""
        short_format = "<type>(<scope>): <subject>"
        
        template = DEFAULT_PROMPT_TEMPLATE.format(
            diff=diff,
            format_type=format_type,
            detailed_format=detailed_format if format_type == "detailed" else short_format
        )
        return template

    def generate_commit_message(self, diff: str, format_type: str = "short") -> str:
        """
        Generate commit message based on the git diff.
        
        Args:
            diff (str): The git diff content
            format_type (str): The commit message format type ('short' or 'detailed')
        
        Returns:
            str: Generated commit message
        """
        click.echo("\n📝 Generating commit message...")
        click.echo(f"✓ Using {format_type} format")
        
        if len(diff.splitlines()) > 100:
            diff = "\n".join(diff.splitlines()[:100])
            click.echo("⚠️ Warning: Large diff detected, using simplified version")
        
        prompt = self._generate_prompt(diff, format_type)
        click.echo("✓ Prompt template prepared")
        
        if self.provider_type == "api":
            return self._generate_api(prompt, format_type)
        else:
            return self._generate_local(prompt)

    def _generate_api(self, prompt: str, format_type: str = "short") -> str:
        """Generate commit message using Hugging Face API"""
        click.echo("🌐 Sending request to Hugging Face API...")
        try:
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates Git commit messages in the Conventional Commits format. Only output the commit message itself, without any additional text or explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "model": self.model
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 422:
                click.echo("❌ Error: Input too large for the model", err=True)
                click.echo("\n💡 Suggestions to fix this:")
                click.echo("1. Use 'git add' to stage only specific files")
                click.echo("2. Make smaller, focused commits")
                click.echo("3. Try using 'git diff --unified=0' for minimal context")
                return ""
            elif response.status_code != 200:
                click.echo(f"❌ API request failed with status {response.status_code}", err=True)
                click.echo(f"Error details: {response.text}", err=True)
                return ""
                
            click.echo("✓ Received API response")
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                raw_message = result["choices"][0]["message"]["content"].strip()
                cleaned_message = self._clean_commit_message(raw_message, format_type)
                if cleaned_message:
                    return cleaned_message
                else:
                    click.echo("❌ Could not extract valid commit message from response", err=True)
                    return ""
            else:
                click.echo("❌ Unexpected API response format", err=True)
                return ""
                
        except Exception as e:
            click.echo(f"❌ API request error: {str(e)}", err=True)
            return ""

    def _generate_local(self, prompt: str) -> str:
        """Generate commit message using local model"""
        click.echo("💭 Generating with local model...")
        result = self.pipeline(
            prompt,
            max_length=2048,
            num_return_sequences=1,
            pad_token_id=self.tokenizer.eos_token_id,
            truncation=True,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            top_k=50
        )
        click.echo("✓ Local generation complete")
        
        # Extract the generated text
        generated_text = result[0]["generated_text"].strip()
        
        # Try to extract message between commit tags
        match = re.search(r"<commit>\s*(.*?)\s*</commit>", generated_text, re.DOTALL)
        if match:
            message = match.group(1).strip()
            if message and any(message.startswith(t) for t in VALID_COMMIT_TYPES):
                click.echo("✓ Successfully extracted commit message from tags")
                return message
            
        # If no valid message found in tags, try to find a conventional commit format message
        lines = generated_text.splitlines()
        for line in lines:
            line = line.strip()
            if line and any(line.startswith(t) for t in VALID_COMMIT_TYPES):
                click.echo("✓ Found valid commit message format")
                return line
                
        click.echo("❌ Could not find valid commit message in generated text", err=True)
        click.echo("Generated text for debugging:")
        click.echo(generated_text)
        return "" 
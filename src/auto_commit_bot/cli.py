"""
Command-line interface for Auto Commit Bot
"""
import sys
import click
from . import __version__
from .config import config
from .git_utils import (
    is_git_repo,
    has_staged_changes,
    get_git_diff,
    stage_all_changes,
    commit_changes,
    get_changed_files
)
from .llm_utils import LLMProvider

@click.group()
@click.version_option(version=__version__)
def cli():
    """Auto Commit Bot - Generate commit messages using LLM"""
    pass

@cli.command()
@click.option("--dry-run", is_flag=True, help="Preview the commit message without committing")
@click.option("--stage-all", is_flag=True, help="Stage all changes before committing")
@click.option("--provider", type=click.Choice(["api", "local"]),
              help="Override the provider type")
def commit(dry_run: bool, stage_all: bool, provider: str):
    """Generate a commit message and commit changes"""
    # Check if we're in a git repository
    if not is_git_repo():
        click.echo("Error: Not a git repository", err=True)
        sys.exit(1)

    # Stage changes if requested
    if stage_all:
        if not stage_all_changes():
            click.echo("Error: Failed to stage changes", err=True)
            sys.exit(1)

    # Check for staged changes
    if not has_staged_changes():
        click.echo("Error: No staged changes to commit", err=True)
        sys.exit(1)

    # Get the diff
    diff = get_git_diff(staged=True)
    if not diff:
        click.echo("Error: Failed to get git diff", err=True)
        sys.exit(1)

    # Override provider if specified
    if provider:
        config.set("provider_type", provider)

    # Initialize LLM provider
    llm = LLMProvider()

    # Generate commit message
    click.echo("✅ Analyzing changes...")
    changed_files = get_changed_files(staged=True)
    if not changed_files:
        click.echo("Error: No files to commit", err=True)
        sys.exit(1)

    for file in changed_files:
        click.echo(f"  - {file}")

    message = llm.generate_commit_message(diff)
    if not message:
        click.echo("Error: Failed to generate commit message", err=True)
        sys.exit(1)

    click.echo("\n✅ Generated commit message:")
    click.echo(f"  {message}")

    # In dry-run mode, just preview the message
    if dry_run:
        sys.exit(0)

    # Commit the changes
    if commit_changes(message):
        click.echo("\n✅ Changes committed successfully!")
    else:
        click.echo("Error: Failed to commit changes", err=True)
        sys.exit(1)

@cli.command()
@click.option("--provider", type=click.Choice(["api", "local"]), help="Provider type")
@click.option("--api-key", type=str, help="API key for Hugging Face")
@click.option("--model", type=str, help="Model name")
def configure(provider: str, api_key: str, model: str):
    """Configure Auto Commit Bot settings"""
    if provider:
        config.set("provider_type", provider)
        click.echo(f"Set provider type to: {provider}")

    if api_key:
        config.set("huggingface_api_key", api_key)
        click.echo("Updated Hugging Face API key")

    if model:
        config.set("model_name", model)
        click.echo(f"Set model to: {model}")

    config.save()
    click.echo("Configuration saved successfully!")

def main():
    """Main entry point for the CLI"""
    cli() 
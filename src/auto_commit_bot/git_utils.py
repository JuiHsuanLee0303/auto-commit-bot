"""
Git operations utilities for Auto Commit Bot
"""
import subprocess
from typing import List, Tuple, Optional
import click  # Add click for colored output

def run_git_command(command: List[str]) -> Tuple[str, str, int]:
    """
    Run a git command and return its output
    
    Args:
        command: List of command parts (e.g., ["git", "diff"])
    
    Returns:
        Tuple of (stdout, stderr, return_code)
    """
    try:
        click.echo(f"🔄 Executing git command: {' '.join(command)}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',  # Explicitly set UTF-8 encoding
            errors='replace'   # Replace invalid characters instead of failing
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            click.echo("✓ Command executed successfully")
        else:
            click.echo(f"❌ Command failed with error: {stderr}", err=True)
        return stdout.strip(), stderr.strip(), process.returncode
    except Exception as e:
        click.echo(f"❌ Exception while running git command: {str(e)}", err=True)
        return "", str(e), 1

def simplify_diff(diff: str, max_length: int = 3000) -> str:
    """
    Simplify git diff by removing metadata and limiting context
    
    Args:
        diff: The original git diff output
        max_length: Maximum length of the simplified diff
    
    Returns:
        Simplified diff content
    """
    simplified_lines = []
    for line in diff.splitlines():
        # Skip metadata lines
        if line.startswith('diff --git') or \
           line.startswith('index ') or \
           line.startswith('--- ') or \
           line.startswith('+++ '):
            continue
            
        # Keep changed lines and minimal context
        if line.startswith('+') or line.startswith('-') or line.startswith('@@ '):
            simplified_lines.append(line)
    
    # Join lines and limit length
    simplified_diff = '\n'.join(simplified_lines)
    if len(simplified_diff) > max_length:
        click.echo(f"⚠️ Diff too large ({len(simplified_diff)} chars), truncating to {max_length} chars")
        return simplified_diff[:max_length]
    
    return simplified_diff

def get_git_diff(staged: bool = True, simplified: bool = True, max_length: int = 3000) -> Optional[str]:
    """
    Get the git diff output
    
    Args:
        staged: Whether to get diff for staged changes only
        simplified: Whether to return simplified diff
        max_length: Maximum length of the diff if simplified
    
    Returns:
        The diff output or None if error
    """
    click.echo(f"\n📝 Getting {'staged' if staged else 'unstaged'} changes...")
    
    # Use --unified=0 to minimize context lines
    command = ["git", "diff", "--unified=0"]
    if staged:
        command.append("--staged")
    
    stdout, stderr, code = run_git_command(command)
    if code != 0:
        click.echo("❌ Failed to get git diff", err=True)
        return None
    
    if not stdout:
        click.echo("ℹ️ No changes found")
        return None
    
    lines = stdout.splitlines()
    click.echo(f"✓ Found {len(lines)} lines of changes")
    
    if simplified:
        click.echo("📝 Simplifying diff...")
        stdout = simplify_diff(stdout, max_length)
        click.echo(f"✓ Simplified diff: {len(stdout)} chars")
    
    return stdout

def stage_all_changes() -> bool:
    """
    Stage all changes in the repository
    
    Returns:
        True if successful, False otherwise
    """
    click.echo("\n📦 Staging all changes...")
    _, _, code = run_git_command(["git", "add", "."])
    if code == 0:
        click.echo("✓ All changes staged successfully")
    else:
        click.echo("❌ Failed to stage changes", err=True)
    return code == 0

def commit_changes(message: str) -> bool:
    """
    Commit staged changes with the given message
    
    Args:
        message: The commit message
    
    Returns:
        True if successful, False otherwise
    """
    click.echo("\n💾 Committing changes...")
    _, _, code = run_git_command(["git", "commit", "-m", message])
    if code == 0:
        click.echo("✓ Changes committed successfully")
    else:
        click.echo("❌ Failed to commit changes", err=True)
    return code == 0

def is_git_repo() -> bool:
    """
    Check if current directory is a git repository
    
    Returns:
        True if current directory is a git repository
    """
    click.echo("\n🔍 Checking if current directory is a git repository...")
    _, _, code = run_git_command(["git", "rev-parse", "--is-inside-work-tree"])
    if code == 0:
        click.echo("✓ Valid git repository found")
    else:
        click.echo("❌ Not a git repository", err=True)
    return code == 0

def has_staged_changes() -> bool:
    """
    Check if there are staged changes
    
    Returns:
        True if there are staged changes
    """
    click.echo("\n🔍 Checking for staged changes...")
    stdout, _, code = run_git_command(["git", "diff", "--staged", "--name-only"])
    has_changes = code == 0 and bool(stdout.strip())
    if has_changes:
        click.echo("✓ Found staged changes")
    else:
        click.echo("❌ No staged changes found", err=True)
    return has_changes

def get_changed_files(staged: bool = True) -> List[str]:
    """
    Get list of changed files
    
    Args:
        staged: Whether to get only staged files
    
    Returns:
        List of changed file paths
    """
    click.echo(f"\n📄 Getting list of {'staged' if staged else 'changed'} files...")
    command = ["git", "diff", "--name-only"]
    if staged:
        command.append("--staged")
    
    stdout, _, code = run_git_command(command)
    if code != 0:
        click.echo("❌ Failed to get changed files", err=True)
        return []
    
    files = [f for f in stdout.split("\n") if f]
    if files:
        click.echo(f"✓ Found {len(files)} changed files:")
        for file in files:
            click.echo(f"  - {file}")
    else:
        click.echo("ℹ️ No changed files found")
    return files 
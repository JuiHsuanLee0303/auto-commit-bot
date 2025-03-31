from auto_commit_bot.llm_utils import LLMProvider
from auto_commit_bot.config import Config
from auto_commit_bot.git_utils import get_git_diff, is_git_repo
import os
import click
import tempfile

def setup_config():
    """Setup basic configuration"""
    print("\n=== Configuration Setup Start ===")
    config = Config()
    
    # Setup Hugging Face API
    print("Checking Hugging Face API key...")
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError("Please set the HUGGINGFACE_API_KEY environment variable")
    print("✓ API key successfully obtained")
    
    print("\nUpdating configuration...")
    config.set("provider_type", "api")
    config.set("model_name", "deepseek-ai/DeepSeek-V3-0324-fast")
    config.set("huggingface_api_key", api_key)
    
    # Display current configuration
    current_config = config.get_all()
    print("\nCurrent Configuration:")
    print(f"- Provider Type: {current_config.get('provider_type')}")
    print(f"- Model Name: {current_config.get('model_name')}")
    print(f"- API Key: {'Set' if current_config.get('huggingface_api_key') else 'Not Set'}")
    
    config.save()
    print("✓ Configuration saved to .acbconfig file")
    print("=== Configuration Setup Complete ===\n")
    return config

def execute_git_commit(message: str, format_type: str) -> bool:
    """
    Execute git commit with the given message.
    
    Args:
        message (str): The commit message
        format_type (str): The format type ('short' or 'detailed')
        
    Returns:
        bool: True if commit was successful, False otherwise
    """
    try:
        if format_type == "short" or "\n" not in message:
            # For single-line messages, use -m
            result = os.system(f'git commit -m "{message}"')
        else:
            # For multi-line messages, write to temp file and use -F
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
                f.write(message)
                temp_file = f.name
            
            result = os.system(f'git commit -F "{temp_file}"')
            os.unlink(temp_file)  # Clean up temp file
            
        return result == 0
    except Exception as e:
        print(f"❌ Error during commit: {str(e)}")
        return False

def generate_commit_message(format_type: str = "short"):
    """
    Generate commit message
    
    Args:
        format_type (str): Type of commit message format ('short' or 'detailed')
    """
    print("\n=== Commit Message Generation Start ===")
    print(f"Using {format_type} commit message format")
    
    # Check if in Git repository
    if not is_git_repo():
        print("❌ Error: Current directory is not a Git repository")
        print("Please run 'git init' to initialize repository")
        return None
    print("✓ Confirmed current directory is a Git repository")
    
    # Initialize LLM provider
    print("\nInitializing LLM provider...")
    llm = LLMProvider()
    print("✓ LLM provider initialization complete")
    
    # Get git diff for staged files
    print("\nGetting Git differences...")
    diff = get_git_diff(staged=True)
    if not diff:
        print("❌ No staged changes found")
        print("Tip: Use 'git add <file>' to stage changes")
        print("     Use 'git status' to check current status")
        return None
    print(f"✓ Successfully retrieved Git diff ({len(diff.splitlines())} lines of changes)")
    
    # Generate commit message
    print("\nGenerating commit message...")
    message = llm.generate_commit_message(diff, format_type=format_type)
    if message:
        print("✓ Successfully generated commit message")
        print(f"\nGenerated Commit Message:\n{'-' * 50}\n{message}\n{'-' * 50}")
    else:
        print("❌ Failed to generate commit message")
    
    print("=== Commit Message Generation Complete ===\n")
    return message

@click.command()
@click.option('--format-type', type=click.Choice(['short', 'detailed']), default='short',
              help='Commit message format type (short or detailed)')
def main(format_type):
    """Auto Commit Bot Example Program"""
    try:
        print("=== Auto Commit Bot Example Program ===")
        print("This program will help you generate Git commit messages using AI")
        
        # Setup configuration
        config = setup_config()
        
        # Generate commit message
        message = generate_commit_message(format_type)
        
        # If message generation successful, ask for confirmation
        if message:
            print("\n=== Commit Confirmation ===")
            choice = input("Do you want to use this commit message? (y/n): ")
            if choice.lower() == 'y':
                print("\nExecuting git commit...")
                if execute_git_commit(message, format_type):
                    print("✓ Commit successfully completed!")
                else:
                    print("❌ Commit failed")
            else:
                print("Commit cancelled")
            print("=== Operation Complete ===")
    
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("For help, please check the documentation or submit an issue")
    
    finally:
        print("\nThank you for using Auto Commit Bot!")

if __name__ == "__main__":
    main()
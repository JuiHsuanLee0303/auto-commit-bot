"""
Example of using Auto Commit Bot with a local LLM (meta-llama/Llama-3.2-1B)
"""
from auto_commit_bot.llm_utils import LLMProvider
from auto_commit_bot.config import Config
from auto_commit_bot.git_utils import get_git_diff, is_git_repo
import os
import click
import tempfile
import torch

def check_gpu_availability():
    """Check if CUDA GPU is available"""
    if torch.cuda.is_available():
        device = torch.cuda.get_device_name(0)
        memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # Convert to GB
        print(f"✓ GPU available: {device}")
        print(f"✓ GPU memory: {memory:.2f} GB")
        return True
    else:
        print("⚠️ No GPU detected, will use CPU (this might be slow)")
        return False

def setup_config():
    """Setup configuration for local LLM"""
    print("\n=== Configuration Setup Start ===")
    
    # Create new configuration instance
    config = Config()
    
    print("\nChecking system requirements...")
    has_gpu = check_gpu_availability()
    
    print("\nUpdating configuration...")
    # Set all required configurations explicitly
    config_dict = {
        "provider_type": "local",
        "model_name": "meta-llama/Llama-3.2-1B",
        "device": "cuda" if has_gpu else "cpu",
        "device_map": "auto" if has_gpu else None,
        "load_in_8bit": True,
        "torch_dtype": "float16" if has_gpu else "float32",
        # Generation parameters
        "max_length": 2048,  # Maximum total sequence length
        "max_new_tokens": 100,  # Maximum number of tokens to generate
        "temperature": 0.8,
        "do_sample": True,
        "top_p": 0.90,
        "top_k": 55,
        "num_return_sequences": 1,
        "pad_token_id": 0,
        "eos_token_id": 2,
        "truncation": True,  # Enable truncation
    }
    
    # Apply all configurations
    for key, value in config_dict.items():
        if value is not None:  # Only set non-None values
            config.set(key, value)
            print(f"✓ Set {key} = {value}")
    
    # Display current configuration
    current_config = config.get_all()
    print("\nCurrent Configuration:")
    for key, value in current_config.items():
        print(f"- {key}: {value}")
    
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
    Generate commit message using local LLM
    
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
    
    # Initialize LLM provider with explicit configuration
    print("\nInitializing Local LLM provider...")
    print("This might take a while when loading the model for the first time")
    
    # Create a new configuration specifically for this LLM instance
    config = Config()
    
    # Set all required configurations
    config_dict = {
        "provider_type": "local",
        "model_name": "meta-llama/Llama-3.2-1B",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "device_map": "auto" if torch.cuda.is_available() else None,
        "load_in_8bit": True,
        "torch_dtype": "float16" if torch.cuda.is_available() else "float32",
        # Generation parameters
        "max_length": 2048,
        "max_new_tokens": 100,
        "temperature": 0.7,
        "do_sample": True,
        "top_p": 0.95,
        "top_k": 50,
        "num_return_sequences": 1,
        "pad_token_id": 0,
        "eos_token_id": 2,
        "truncation": True,
    }
    
    # Apply all configurations
    for key, value in config_dict.items():
        if value is not None:
            config.set(key, value)
    
    llm = LLMProvider()
    print("✓ Local LLM provider initialization complete")
    
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
    print("⚠️ Local generation might take longer than API calls")
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
@click.option('--max-new-tokens', type=int, default=100,
              help='Maximum number of tokens to generate')
@click.option('--temperature', type=float, default=0.7,
              help='Temperature for text generation (0.0-1.0)')
def main(format_type, max_new_tokens, temperature):
    """Auto Commit Bot Example Program (Local LLM Version)"""
    try:
        print("=== Auto Commit Bot Local LLM Example ===")
        print("This program will help you generate Git commit messages using a local LLM")
        print("\nModel: meta-llama/Llama-3.2-1B")
        print("Note: First run might take longer to download and load the model")
        
        # Setup configuration
        config = setup_config()
        
        # Set generation parameters
        config.set("max_new_tokens", max_new_tokens)
        config.set("temperature", temperature)
        
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
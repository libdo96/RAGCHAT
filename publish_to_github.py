import subprocess
import sys
import re

def run_command(command, error_message=None):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if error_message:
            print(f"Error: {error_message}")
        print(f"Command failed: {command}")
        print(f"Error output: {e.stderr}")
        return False, e.stderr

def is_valid_repo_url(url):
    """Check if the GitHub repository URL is valid."""
    pattern = r'^https://github\.com/[\w-]+/[\w-]+\.git$'
    return bool(re.match(pattern, url))

def publish_to_github():
    """Publish the repository to GitHub."""
    # Check if git is initialized
    success, _ = run_command("git status", "Git repository is not initialized. Run init_repo.py first.")
    if not success:
        return False
    
    # Get GitHub repository URL
    repo_url = input("\nEnter your GitHub repository URL (https://github.com/username/repo-name.git): ").strip()
    
    if not is_valid_repo_url(repo_url):
        print("Invalid GitHub repository URL format. It should be like: https://github.com/username/repo-name.git")
        return False
    
    # Check if remote already exists
    success, output = run_command("git remote -v")
    if "origin" in output:
        choice = input("Remote 'origin' already exists. Do you want to overwrite it? (y/n): ").strip().lower()
        if choice == 'y':
            run_command("git remote remove origin")
        else:
            print("Aborted.")
            return False
    
    # Add remote
    print(f"Adding remote repository: {repo_url}")
    if not run_command(f"git remote add origin {repo_url}"):
        return False
    
    # Set main branch
    print("Setting main branch...")
    if not run_command("git branch -M main"):
        return False
    
    # Push to GitHub
    print("Pushing to GitHub...")
    success, output = run_command("git push -u origin main")
    if not success:
        if "Authentication failed" in output:
            print("\nAuthentication failed. Please make sure:")
            print("1. You have the correct permissions for this repository")
            print("2. You've configured your Git credentials")
            print("\nYou might need to use a personal access token instead of your password.")
            print("See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token")
        return False
    
    # Extract username and repo name from URL
    match = re.match(r'https://github\.com/([\w-]+)/([\w-]+)\.git', repo_url)
    if match:
        username, repo_name = match.groups()
        print(f"\nSuccess! Your repository is now published at: https://github.com/{username}/{repo_name}")
    else:
        print("\nSuccess! Your repository is now published.")
    
    return True

if __name__ == "__main__":
    publish_to_github()
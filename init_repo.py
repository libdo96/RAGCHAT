import os
import subprocess
import sys

def run_command(command, error_message=None):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        if error_message:
            print(f"Error: {error_message}")
        print(f"Command failed: {command}")
        print(f"Error output: {e.stderr}")
        return False

def init_repo():
    """Initialize a Git repository and prepare for GitHub."""
    # Check if git is installed
    if not run_command("git --version", "Git is not installed. Please install Git first."):
        return False
    
    # Initialize git repository if .git doesn't exist
    if not os.path.exists(".git"):
        print("Initializing Git repository...")
        if not run_command("git init"):
            return False
    else:
        print("Git repository already initialized.")
    
    # Create .gitignore file
    print("Creating .gitignore file...")
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Environment variables
.env

# Vector database files
vector_db/
*.pkl

# IDE files
.idea/
.vscode/
*.swp
*.swo

# OS specific files
.DS_Store
Thumbs.db
    """
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())
    
    # Create a README if it doesn't exist
    if not os.path.exists("README.md"):
        print("README.md not found. Please create one before publishing.")
    
    # Add all files to git
    print("Adding files to Git...")
    if not run_command("git add ."):
        return False
    
    # Initial commit
    print("Creating initial commit...")
    if not run_command('git commit -m "Initial commit: RAG-powered PDF Chat with Gemini"'):
        return False
    
    print("\nRepository initialized successfully!")
    print("\nNext steps:")
    print("1. Create a new repository on GitHub (don't initialize with README, .gitignore, or license)")
    print("2. Run the following commands to push to GitHub:")
    print("   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    return True

if __name__ == "__main__":
    init_repo()
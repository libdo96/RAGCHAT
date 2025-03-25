import os
import subprocess
import sys
import platform
import venv
from pathlib import Path

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

def create_virtual_environment():
    """Create a virtual environment."""
    print("Creating virtual environment...")
    venv_dir = "venv"
    
    if os.path.exists(venv_dir):
        print(f"Virtual environment already exists at {venv_dir}")
        return True
    
    try:
        venv.create(venv_dir, with_pip=True)
        print(f"Virtual environment created at {venv_dir}")
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False

def install_dependencies():
    """Install project dependencies."""
    print("Installing dependencies...")
    
    # Determine the activate script based on the OS
    if platform.system() == "Windows":
        activate_script = os.path.join("venv", "Scripts", "activate")
        pip_command = f"call {activate_script} && pip install -r requirements.txt"
    else:  # macOS or Linux
        activate_script = os.path.join("venv", "bin", "activate")
        pip_command = f"source {activate_script} && pip install -r requirements.txt"
    
    return run_command(pip_command, "Failed to install dependencies")

def create_env_file():
    """Create a .env file template."""
    if os.path.exists(".env"):
        print(".env file already exists")
        return True
    
    print("Creating .env file template...")
    env_content = """# Google API Key for Gemini
GOOGLE_API_KEY=your_api_key_here

# Optional: Vector database directory
VECTOR_DB_DIR=./vector_db
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print(".env file created. Please edit it to add your Google API key.")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def create_vector_db_dir():
    """Create directory for vector database."""
    vector_db_dir = "vector_db"
    if not os.path.exists(vector_db_dir):
        try:
            os.makedirs(vector_db_dir)
            print(f"Created vector database directory: {vector_db_dir}")
        except Exception as e:
            print(f"Error creating vector database directory: {e}")
            return False
    return True

def setup_project():
    """Set up the project environment."""
    print("Setting up RAG-Powered PDF Chat with Gemini...\n")
    
    # Check if all required files exist
    required_files = ["app.py", "modules/pdf_processor.py", "modules/vector_store.py", "modules/rag_engine.py", "requirements.txt"]
    missing_files = [file for file in required_files if not os.path.exists(file)]
    
    if missing_files:
        print(f"Error: The following required files are missing: {', '.join(missing_files)}")
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    create_env_file()
    
    # Create vector database directory
    create_vector_db_dir()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file to add your Google API key")
    print("2. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run the application:")
    print("   python run.py")
    
    return True

if __name__ == "__main__":
    setup_project()

#!/bin/bash

# Exit on error
set -e

# Check for project name input
if [ -z "$1" ]; then
  echo "Usage: ./newvenv.sh <project_name>"
  exit 1
fi

# Function to detect OS and set BASE_DIR
set_base_dir() {
  case "$(uname -s)" in
    Darwin)
      # macOS
      BASE_DIR="$HOME/Documents/Workspace"
      ;;
    Linux)
      # Linux
      BASE_DIR="$HOME/workspace"
      ;;
    MINGW*|CYGWIN*|MSYS*)
      # Windows (Git Bash, WSL, etc.)
      BASE_DIR="$HOME/Documents/Workspace"
      ;;
    *)
      # Default fallback
      BASE_DIR="$HOME/workspace"
      ;;
  esac
}

# Function to find Python 3
find_python() {
  if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
  elif command -v python &> /dev/null; then
    # Check if python is python 3
    if python --version 2>&1 | grep -q "Python 3"; then
      PYTHON_CMD="python"
    else
      echo "Error: Python 3 is required but not found"
      exit 1
    fi
  else
    echo "Error: Python is not installed"
    exit 1
  fi
}

# Function to find pip
find_pip() {
  if [ "$PYTHON_CMD" = "python3" ]; then
    PIP_CMD="pip3"
  else
    PIP_CMD="pip"
  fi
  
  # Verify pip exists
  if ! command -v $PIP_CMD &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
  fi
}

# Set up environment
set_base_dir
find_python
find_pip

# Set paths
PROJECT_NAME="$1"
PROJECT_PATH="$BASE_DIR/$PROJECT_NAME"

echo "Setting up project '$PROJECT_NAME' at '$PROJECT_PATH'"

# Create and move into project directory
mkdir -p "$PROJECT_PATH"
cd "$PROJECT_PATH"

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv .venv

# Activate the environment based on OS
echo "Activating virtual environment..."
if [ -f ".venv/Scripts/activate" ]; then
  # Windows
  source .venv/Scripts/activate
  VENV_PYTHON=".venv/Scripts/python.exe"
  VENV_PIP=".venv/Scripts/pip.exe"
else
  # Mac/Linux
  source .venv/bin/activate
  VENV_PYTHON=".venv/bin/python"
  VENV_PIP=".venv/bin/pip"
fi

# Update pip using the venv's python
echo "Updating pip..."
$VENV_PYTHON -m pip install --upgrade pip

# Create standard files
echo "Creating project files..."
echo "SECRET_KEY=your_secret_key_here" > .env
touch requirements.txt

# Create comprehensive .gitignore
cat <<EOL > .gitignore
.venv/
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
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
wheels/
*.egg-info/
.installed.cfg
*.egg
.DS_Store
.idea/
.vscode/
*.swp
*.swo
*~
EOL

cat <<EOL > main.py
import os
from dotenv import load_dotenv

load_dotenv()
secret = os.getenv("SECRET_KEY")

print(f"Hello from $PROJECT_NAME!")
print(f"Loaded secret key: {secret}")
EOL

# Install basic dev packages
echo "Installing python-dotenv..."
$VENV_PIP install --quiet python-dotenv

# Freeze to requirements
$VENV_PIP freeze > requirements.txt

# Open in VS Code
echo "Opening in VS Code..."
if command -v code &> /dev/null; then
  code .
  echo "✅ Project opened in VS Code"
else
  echo "⚠️  VS Code 'code' command not found. Please open VS Code manually."
  echo "   To install the 'code' command: View > Command Palette > 'Shell Command: Install 'code' command in PATH'"
fi

# Print activation instructions based on OS
echo ""
echo "✅ Project '$PROJECT_NAME' set up at '$PROJECT_PATH'"
echo ""
echo "To activate the virtual environment in the future:"
if [ -f ".venv/Scripts/activate" ]; then
  echo "   source .venv/Scripts/activate"
else
  echo "   source .venv/bin/activate"
fi
echo ""

# Keep the terminal open in the virtual environment
echo "Virtual environment is now active. You can start working on your project!"
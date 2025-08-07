#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "Usage: ./cleanup_projects.sh <project_name_or_pattern> [days_old]"
  echo "Example: ./cleanup_projects.sh '*test' 7"
  exit 1
fi

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


set_base_dir
WORKSPACE="$BASE_DIR"


PATTERN="$1"
DAYS_OLD="${2:-0}" 


cd "$WORKSPACE" || { echo "❌ Cannot access workspace at $WORKSPACE"; exit 1; }

echo "🔍 Looking for folders matching '$PATTERN' in $WORKSPACE"
[ "$DAYS_OLD" -gt 0 ] && echo "📅 Restricting to folders older than $DAYS_OLD days"


if [ "$DAYS_OLD" -gt 0 ]; then
  MATCHING=$(find . -maxdepth 1 -type d -name "$PATTERN" -mtime +"$DAYS_OLD" 2>/dev/null | grep -v "^\.$" || true)
else
  MATCHING=$(find . -maxdepth 1 -type d -name "$PATTERN" 2>/dev/null | grep -v "^\.$" || true)
fi

if [ -z "$MATCHING" ]; then
  echo "✅ No matching projects found."
  exit 0
fi

echo "⚠️  The following folders will be deleted:"
echo "$MATCHING" | sed 's/^\.\//  /'
echo ""


read -p "Are you sure you want to delete these projects? [y/N] " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "❌ Aborted."
  exit 0
fi

echo "🗑️  Deleting projects..."
if [ "$DAYS_OLD" -gt 0 ]; then
  find . -maxdepth 1 -type d -name "$PATTERN" -mtime +"$DAYS_OLD" ! -name "." -exec rm -rf {} + 2>/dev/null || true
else
  find . -maxdepth 1 -type d -name "$PATTERN" ! -name "." -exec rm -rf {} + 2>/dev/null || true
fi

echo "🧹 Deleted matching projects."
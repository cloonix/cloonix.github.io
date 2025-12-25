#!/usr/bin/env bash
#
# Quick wrapper script for publishing blog posts
# Usage: ./publish.sh <draft_file.md> [options]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUBLISH_SCRIPT="$SCRIPT_DIR/publish-blog-post.py"

# Check if Python script exists
if [[ ! -f "$PUBLISH_SCRIPT" ]]; then
    echo "❌ Error: publish-blog-post.py not found in $SCRIPT_DIR"
    exit 1
fi

# Check if at least one argument provided
if [[ $# -eq 0 ]]; then
    echo "Usage: ./publish.sh <draft_file.md> [options]"
    echo ""
    echo "Options:"
    echo "  --max-width <pixels>  Maximum image width (default: 1920)"
    echo "  --dry-run             Show what would happen without making changes"
    echo "  --verbose             Show detailed output"
    echo ""
    echo "Examples:"
    echo "  ./publish.sh ~/Documents/blog-drafts/my-post.md"
    echo "  ./publish.sh ~/Documents/blog-drafts/my-post.md --max-width 1200"
    echo "  ./publish.sh ~/Documents/blog-drafts/my-post.md --dry-run --verbose"
    exit 1
fi

# Run the Python script with all arguments
python3 "$PUBLISH_SCRIPT" "$@"

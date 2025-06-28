#!/bin/bash
# Automated RSS feed update and deployment script
#
# This script will:
# 1. Fetch the latest reading list from Notion
# 2. Generate RSS feed
# 3. If a deployment directory is specified, copy the file to that directory
#
# Usage:
# ./update_feed.sh                           # Generate RSS feed only
# ./update_feed.sh /var/www/html             # Generate and copy to web directory
# ./update_feed.sh /var/www/html 8080        # Specify server port

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
FEED_FILE="notion_reading_list.xml"
DEFAULT_PORT="8080"

# Parse arguments
DEPLOY_DIR="$1"
SERVER_PORT="${2:-$DEFAULT_PORT}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python virtual environment
if [ ! -f "$PYTHON_CMD" ]; then
    log_error "Python virtual environment not found: $PYTHON_CMD"
    log_info "Please run first: uv sync"
    exit 1
fi

# Enter project directory
cd "$SCRIPT_DIR" || exit 1

log_info "Starting RSS feed update..."

# Generate RSS feed
if [ -n "$DEPLOY_DIR" ]; then
    # If deployment directory is specified, use corresponding URL
    RSS_URL="http://localhost:$SERVER_PORT/$FEED_FILE"
    log_info "Generating RSS feed with URL: $RSS_URL"
    
    if "$PYTHON_CMD" main.py --link "$RSS_URL"; then
        log_info "RSS feed generated successfully"
        
        # Check deployment directory
        if [ ! -d "$DEPLOY_DIR" ]; then
            log_warn "Deployment directory does not exist, attempting to create: $DEPLOY_DIR"
            if ! mkdir -p "$DEPLOY_DIR"; then
                log_error "Cannot create deployment directory: $DEPLOY_DIR"
                exit 1
            fi
        fi
        
        # Copy file to deployment directory
        if cp "$FEED_FILE" "$DEPLOY_DIR/"; then
            log_info "RSS feed deployed to: $DEPLOY_DIR/$FEED_FILE"
            log_info "Accessible via URL: http://localhost:$SERVER_PORT/$FEED_FILE"
        else
            log_error "Cannot copy file to deployment directory"
            exit 1
        fi
    else
        log_error "RSS feed generation failed"
        exit 1
    fi
else
    # Generate RSS feed only, no deployment
    log_info "Generating RSS feed (local mode)"
    
    if "$PYTHON_CMD" main.py; then
        log_info "RSS feed generated successfully: $SCRIPT_DIR/$FEED_FILE"
    else
        log_error "RSS feed generation failed"
        exit 1
    fi
fi

log_info "RSS feed update completed!"

# Display statistics
if [ -f "$FEED_FILE" ]; then
    ITEM_COUNT=$(grep -c "<item>" "$FEED_FILE" 2>/dev/null || echo "unknown")
    log_info "RSS feed contains $ITEM_COUNT items"
fi

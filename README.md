# Notion RSS Feed Generator

A Python tool to fetch your reading list from a Notion database and generate a standards-compliant RSS feed.

## Features

- 📚 Fetch reading list from Notion database
- 🔄 Generate RSS feed with rich metadata
- 🏷️ Support for comments, tags, and status fields
- 📅 Proper date handling and formatting
- 🔧 Configurable via environment variables and command line
- 📝 Detailed logging and error handling (console & file)
- 🖥️ Command-line interface with multiple options

## Installation

1. **Clone the repository**:

   ```bash
   git clone <your-repo-url>
   cd make-feed
   ```

2. **Install dependencies** (requires Python 3.12+):

   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env  # if .env.example is provided
   # Edit .env with your Notion credentials
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Required
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id

# Optional
RSS_FEED_PATH=notion_reading_list.xml
RSS_FEED_TITLE=My Reading List
RSS_FEED_DESCRIPTION=My personal reading list from Notion
RSS_FEED_LINK=https://yourdomain.com/feed.xml
LOG_LEVEL=INFO
```

## Usage

### Command Line Interface

The main entry point is `main.py`, which provides a CLI:

```bash
# Generate RSS feed (default)
python main.py

# Specify custom output file
python main.py --output my_feed.xml

# Customize feed metadata
python main.py --title "My Reading List" --description "Books I want to read"

# Only display items (no RSS output)
python main.py --display-only

# Enable verbose logging
python main.py --verbose

# Specify feed link URL
python main.py --link "https://mydomain.com/feed.xml"

# Show help
python main.py --help
```

#### Command Line Options

- `--output, -o`: Output RSS file path (default: notion_reading_list.xml)
- `--title, -t`: RSS feed title (default: Notion Reading List)
- `--description, -d`: RSS feed description
- `--link, -l`: RSS feed self-referencing URL
- `--display-only`: Only display items, don't generate RSS
- `--verbose, -v`: Enable debug logging

### Getting Notion Credentials

1. **API Key**: Go to [Notion Integrations](https://www.notion.so/my-integrations) and create a new integration.
2. **Database ID**:
   - Open your Notion database
   - Copy the URL; the database ID is the 32-character string before the `?`
   - Example: `https://notion.so/workspace/21fb96ce96c080c59663fde96f49746d?v=...`
   - Database ID: `21fb96ce96c080c59663fde96f49746d`
3. **Grant Access**: Share your database with the integration you created.

## Notion Database Structure

Your Notion database should have the following properties:

| Property Name | Type      | Description               |
| ------------- | --------- | ------------------------- |
| Name          | Title     | Title of the article/item |
| URL           | URL       | Link to the article       |
| Comments      | Rich Text | Your notes/comments       |
| Tags          | Rich Text | Tags (comma-separated)    |
| Status        | Status    | Reading status            |
| Created Time  | Date      | When item was added       |

### Programmatic Usage

You can use the main functions directly in your own scripts:

```python
from make_feed.pull_notion import fetch_reading_list
from make_feed.generate_rss import generate_rss

# Fetch data
items = fetch_reading_list()

# Generate RSS
success = generate_rss(
    items=items,
    feed_path="my_feed.xml",
    feed_title="My Custom Feed"
)
```

## Local Deployment and FreshRSS Subscription Configuration

### Method 1: Using Built-in HTTP Server (Recommended)

1. **Generate RSS feed with local URL specified**:
   ```bash
   # Generate RSS feed
   python main.py --link "http://localhost:8080/notion_reading_list.xml"
   ```

2. **Start HTTP server**:
   ```bash
   # Start server in current directory
   python serve_rss.py --port 8080
   
   # Or specify different port
   python serve_rss.py --port 8081
   ```

3. **Add subscription in FreshRSS**:
   - URL: `http://localhost:8080/notion_reading_list.xml`
   - If FreshRSS is on a different machine, replace `localhost` with server IP

### Method 2: Deploy to Web Server Directory

1. **Generate and deploy to web directory**:
   ```bash
   # Use automation script (recommended)
   ./update_feed.sh /var/www/html 8080
   
   # Or manually generate and copy
   python main.py --link "http://your-domain.com/notion_reading_list.xml" --output /var/www/html/notion_reading_list.xml
   ```

2. **Add subscription in FreshRSS**:
   - URL: `http://your-domain.com/notion_reading_list.xml`

### Method 3: Configure via Environment Variables

Set in `.env` file:
```env
RSS_FEED_LINK=http://localhost:8080/notion_reading_list.xml
# Or use your domain
# RSS_FEED_LINK=http://yourdomain.com/notion_reading_list.xml
```

Then run directly:
```bash
python main.py
```

### Automated Updates

Use the `update_feed.sh` script to automate RSS feed generation and deployment:

```bash
# Generate RSS feed only
./update_feed.sh

# Generate and deploy to web directory
./update_feed.sh /var/www/html

# Specify specific port
./update_feed.sh /var/www/html 8081
```

### Cron Auto-update (Optional)

Set up a cron job to update RSS feed every hour:
```bash
# Edit crontab
crontab -e

# Add the following line (update every hour)
0 * * * * cd /path/to/make_feed && ./update_feed.sh /var/www/html >/dev/null 2>&1
```

## Output

The generated RSS feed includes:

- **Rich descriptions** with comments, tags, and status
- **Proper publication dates** from Notion timestamps
- **Valid RSS 2.0 format** compatible with all feed readers
- **HTML-formatted content** for better readability

Example RSS entry:

```xml
<item>
    <title>Mind_Sweep_Trigger_List.pdf</title>
    <link>https://gettingthingsdone.com/wp-content/uploads/2014/10/Mind_Sweep_Trigger_List.pdf</link>
    <description>
        <p><strong>Comments:</strong> Used for learn how to record and plan tasks</p>
        <p><strong>Tags:</strong> information, life</p>
        <p><strong>Status:</strong> 未开始</p>
        <p><strong>Added:</strong> 2025-06-27 11:34:00 UTC</p>
    </description>
    <pubDate>Thu, 27 Jun 2025 11:34:00 +0000</pubDate>
    <guid>https://gettingthingsdone.com/wp-content/uploads/2014/10/Mind_Sweep_Trigger_List.pdf</guid>
</item>
```

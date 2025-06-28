import logging

from notion_client import APIResponseError, Client

from make_feed.config import Config

logger = logging.getLogger(__name__)


def fetch_reading_list() -> list[dict[str, str | None]]:
    """Fetch reading list from Notion database.

    Returns:
        List of dictionaries containing item information
    """
    config = Config()
    notion = Client(auth=config.NOTION_API_KEY)
    try:
        result = notion.databases.query(database_id=config.NOTION_DATABASE_ID)
        items = []

        for row in result["results"]:
            props = row["properties"]

            # Extract title from Name field
            title = "No Title"
            if props.get("Name", {}).get("title"):
                title = props["Name"]["title"][0]["plain_text"]

            # Extract URL
            url = props.get("URL", {}).get("url")

            # Extract comments/notes
            comments = ""
            if props.get("Comments", {}).get("rich_text"):
                comments = props["Comments"]["rich_text"][0]["plain_text"]

            # Extract tags
            tags = ""
            if props.get("Tags", {}).get("rich_text"):
                tags = props["Tags"]["rich_text"][0]["plain_text"]

            # Extract status
            status = ""
            if props.get("Status", {}).get("status"):
                status = props["Status"]["status"]["name"]

            # Extract created time
            created_time = row["created_time"]

            items.append(
                {
                    "title": title,
                    "url": url,
                    "comments": comments,
                    "tags": tags,
                    "status": status,
                    "created_time": created_time,
                }
            )

    except APIResponseError:
        logger.exception("Error fetching reading list")
        return []
    else:
        logger.info("Successfully fetched %d items from reading list", len(items))
        return items


def display_reading_list(items: list[dict[str, str | None]]) -> None:
    """Display reading list items in a formatted way.

    Args:
        items: List of reading list items to display
    """
    for item in items:
        logger.info("Title: %s", item["title"])
        logger.info("URL: %s", item["url"])
        logger.info("Status: %s", item["status"])
        logger.info("Tags: %s", item["tags"])
        logger.info("Comments: %s", item["comments"])
        logger.info("Created: %s", item["created_time"])
        logger.info("-" * 50)

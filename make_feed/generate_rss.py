import logging
from datetime import UTC, datetime
from pathlib import Path

from feedgen.feed import FeedGenerator

logger = logging.getLogger(__name__)


def create_feed_description(item: dict[str, str | None]) -> str:
    """Create a rich HTML description for the RSS feed entry.

    Args:
        item: Dictionary containing item information from Notion

    Returns:
        HTML-formatted description string
    """
    description_parts = []

    # Add comments if available
    if item.get("comments"):
        description_parts.append(f"<p><strong>Comments:</strong> {item['comments']}</p>")

    # Add tags if available
    if item.get("tags"):
        description_parts.append(f"<p><strong>Tags:</strong> {item['tags']}</p>")

    # Add status if available
    if item.get("status"):
        description_parts.append(f"<p><strong>Status:</strong> {item['status']}</p>")

    # Add creation date
    if item.get("created_time"):
        try:
            created_date = datetime.fromisoformat(item["created_time"])
            formatted_date = created_date.strftime("%Y-%m-%d %H:%M:%S UTC")
            description_parts.append(f"<p><strong>Added:</strong> {formatted_date}</p>")
        except (ValueError, AttributeError) as e:
            logger.warning("Failed to parse created_time: %s", e)

    return (
        "".join(description_parts)
        if description_parts
        else "<p>No additional information available.</p>"
    )


def parse_publication_date(created_time: str | None) -> datetime:
    """Parse publication date from created_time string.

    Args:
        created_time: ISO format timestamp string

    Returns:
        Parsed datetime object or current time if parsing fails
    """
    if not created_time:
        return datetime.now(tz=UTC)

    try:
        return datetime.fromisoformat(created_time)
    except (ValueError, AttributeError) as e:
        logger.warning("Failed to parse publication date: %s", e)
        return datetime.now(tz=UTC)


def create_feed_entry(fg: FeedGenerator, item: dict[str, str | None]) -> bool:
    """Create a single RSS feed entry.

    Args:
        fg: FeedGenerator instance
        item: Item data from Notion

    Returns:
        True if entry was created successfully, False otherwise
    """
    try:
        fe = fg.add_entry()
        fe.id(item["url"])
        fe.title(item.get("title", "Untitled"))
        fe.link(href=item["url"])

        # Create rich description
        description = create_feed_description(item)
        fe.description(description)

        # Set publication date
        pub_date = parse_publication_date(item.get("created_time"))
        fe.published(pub_date)

    except (ValueError, KeyError, AttributeError):
        logger.exception("Failed to process item '%s'", item.get("title", "Unknown"))
        return False
    else:
        return True


def generate_rss(
    items: list[dict[str, str | None]],
    feed_path: str = "notion_reading_list.xml",
    feed_title: str = "Notion Reading List",
    feed_description: str = "My personal reading list collected in Notion",
    feed_link: str | None = None,
) -> bool:
    """Generate RSS feed from Notion reading list items.

    Args:
        items: List of reading list items from Notion
        feed_path: Path where the RSS file will be saved
        feed_title: Title of the RSS feed
        feed_description: Description of the RSS feed
        feed_link: Self-referencing link for the feed

    Returns:
        True if RSS generation was successful, False otherwise
    """
    if not items:
        logger.warning("No items provided for RSS generation")
        return False

    # Filter items with URLs
    valid_items = [item for item in items if item.get("url")]

    if not valid_items:
        logger.warning("No items with valid URLs found")
        return False

    try:
        # Initialize feed generator
        fg = FeedGenerator()
        fg.id("notion-reading-list")
        fg.title(feed_title)
        fg.description(feed_description)
        fg.language("en")
        fg.lastBuildDate(datetime.now(tz=UTC))

        # Set feed link
        if feed_link:
            fg.link(href=feed_link, rel="self")
        else:
            fg.link(href=f"file://{Path(feed_path).absolute()}", rel="self")

        # Add author information
        fg.author({"name": "Notion RSS Generator", "email": "noreply@example.com"})

        logger.info("Processing %d valid items for RSS feed", len(valid_items))

        # Add entries to feed
        successful_entries = 0
        for item in valid_items:
            if create_feed_entry(fg, item):
                successful_entries += 1

        if successful_entries == 0:
            logger.error("No entries could be processed successfully")
            return False

        # Generate RSS file
        fg.rss_file(feed_path)

    except Exception:
        logger.exception("Failed to generate RSS feed")
        return False
    else:
        logger.info("RSS feed successfully generated: %s", feed_path)
        return True

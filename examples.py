#!/usr/bin/env python3
"""Example usage of the RSS Feed Generator.

This script demonstrates how to use the RSS generator programmatically.
"""

import logging
import sys
from pathlib import Path

from make_feed.config import Config, configure_logging
from make_feed.generate_rss import generate_rss
from make_feed.pull_notion import fetch_reading_list


def example_basic_usage(logger: logging.Logger) -> None:
    """Example of basic RSS generation."""
    logger.info("Starting basic RSS generation example...")

    # Validate configuration
    config = Config()
    config_errors = config.validate()
    if config_errors:
        logger.error("Configuration validation failed:")
        for error in config_errors:
            logger.error("  - %s", error)
        return

    # Fetch data from Notion
    logger.info("Fetching reading list from Notion...")
    reading_list = fetch_reading_list()

    if not reading_list:
        logger.error("No reading list items found")
        return

    logger.info("Found %d items in reading list", len(reading_list))

    # Generate RSS feed
    output_path = "example_feed.xml"
    success = generate_rss(
        items=reading_list,
        feed_path=output_path,
        feed_title="Example Reading List",
        feed_description="An example RSS feed generated from Notion",
        feed_link="https://example.com/feed.xml",
    )

    if success:
        full_path = Path(output_path).resolve()
        logger.info("RSS feed generated successfully: %s", full_path)
        logger.info("You can now use this RSS feed in your feed reader.")
    else:
        logger.error("Failed to generate RSS feed")


def example_custom_configuration(logger: logging.Logger) -> None:
    """Example with custom configuration."""
    logger.info("Starting custom configuration example...")

    # Get configuration instance
    config = Config()

    # Show current configuration
    logger.info("Current configuration:")
    logger.info("  Notion API Key: %s", "***" if config.NOTION_API_KEY else "NOT SET")
    logger.info(
        "  Database ID: %s",
        config.NOTION_DATABASE_ID[:8] + "..." if config.NOTION_DATABASE_ID else "NOT SET",
    )
    logger.info("  Default feed path: %s", config.RSS_FEED_PATH)
    logger.info("  Default feed title: %s", config.RSS_FEED_TITLE)

    # Fetch and process data
    reading_list = fetch_reading_list()

    if reading_list:
        logger.info("Sample item from reading list:")
        sample_item = reading_list[0]
        for key, value in sample_item.items():
            logger.info("  %s: %s", key, value)


def main() -> None:
    """Run examples based on command line argument."""
    configure_logging(verbose=True)  # Enable debug logging for examples
    logger = logging.getLogger(__name__)

    if len(sys.argv) > 1 and sys.argv[1] == "config":
        example_custom_configuration(logger)
    else:
        example_basic_usage(logger)


if __name__ == "__main__":
    main()

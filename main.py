#!/usr/bin/env python3
"""Main entry point for the Notion RSS Feed Generator.

This module provides the command-line interface and main execution logic
for generating RSS feeds from Notion database content.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import NoReturn

from make_feed.config import Config, configure_logging
from make_feed.generate_rss import generate_rss
from make_feed.pull_notion import display_reading_list, fetch_reading_list


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Generate RSS feeds from Notion database content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Generate RSS with default settings
  %(prog)s --output my_feed.xml         # Specify output file
  %(prog)s --title "My Reading List"    # Custom feed title
  %(prog)s --display-only               # Only display items, don't generate RSS
  %(prog)s --verbose                    # Enable debug logging
        """,
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="notion_reading_list.xml",
        help="Output RSS file path (default: notion_reading_list.xml)",
    )

    parser.add_argument(
        "--title",
        "-t",
        type=str,
        default="Notion Reading List",
        help="RSS feed title (default: Notion Reading List)",
    )

    parser.add_argument(
        "--description",
        "-d",
        type=str,
        default="My personal reading list collected in Notion",
        help="RSS feed description",
    )

    parser.add_argument(
        "--link", "-l", type=str, help="RSS feed self-referencing link URL"
    )

    parser.add_argument(
        "--display-only",
        action="store_true",
        help="Only display items without generating RSS feed",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose (debug) logging"
    )

    return parser


def validate_arguments(args: argparse.Namespace, *, logger: logging.Logger) -> None:
    """Validate command-line arguments.

    Args:
        args: Parsed command-line arguments
        logger: Logger instance for error reporting
    """
    if not args.display_only:
        output_path = Path(args.output)

        # Check if output directory exists and is writable
        output_dir = output_path.parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                logger.exception("Cannot create output directory '%s'", output_dir)
                sys.exit(1)

        if not output_dir.is_dir():
            logger.error("Output directory '%s' is not a directory", output_dir)
            sys.exit(1)


def main() -> NoReturn:
    """Main entry point for the application."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Setup logging
    configure_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Validate configuration
        config = Config()
        config_errors = config.validate()
        if config_errors:
            logger.error("Configuration validation failed:")
            for error in config_errors:
                logger.error("  - %s", error)
            logger.info("Please check your .env file or environment variables")
            sys.exit(1)

        # Validate arguments
        validate_arguments(args, logger=logger)

        logger.info("Starting Notion RSS Feed Generator")
        logger.debug("Arguments: %s", vars(args))

        # Fetch reading list from Notion
        logger.info("Fetching reading list from Notion...")
        reading_list = fetch_reading_list()

        if not reading_list:
            logger.error("No reading list items retrieved from Notion")
            logger.info("Please check your Notion API configuration and database ID")
            sys.exit(1)

        logger.info("Retrieved %d items from Notion", len(reading_list))

        # Display items if requested
        if args.display_only:
            logger.info("Displaying reading list items:")
            display_reading_list(reading_list)
            logger.info("Display completed successfully")
            sys.exit(0)

        # Generate RSS feed
        logger.info("Generating RSS feed...")
        success = generate_rss(
            items=reading_list,
            feed_path=args.output,
            feed_title=args.title,
            feed_description=args.description,
            feed_link=args.link,
        )

        if success:
            output_path = Path(args.output).resolve()
            logger.info("RSS feed generated successfully: %s", output_path)
            valid_items_count = len([item for item in reading_list if item.get("url")])
            logger.info("Feed contains %d items", valid_items_count)
            sys.exit(0)
        else:
            logger.error("RSS feed generation failed")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception:
        logger.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Simple HTTP server to serve RSS feeds locally.

This script creates a basic HTTP server that serves the generated RSS feed
for local consumption by FreshRSS or other feed readers.
"""

import argparse
import http.server
import os
import socketserver
import sys
from pathlib import Path

# Constants
ADDRESS_ALREADY_IN_USE_ERRNO = 98


def serve_rss(
    *,
    port: int = 8080,
    directory: str = ".",
    feed_file: str = "notion_reading_list.xml",
) -> None:
    """Serve RSS feed via HTTP server.

    Args:
        port: Port number to serve on
        directory: Directory to serve files from
        feed_file: Name of the RSS feed file
    """
    # Change to the specified directory
    serve_dir = Path(directory).resolve()

    if not serve_dir.exists():
        sys.stderr.write(f"Error: Directory {serve_dir} does not exist\n")
        sys.exit(1)

    feed_path = serve_dir / feed_file
    if not feed_path.exists():
        sys.stderr.write(f"Warning: RSS feed file {feed_path} does not exist yet\n")
        sys.stderr.write("Generate it first with: python main.py\n")

    # Create HTTP server
    handler = http.server.SimpleHTTPRequestHandler

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            sys.stdout.write(f"Server started at http://localhost:{port}/\n")
            sys.stdout.write(f"RSS Feed URL: http://localhost:{port}/{feed_file}\n")
            sys.stdout.write("Press Ctrl+C to stop the server\n")

            # Change to serve directory
            os.chdir(serve_dir)

            httpd.serve_forever()

    except KeyboardInterrupt:
        sys.stdout.write("\nServer stopped\n")
    except OSError as e:
        if e.errno == ADDRESS_ALREADY_IN_USE_ERRNO:  # Address already in use
            sys.stderr.write(f"Error: Port {port} is already in use\n")
            sys.stderr.write(f"Try: python {sys.argv[0]} --port {port + 1}\n")
        else:
            sys.stderr.write(f"Error starting server: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve RSS feeds locally")
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8080,
        help="Port to serve on (default: 8080)",
    )
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=".",
        help="Directory to serve files from (default: current directory)",
    )
    parser.add_argument(
        "--feed-file",
        "-f",
        type=str,
        default="notion_reading_list.xml",
        help="RSS feed filename (default: notion_reading_list.xml)",
    )

    args = parser.parse_args()

    serve_rss(
        port=args.port,
        directory=args.directory,
        feed_file=args.feed_file,
    )

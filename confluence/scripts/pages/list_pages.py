#!/usr/bin/env python3
"""List Confluence pages with optional filters.

Reads JSON input from stdin with optional filters.
Optional parameters: space_id, title, status, limit (default: 25), cursor.

Example input:
{
    "space_id": "123456",
    "status": "current",
    "limit": 50
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """List Confluence pages from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Build query parameters from optional filters
    params = {}

    if "space_id" in data:
        params["space-id"] = data["space_id"]

    if "title" in data:
        params["title"] = data["title"]

    if "status" in data:
        params["status"] = data["status"]

    # Set limit with default
    params["limit"] = data.get("limit", 25)

    if "cursor" in data:
        params["cursor"] = data["cursor"]

    try:
        client = ConfluenceClient()
        result = client.get("pages", params if params else None)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

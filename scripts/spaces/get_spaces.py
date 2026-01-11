#!/usr/bin/env python3
"""List all Confluence spaces.

Reads JSON input from stdin with optional pagination parameters.
Optional parameters: limit (default: 25), cursor.

Example input:
{
    "limit": 50,
    "cursor": "eyJpZCI6IjEyMzQ1NiJ9"
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """List Confluence spaces from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Build query parameters
    params = {}

    # Set limit with default
    params["limit"] = data.get("limit", 25)

    if "cursor" in data:
        params["cursor"] = data["cursor"]

    try:
        client = ConfluenceClient()
        result = client.get("spaces", params)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

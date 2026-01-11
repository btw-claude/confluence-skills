#!/usr/bin/env python3
"""Create a new Confluence page.

Reads JSON input from stdin with required space_id, title, and body.
Optional parameters: parent_id, status (default: "current").

Example input:
{
    "space_id": "123456",
    "title": "My Page",
    "body": "<p>Page content in storage format.</p>",
    "parent_id": "789012",
    "status": "current"
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Create a Confluence page from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["space_id", "title", "body"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    # Build request payload
    payload = {
        "spaceId": data["space_id"],
        "title": data["title"],
        "body": {
            "representation": "storage",
            "value": data["body"]
        },
        "status": data.get("status", "current")
    }

    # Add optional parent page
    if "parent_id" in data:
        payload["parentId"] = data["parent_id"]

    try:
        client = ConfluenceClient()
        result = client.post("pages", payload)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

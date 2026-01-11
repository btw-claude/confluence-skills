#!/usr/bin/env python3
"""Update an existing Confluence page.

Reads JSON input from stdin with required page_id, title, body, and version_number.
The version_number must match the current version to prevent conflicts.

Example input:
{
    "page_id": "456789",
    "title": "Updated Title",
    "body": "<p>Updated content in storage format.</p>",
    "version_number": 1
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Update a Confluence page from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["page_id", "title", "body", "version_number"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    page_id = data["page_id"]

    # Build request payload
    payload = {
        "id": page_id,
        "title": data["title"],
        "body": {
            "representation": "storage",
            "value": data["body"]
        },
        "version": {
            "number": data["version_number"] + 1,
            "message": data.get("version_message", "")
        },
        "status": "current"
    }

    try:
        client = ConfluenceClient()
        result = client.put(f"pages/{page_id}", payload)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

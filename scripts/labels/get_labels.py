#!/usr/bin/env python3
"""Get labels on a Confluence page.

Reads JSON input from stdin with required page_id.
Optional parameters: limit (default: 25), cursor.

Example input:
{
    "page_id": "456789",
    "limit": 50
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Get labels on a Confluence page from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["page_id"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    page_id = data["page_id"]

    # Build query parameters
    params = {}
    params["limit"] = data.get("limit", 25)

    if "cursor" in data:
        params["cursor"] = data["cursor"]

    try:
        client = ConfluenceClient()
        result = client.get(f"pages/{page_id}/labels", params)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

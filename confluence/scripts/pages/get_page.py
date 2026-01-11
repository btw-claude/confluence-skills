#!/usr/bin/env python3
"""Get a Confluence page by ID.

Reads JSON input from stdin with required page_id.
Optional parameters: include_body (default: true), body_format (default: "storage").

Example input:
{
    "page_id": "456789",
    "include_body": true,
    "body_format": "storage"
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Get a Confluence page from stdin JSON input."""
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
    include_body = data.get("include_body", True)
    body_format = data.get("body_format", "storage")

    # Build query parameters
    params = {}
    if include_body:
        params["body-format"] = body_format

    try:
        client = ConfluenceClient()
        result = client.get(f"pages/{page_id}", params if params else None)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

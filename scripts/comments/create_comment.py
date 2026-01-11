#!/usr/bin/env python3
"""Create a comment on a Confluence page.

Reads JSON input from stdin with required page_id and body.

Example input:
{
    "page_id": "456789",
    "body": "<p>This is a comment.</p>"
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Create a comment on a Confluence page from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["page_id", "body"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    page_id = data["page_id"]

    # Build request payload
    payload = {
        "body": {
            "representation": "storage",
            "value": data["body"]
        }
    }

    try:
        client = ConfluenceClient()
        result = client.post(f"pages/{page_id}/footer-comments", payload)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Delete a comment from a Confluence page.

Reads JSON input from stdin with required comment_id.

Example input:
{
    "comment_id": "123456"
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Delete a comment from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["comment_id"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    comment_id = data["comment_id"]

    try:
        client = ConfluenceClient()
        success = client.delete(f"footer-comments/{comment_id}")
        result = {
            "success": success,
            "comment_id": comment_id
        }
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

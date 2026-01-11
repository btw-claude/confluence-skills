#!/usr/bin/env python3
"""Add a label to a Confluence page.

Reads JSON input from stdin with required page_id and label.

Example input:
{
    "page_id": "456789",
    "label": "reviewed"
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Add a label to a Confluence page from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["page_id", "label"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    page_id = data["page_id"]
    label = data["label"]

    # Build request payload - API expects a single label object
    payload = {
        "name": label
    }

    try:
        client = ConfluenceClient()
        result = client.post(f"pages/{page_id}/labels", payload)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

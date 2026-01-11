#!/usr/bin/env python3
"""Delete an attachment from Confluence.

Reads JSON input from stdin with required attachment_id.
Optional parameter: purge (default: false) - permanently delete vs move to trash.

Example input:
{
    "attachment_id": "123456",
    "purge": false
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Delete an attachment from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["attachment_id"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    attachment_id = data["attachment_id"]
    purge = data.get("purge", False)

    # Build query parameters
    params = {}
    if purge:
        params["purge"] = "true"

    try:
        client = ConfluenceClient()
        success = client.delete(f"attachments/{attachment_id}", params if params else None)
        result = {
            "success": success,
            "attachment_id": attachment_id,
            "purged": purge
        }
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

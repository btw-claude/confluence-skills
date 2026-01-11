#!/usr/bin/env python3
"""Delete a Confluence space.

Reads JSON input from stdin with required space_key.
Note: This operation is asynchronous and permanently deletes the space and all its content.

Example input:
{
    "space_key": "DEV"
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Delete a Confluence space from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["space_key"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    space_key = data["space_key"]

    try:
        client = ConfluenceClient()

        # v2 API does not support space deletion
        # success = client.delete(f"spaces/{space_key}")

        # Use v1 API for space deletion
        success = client.delete_v1(f"space/{space_key}")

        result = {
            "success": success,
            "space_key": space_key,
            "message": "Space deletion initiated. This is an asynchronous operation."
        }
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

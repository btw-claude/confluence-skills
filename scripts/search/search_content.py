#!/usr/bin/env python3
"""Search Confluence content using CQL (Confluence Query Language).

Reads JSON input from stdin with required query (CQL string).
Optional parameters: limit (default: 25), cursor.

Example input:
{
    "query": "type=page AND space=DEV",
    "limit": 50
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Search Confluence content from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["query"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    # Build query parameters
    params = {
        "cql": data["query"],
        "limit": data.get("limit", 25)
    }

    if "cursor" in data:
        params["cursor"] = data["cursor"]

    try:
        client = ConfluenceClient()
        result = client.get("content/search", params)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

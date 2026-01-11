#!/usr/bin/env python3
"""Create a new Confluence space.

Reads JSON input from stdin with required name.
Optional parameters: key, description, alias, create_private_space (default: false).

Example input:
{
    "name": "Development Team",
    "key": "DEV",
    "description": "Space for development team documentation",
    "create_private_space": false
}
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from confluence_client import ConfluenceClient


def main():
    """Create a Confluence space from stdin JSON input."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required parameters
    required = ["name"]
    missing = [p for p in required if p not in data]
    if missing:
        print(f"Error: Missing required parameters: {missing}", file=sys.stderr)
        sys.exit(1)

    # Build request payload
    payload = {
        "name": data["name"]
    }

    # Add optional parameters
    if "key" in data:
        payload["key"] = data["key"]

    if "description" in data:
        payload["description"] = {
            "plain": {
                "value": data["description"],
                "representation": "plain"
            }
        }

    if "alias" in data:
        payload["alias"] = data["alias"]

    # Handle private space creation (default: false)
    if data.get("create_private_space", False):
        payload["permissions"] = [
            {
                "principal": {
                    "type": "user",
                    "id": "current"
                },
                "operation": {
                    "key": "administer",
                    "targetType": "space"
                }
            }
        ]

    try:
        client = ConfluenceClient()
        result = client.post("spaces", payload)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

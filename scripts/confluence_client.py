#!/usr/bin/env python3
"""Confluence API client with environment-based configuration."""

import os
import sys
from pathlib import Path
from typing import Optional
import requests
from requests.auth import HTTPBasicAuth


def load_env() -> dict[str, str]:
    """Load environment from .claude/env or ~/.claude/env.

    Searches for environment files in the following order:
    1. .claude/env (project-level, in current working directory)
    2. ~/.claude/env (user-level, in home directory)

    Returns:
        dict[str, str]: Dictionary of environment variable key-value pairs.

    Exits:
        Exits with status 1 if no env file is found.
    """
    env_paths = [
        Path(".claude/env"),
        Path.home() / ".claude/env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            env_vars = {}
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')
            return env_vars

    print("Error: No env file found at .claude/env or ~/.claude/env", file=sys.stderr)
    sys.exit(1)


class ConfluenceClient:
    """Confluence REST API v2 client.

    Provides methods for interacting with the Confluence REST API v2.
    Authentication is handled via HTTP Basic Auth using email and API token.

    Attributes:
        base_url: The base Confluence URL (e.g., https://your-domain.atlassian.net)
        api_url: The full API URL ({base_url}/wiki/api/v2)
        auth: HTTPBasicAuth object for request authentication
        headers: Default headers for API requests
    """

    def __init__(self):
        """Initialize the Confluence client with environment configuration.

        Loads configuration from environment files and sets up authentication.

        Exits:
            Exits with status 1 if required environment variables are missing.
        """
        env = load_env()
        self.base_url = env.get("CONFLUENCE_BASE_URL", "").rstrip("/")
        self.email = env.get("CONFLUENCE_EMAIL", "")
        self.token = env.get("CONFLUENCE_API_TOKEN", "")

        if not all([self.base_url, self.email, self.token]):
            print("Error: Missing required env vars (CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)", file=sys.stderr)
            sys.exit(1)

        self.api_url = f"{self.base_url}/wiki/api/v2"
        self.auth = HTTPBasicAuth(self.email, self.token)
        self.headers = {"Content-Type": "application/json"}

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Send a GET request to the Confluence API.

        Args:
            endpoint: API endpoint path (without base URL).
            params: Optional query parameters.

        Returns:
            dict: JSON response from the API.

        Raises:
            requests.HTTPError: If the request fails.
        """
        resp = requests.get(
            f"{self.api_url}/{endpoint}",
            auth=self.auth,
            headers=self.headers,
            params=params
        )
        resp.raise_for_status()
        return resp.json()

    def post(self, endpoint: str, data: dict) -> dict:
        """Send a POST request to the Confluence API.

        Args:
            endpoint: API endpoint path (without base URL).
            data: JSON data to send in the request body.

        Returns:
            dict: JSON response from the API.

        Raises:
            requests.HTTPError: If the request fails.
        """
        resp = requests.post(
            f"{self.api_url}/{endpoint}",
            auth=self.auth,
            headers=self.headers,
            json=data
        )
        resp.raise_for_status()
        return resp.json()

    def put(self, endpoint: str, data: dict) -> dict:
        """Send a PUT request to the Confluence API.

        Args:
            endpoint: API endpoint path (without base URL).
            data: JSON data to send in the request body.

        Returns:
            dict: JSON response from the API.

        Raises:
            requests.HTTPError: If the request fails.
        """
        resp = requests.put(
            f"{self.api_url}/{endpoint}",
            auth=self.auth,
            headers=self.headers,
            json=data
        )
        resp.raise_for_status()
        return resp.json()

    def delete(self, endpoint: str, params: Optional[dict] = None) -> bool:
        """Send a DELETE request to the Confluence API.

        Args:
            endpoint: API endpoint path (without base URL).
            params: Optional query parameters.

        Returns:
            bool: True if deletion was successful (status 200 or 204).

        Raises:
            requests.HTTPError: If the request fails.
        """
        resp = requests.delete(
            f"{self.api_url}/{endpoint}",
            auth=self.auth,
            headers=self.headers,
            params=params
        )
        resp.raise_for_status()
        return resp.status_code in (200, 204)

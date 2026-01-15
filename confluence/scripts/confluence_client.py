#!/usr/bin/env python3
"""Confluence API client with environment-based configuration."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional
import requests
from requests.auth import HTTPBasicAuth

# Configure module logger
logger = logging.getLogger(__name__)


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

    logger.error("No env file found at .claude/env or ~/.claude/env")
    sys.exit(1)


class AuthenticationError(Exception):
    """Raised when authentication with Confluence fails."""


# Default timeout in seconds for HTTP requests
DEFAULT_TIMEOUT = 10


class ConfluenceClient:
    """Confluence REST API client.

    Provides methods for interacting with the Confluence REST API.
    Supports both v2 API (default) and v1 API (for operations not available in v2).
    Authentication is handled via either:
    - Personal Access Token (PAT) using Bearer token authentication
    - HTTP Basic Auth using email and API token

    PAT authentication takes precedence if both methods are configured.

    Attributes:
        base_url: The Confluence base URL (CONFLUENCE_URL)
        api_url: The v2 API URL ({CONFLUENCE_URL}/api/v2)
        api_url_v1: The v1 API URL ({CONFLUENCE_URL}/rest/api)
        auth: HTTPBasicAuth object for request authentication (None if using PAT)
        headers: Default headers for API requests (includes Authorization for PAT)
        auth_type: The authentication type being used ('pat' or 'basic')
        timeout: HTTP request timeout in seconds (configurable via CONFLUENCE_TIMEOUT)
    """

    def __init__(self, validate_auth: bool = True):
        """Initialize the Confluence client with environment configuration.

        Loads configuration from environment files and sets up authentication.
        Supports two authentication methods:
        - PAT (Personal Access Token): Set CONFLUENCE_PAT for Bearer token auth
        - Basic Auth: Set CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN

        PAT takes precedence if both authentication methods are configured.

        Args:
            validate_auth: If True (default), validates authentication credentials
                by making a lightweight API call during initialization. Set to False
                to skip validation for improved performance when credentials are
                known to be valid.

        Raises:
            AuthenticationError: If validate_auth is True and authentication fails.

        Exits:
            Exits with status 1 if required environment variables are missing.
        """
        env = load_env()
        self.base_url = env.get("CONFLUENCE_URL", "").rstrip("/")

        if not self.base_url:
            logger.error("Missing required env var CONFLUENCE_URL")
            sys.exit(1)

        # Check for PAT authentication (takes precedence)
        # Use local variables to avoid storing credentials as instance attributes
        pat = env.get("CONFLUENCE_PAT", "")

        # Check for Basic Auth credentials
        email = env.get("CONFLUENCE_EMAIL", "")
        token = env.get("CONFLUENCE_API_TOKEN", "")

        # Set up authentication based on available credentials
        self.headers = {"Content-Type": "application/json"}

        if pat:
            # Use PAT authentication (Bearer token)
            self.auth_type = "pat"
            self.auth = None
            self.headers["Authorization"] = f"Bearer {pat}"
            logger.debug("Confluence client initialized with PAT authentication")
        elif email and token:
            # Use Basic authentication
            self.auth_type = "basic"
            self.auth = HTTPBasicAuth(email, token)
            logger.debug("Confluence client initialized with Basic authentication")
        else:
            logger.error(
                "No authentication configured. Please set either:\n"
                "  - CONFLUENCE_PAT for Personal Access Token authentication, or\n"
                "  - CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN for Basic authentication"
            )
            sys.exit(1)

        self.api_url = f"{self.base_url}/api/v2"
        self.api_url_v1 = f"{self.base_url}/rest/api"

        # Configure timeout from environment or use default
        timeout_str = env.get("CONFLUENCE_TIMEOUT", "")
        if timeout_str:
            try:
                self.timeout = float(timeout_str)
                logger.info("Using configured timeout: %.2f seconds", self.timeout)
            except ValueError:
                logger.warning(
                    "Invalid CONFLUENCE_TIMEOUT value '%s', using default %d seconds",
                    timeout_str,
                    DEFAULT_TIMEOUT
                )
                self.timeout = DEFAULT_TIMEOUT
        else:
            self.timeout = DEFAULT_TIMEOUT

        logger.debug(
            "Confluence client configured: base_url=%s, auth_type=%s, timeout=%g",
            self.base_url,
            self.auth_type,
            self.timeout
        )

        # Validate authentication if requested
        if validate_auth:
            self._validate_authentication()

    def _validate_authentication(self) -> None:
        """Validate authentication credentials by making a lightweight API call.

        Makes a minimal API request to verify that the configured credentials
        are valid and working. Uses the space endpoint with limit=1 for minimal
        overhead.

        Raises:
            AuthenticationError: If authentication fails with clear guidance
                on how to resolve the issue.
        """
        try:
            resp = requests.get(
                f"{self.api_url_v1}/space",
                auth=self.auth,
                headers=self.headers,
                params={"limit": 1},
                timeout=self.timeout
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                if self.auth_type == "pat":
                    raise AuthenticationError(
                        "Authentication failed: Invalid or expired Personal Access Token.\n"
                        "Please verify your CONFLUENCE_PAT is correct and has not expired.\n"
                        "You can generate a new token at: "
                        "Settings > Personal Access Tokens in Confluence."
                    ) from e
                else:
                    raise AuthenticationError(
                        "Authentication failed: Invalid email or API token.\n"
                        "Please verify:\n"
                        "  - CONFLUENCE_EMAIL is your Atlassian account email\n"
                        "  - CONFLUENCE_API_TOKEN is a valid API token\n"
                        "You can generate a new token at: "
                        "https://id.atlassian.com/manage-profile/security/api-tokens"
                    ) from e
            elif e.response.status_code == 403:
                raise AuthenticationError(
                    "Authentication failed: Access forbidden.\n"
                    "Your credentials are valid but you don't have permission to access "
                    "Confluence.\nPlease contact your Confluence administrator."
                ) from e
            else:
                raise AuthenticationError(
                    f"Authentication validation failed with status {e.response.status_code}.\n"
                    f"Please verify your Confluence URL and credentials.\n"
                    f"Error: {e.response.text}"
                ) from e
        except requests.exceptions.Timeout as e:
            raise AuthenticationError(
                f"Connection to Confluence at {self.base_url} timed out.\n"
                "The server may be slow or unresponsive. Please try again later."
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise AuthenticationError(
                f"Could not connect to Confluence at {self.base_url}.\n"
                "Please verify CONFLUENCE_URL is correct and the server is reachable."
            ) from e
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(
                f"Authentication validation failed: {str(e)}"
            ) from e

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Send a GET request to the Confluence v2 API.

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
            params=params,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def get_v1(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Send a GET request to the Confluence v1 API.

        Some operations (like search) require the v1 API.

        Args:
            endpoint: API endpoint path (without base URL).
            params: Optional query parameters.

        Returns:
            dict: JSON response from the API.

        Raises:
            requests.HTTPError: If the request fails.
        """
        resp = requests.get(
            f"{self.api_url_v1}/{endpoint}",
            auth=self.auth,
            headers=self.headers,
            params=params,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def post(self, endpoint: str, data: dict) -> dict:
        """Send a POST request to the Confluence v2 API.

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
            json=data,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def post_v1(self, endpoint: str, data: dict) -> dict:
        """Send a POST request to the Confluence v1 API.

        Some operations (like space creation) require the v1 API
        when RBAC is not enabled on the Confluence site.

        Args:
            endpoint: API endpoint path (without base URL).
            data: JSON data to send in the request body.

        Returns:
            dict: JSON response from the API.

        Raises:
            requests.HTTPError: If the request fails.
        """
        resp = requests.post(
            f"{self.api_url_v1}/{endpoint}",
            auth=self.auth,
            headers=self.headers,
            json=data,
            timeout=self.timeout
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
            json=data,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.json()

    def delete(self, endpoint: str, params: Optional[dict] = None) -> bool:
        """Send a DELETE request to the Confluence v2 API.

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
            params=params,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.status_code in (200, 204)

    def delete_v1(self, endpoint: str, params: Optional[dict] = None) -> bool:
        """Send a DELETE request to the Confluence v1 API.

        Some operations (like space deletion) require the v1 API.

        Args:
            endpoint: API endpoint path (without base URL).
            params: Optional query parameters.

        Returns:
            bool: True if deletion was successful (status 200, 202, or 204).

        Raises:
            requests.HTTPError: If the request fails.
        """
        resp = requests.delete(
            f"{self.api_url_v1}/{endpoint}",
            auth=self.auth,
            headers=self.headers,
            params=params,
            timeout=self.timeout
        )
        resp.raise_for_status()
        return resp.status_code in (200, 202, 204)

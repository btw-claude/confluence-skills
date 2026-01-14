---
name: confluence
description: Manage Confluence wiki pages, spaces, comments, labels, and attachments. Search content using CQL queries.
---

# Confluence Skill

This skill provides comprehensive Confluence wiki operations through the Atlassian REST API v2.

## Available Operations

This skill is organized into granular operation files:

- **[Managing Pages](managing-pages.md)** - Create, read, update, and delete Confluence pages
- **[Managing Spaces](managing-spaces.md)** - List, create, and manage Confluence spaces
- **[Managing Comments](managing-comments.md)** - Add, view, and delete page comments
- **[Managing Labels](managing-labels.md)** - Add, view, and remove page labels
- **[Searching Content](searching-content.md)** - Search Confluence using CQL (Confluence Query Language)
- **[Managing Attachments](managing-attachments.md)** - View and manage page attachments

## Configuration

### Authentication Methods

This skill supports two authentication methods:

1. **Personal Access Token (PAT)** - Bearer token authentication
2. **Basic Authentication** - Email + API token

**Precedence Rule**: If both authentication methods are configured, PAT authentication takes precedence.

### Option 1: Personal Access Token (PAT)

Personal Access Tokens provide a simple, single-token authentication method. Use PAT when:
- You prefer a single credential to manage
- Your organization uses PAT-based authentication
- You're working with Confluence Data Center or Server

#### Required Environment Variables

```
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_PAT=your-personal-access-token
```

#### Creating a PAT

For Confluence Cloud, create a PAT at: https://id.atlassian.com/manage-profile/security/api-tokens

For Confluence Data Center/Server, navigate to your profile settings and select "Personal Access Tokens".

### Option 2: Basic Authentication (Email + API Token)

Basic authentication uses your email address combined with an API token. Use Basic Auth when:
- You're using Confluence Cloud
- Your organization requires email-based audit trails
- You need compatibility with existing API token infrastructure

#### Required Environment Variables

```
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
```

#### Creating an API Token

Create an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

### Environment File Locations

Environment variables are loaded in the following order of precedence:

1. **Project-level**: `.claude/env` (in the current working directory)
2. **User-level**: `~/.claude/env` (in the user's home directory)

The first file found is used.

### Example Configurations

#### Example .claude/env with PAT Authentication

```bash
# Confluence API Configuration (PAT)
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_PAT=your-personal-access-token
```

#### Example .claude/env with Basic Authentication

```bash
# Confluence API Configuration (Basic Auth)
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
```

### Authentication Precedence

When multiple authentication methods are configured:

1. **CONFLUENCE_PAT** is checked first - if set, Bearer token authentication is used
2. **CONFLUENCE_EMAIL + CONFLUENCE_API_TOKEN** are used as fallback for Basic authentication
3. If neither method is configured, an error is displayed with setup instructions

## API Reference

All operations use the Confluence REST API v2 at `{CONFLUENCE_URL}/api/v2`.

For detailed API documentation, see: https://developer.atlassian.com/cloud/confluence/rest/v2/intro/

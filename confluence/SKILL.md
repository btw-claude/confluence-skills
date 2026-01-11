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

### Required Environment Variables

The following environment variables must be configured:

```
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
```

### Environment File Locations

Environment variables are loaded in the following order of precedence:

1. **Project-level**: `.claude/env` (in the current working directory)
2. **User-level**: `~/.claude/env` (in the user's home directory)

The first file found is used. Create an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

### Example .claude/env

```bash
# Confluence API Configuration
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
```

## API Reference

All operations use the Confluence REST API v2 at `{CONFLUENCE_URL}/api/v2`.

For detailed API documentation, see: https://developer.atlassian.com/cloud/confluence/rest/v2/intro/

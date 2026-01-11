# Managing Confluence Spaces

This guide covers operations for managing Confluence spaces using the provided scripts.

## Overview

Confluence spaces are organizational containers that hold pages, blog posts, and other content. Each space has a unique key (e.g., "DEV", "HR") used in URLs and API calls. Spaces can be public or private, and have their own permission settings.

## Scripts

All scripts read JSON input from stdin and output JSON results to stdout. Errors are written to stderr with a non-zero exit code.

### List Spaces

**Script:** `scripts/spaces/get_spaces.py`

Lists all spaces the user has access to, with pagination support.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 25 | Maximum number of results (1-250) |
| cursor | string | No | - | Pagination cursor from previous response |

#### Example Usage

List spaces with default limit:

```bash
echo '{}' | python scripts/spaces/get_spaces.py
```

List with custom limit:

```bash
echo '{"limit": 50}' | python scripts/spaces/get_spaces.py
```

Paginate results:

```bash
echo '{
  "cursor": "eyJpZCI6IjEyMzQ1NiJ9"
}' | python scripts/spaces/get_spaces.py
```

#### Example Output

```json
{
  "results": [
    {
      "id": "123456",
      "key": "DEV",
      "name": "Development Team",
      "type": "global",
      "status": "current",
      "authorId": "user123",
      "createdAt": "2024-01-10T09:00:00.000Z",
      "homepageId": "456789",
      "description": {
        "plain": {
          "value": "Space for development team documentation",
          "representation": "plain"
        }
      },
      "_links": {
        "webui": "/spaces/DEV"
      }
    },
    {
      "id": "123457",
      "key": "HR",
      "name": "Human Resources",
      "type": "global",
      "status": "current",
      "authorId": "user456",
      "createdAt": "2024-01-12T14:30:00.000Z",
      "homepageId": "456790",
      "_links": {
        "webui": "/spaces/HR"
      }
    }
  ],
  "_links": {
    "next": "/wiki/api/v2/spaces?cursor=eyJpZCI6IjEyMzQ1NyJ9"
  }
}
```

**Note:** The `_links.next` field contains the URL for the next page of results. Extract the cursor parameter and pass it in subsequent requests to paginate.

---

### Get Space

**Script:** `scripts/spaces/get_space.py`

Retrieves a single space by its ID.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| space_id | string | Yes | - | The ID of the space to retrieve |

#### Example Usage

```bash
echo '{"space_id": "123456"}' | python scripts/spaces/get_space.py
```

#### Example Output

```json
{
  "id": "123456",
  "key": "DEV",
  "name": "Development Team",
  "type": "global",
  "status": "current",
  "authorId": "user123",
  "createdAt": "2024-01-10T09:00:00.000Z",
  "homepageId": "456789",
  "description": {
    "plain": {
      "value": "Space for development team documentation",
      "representation": "plain"
    }
  },
  "_links": {
    "webui": "/spaces/DEV"
  }
}
```

---

### Create Space

**Script:** `scripts/spaces/create_space.py`

Creates a new Confluence space. Requires the 'Create Space' global permission.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | string | Yes | - | The display name of the space |
| key | string | No | - | Unique space key (uppercase letters, used in URLs). Auto-generated if not provided |
| description | string | No | - | Plain text description of the space |
| alias | string | No | - | Alternative name/alias for the space |
| create_private_space | boolean | No | false | If true, creates a private space visible only to the creator |

#### Example Usage

Create a basic space:

```bash
echo '{
  "name": "Project Alpha"
}' | python scripts/spaces/create_space.py
```

Create a space with all options:

```bash
echo '{
  "name": "Development Team",
  "key": "DEV",
  "description": "Space for development team documentation and guides",
  "create_private_space": false
}' | python scripts/spaces/create_space.py
```

Create a private space:

```bash
echo '{
  "name": "My Private Notes",
  "key": "PRIVATE",
  "create_private_space": true
}' | python scripts/spaces/create_space.py
```

#### Example Output

```json
{
  "id": "789012",
  "key": "DEV",
  "name": "Development Team",
  "type": "global",
  "status": "current",
  "authorId": "user123",
  "createdAt": "2024-01-15T10:30:00.000Z",
  "homepageId": "890123",
  "description": {
    "plain": {
      "value": "Space for development team documentation and guides",
      "representation": "plain"
    }
  },
  "_links": {
    "webui": "/spaces/DEV"
  }
}
```

**Note:** The space key must be unique across your Confluence instance. If not provided, Confluence will auto-generate one based on the space name.

---

### Delete Space

**Script:** `scripts/spaces/delete_space.py`

Deletes a Confluence space. Requires 'Admin' permission for the space.

**WARNING:** This operation permanently deletes the space and ALL its content (pages, blog posts, attachments, etc.). This cannot be undone.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| space_key | string | Yes | - | The space KEY (e.g., "DEV"), not the numeric ID |

#### Example Usage

```bash
echo '{"space_key": "DEV"}' | python scripts/spaces/delete_space.py
```

#### Example Output

```json
{
  "success": true,
  "space_key": "DEV",
  "message": "Space deletion initiated. This is an asynchronous operation."
}
```

**Note:** Space deletion is an asynchronous operation. The API returns immediately, but the actual deletion happens in the background. Large spaces with many pages may take some time to fully delete.

---

## Space Keys vs Space IDs

Confluence spaces have two identifiers:

- **Space ID**: A numeric identifier (e.g., "123456") used internally
- **Space Key**: A short uppercase string (e.g., "DEV", "HR") used in URLs

Most operations use the space ID, but **delete** operations use the space key.

| Operation | Uses |
|-----------|------|
| List spaces | - (returns both) |
| Get space | space_id |
| Create space | - (returns both) |
| Delete space | space_key |

## Error Handling

All scripts exit with code 1 on errors and print error details to stderr:

- **Invalid JSON input:** The input could not be parsed as JSON
- **Missing required parameters:** Required fields are not provided
- **API errors:** HTTP errors from Confluence (404 not found, 403 forbidden, etc.)
- **Authentication errors:** Invalid credentials or missing environment configuration
- **Permission errors:** User lacks required permissions (e.g., Create Space global permission)

Example error output:

```
Error: Missing required parameters: ['space_key']
```

```
Error: API request failed: 403 Forbidden - You do not have permission to create spaces
```

```
Error: API request failed: 404 Not Found - Space not found
```

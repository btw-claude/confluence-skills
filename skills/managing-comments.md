# Managing Confluence Comments

This guide covers operations for managing comments on Confluence pages using the provided scripts.

## Overview

Confluence comments allow users to discuss and collaborate on page content. Comments appear in the footer section of pages and support rich text formatting using Confluence's storage format.

## Scripts

All scripts read JSON input from stdin and output JSON results to stdout. Errors are written to stderr with a non-zero exit code.

### Create Comment

**Script:** `scripts/comments/create_comment.py`

Adds a new comment to a Confluence page.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to comment on |
| body | string | Yes | - | The comment content in storage format (Confluence XML) |

#### Example Usage

```bash
echo '{
  "page_id": "456789",
  "body": "<p>This is a helpful comment!</p>"
}' | python scripts/comments/create_comment.py
```

With rich formatting:

```bash
echo '{
  "page_id": "456789",
  "body": "<p>Great work on this page! A few suggestions:</p><ul><li>Add more examples</li><li>Include a diagram</li></ul>"
}' | python scripts/comments/create_comment.py
```

#### Example Output

```json
{
  "id": "789012",
  "status": "current",
  "title": "Re: My Page Title",
  "parentId": "456789",
  "authorId": "user123",
  "createdAt": "2024-01-15T14:30:00.000Z",
  "version": {
    "number": 1,
    "authorId": "user123",
    "createdAt": "2024-01-15T14:30:00.000Z"
  },
  "body": {
    "storage": {
      "value": "<p>This is a helpful comment!</p>",
      "representation": "storage"
    }
  },
  "_links": {
    "webui": "/pages/viewpage.action?pageId=456789#comment-789012"
  }
}
```

---

### Get Comments

**Script:** `scripts/comments/get_comments.py`

Retrieves all comments on a page with pagination support.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to get comments from |
| limit | integer | No | 25 | Maximum number of results (1-250) |
| cursor | string | No | - | Pagination cursor from previous response |

#### Example Usage

Get comments with default limit:

```bash
echo '{"page_id": "456789"}' | python scripts/comments/get_comments.py
```

Get more comments:

```bash
echo '{
  "page_id": "456789",
  "limit": 100
}' | python scripts/comments/get_comments.py
```

Paginate results:

```bash
echo '{
  "page_id": "456789",
  "cursor": "eyJpZCI6IjEyMzQ1NiJ9"
}' | python scripts/comments/get_comments.py
```

#### Example Output

```json
{
  "results": [
    {
      "id": "789012",
      "status": "current",
      "title": "Re: My Page Title",
      "parentId": "456789",
      "authorId": "user123",
      "createdAt": "2024-01-15T14:30:00.000Z",
      "version": {
        "number": 1,
        "authorId": "user123",
        "createdAt": "2024-01-15T14:30:00.000Z"
      },
      "body": {
        "storage": {
          "value": "<p>First comment</p>",
          "representation": "storage"
        }
      }
    },
    {
      "id": "789013",
      "status": "current",
      "title": "Re: My Page Title",
      "parentId": "456789",
      "authorId": "user456",
      "createdAt": "2024-01-15T15:00:00.000Z",
      "version": {
        "number": 1,
        "authorId": "user456",
        "createdAt": "2024-01-15T15:00:00.000Z"
      },
      "body": {
        "storage": {
          "value": "<p>Second comment</p>",
          "representation": "storage"
        }
      }
    }
  ],
  "_links": {
    "next": "/wiki/api/v2/pages/456789/footer-comments?cursor=eyJpZCI6Ijc4OTAxMyJ9"
  }
}
```

**Note:** The `_links.next` field contains the cursor for the next page of results. Extract the cursor parameter and pass it in subsequent requests to paginate.

---

### Delete Comment

**Script:** `scripts/comments/delete_comment.py`

Deletes a comment from a page.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| comment_id | string | Yes | - | The ID of the comment to delete |

#### Example Usage

```bash
echo '{"comment_id": "789012"}' | python scripts/comments/delete_comment.py
```

#### Example Output

```json
{
  "success": true,
  "comment_id": "789012"
}
```

---

## Comment Permissions

- **Creating comments:** Requires "Add Comments" permission on the page
- **Deleting comments:** Users can delete their own comments; space admins can delete any comment
- **Viewing comments:** Requires "View" permission on the page

## Error Handling

All scripts exit with code 1 on errors and print error details to stderr:

- **Invalid JSON input:** The input could not be parsed as JSON
- **Missing required parameters:** Required fields are not provided
- **API errors:** HTTP errors from Confluence (404 not found, 403 forbidden, etc.)
- **Authentication errors:** Invalid credentials or missing environment configuration

Example error output:

```
Error: Missing required parameters: ['page_id', 'body']
```

```
Error: API request failed: 403 Forbidden - You do not have permission to add comments
```

```
Error: API request failed: 404 Not Found - Page not found
```

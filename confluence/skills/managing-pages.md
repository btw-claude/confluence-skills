# Managing Confluence Pages

This guide covers CRUD operations for Confluence pages using the provided scripts.

## Overview

Confluence pages are the primary content units in Confluence. Each page belongs to a space and can optionally have a parent page for hierarchical organization. Pages support rich content using Confluence's storage format (XML-based).

## Scripts

All scripts read JSON input from stdin and output JSON results to stdout. Errors are written to stderr with a non-zero exit code.

### Create Page

**Script:** `scripts/pages/create_page.py`

Creates a new page in a Confluence space.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| space_id | string | Yes | - | The ID of the space to create the page in |
| title | string | Yes | - | The title of the page |
| body | string | Yes | - | The page content in storage format (Confluence XML) |
| parent_id | string | No | - | The ID of the parent page for nesting |
| status | string | No | "current" | Page status: "current" (published) or "draft" |

#### Example Usage

```bash
echo '{
  "space_id": "123456",
  "title": "My New Page",
  "body": "<p>This is the page content.</p>"
}' | python scripts/pages/create_page.py
```

With parent page:

```bash
echo '{
  "space_id": "123456",
  "title": "Child Page",
  "body": "<p>This is a nested page.</p>",
  "parent_id": "789012"
}' | python scripts/pages/create_page.py
```

#### Example Output

```json
{
  "id": "456789",
  "status": "current",
  "title": "My New Page",
  "spaceId": "123456",
  "parentId": null,
  "authorId": "user123",
  "createdAt": "2024-01-15T10:30:00.000Z",
  "version": {
    "number": 1,
    "authorId": "user123",
    "createdAt": "2024-01-15T10:30:00.000Z"
  },
  "_links": {
    "webui": "/spaces/MYSPACE/pages/456789/My+New+Page"
  }
}
```

---

### Get Page

**Script:** `scripts/pages/get_page.py`

Retrieves a page by its ID.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to retrieve |
| include_body | boolean | No | true | Whether to include the page body content |
| body_format | string | No | "storage" | Body format: "storage", "atlas_doc_format", or "view" |

#### Example Usage

```bash
echo '{"page_id": "456789"}' | python scripts/pages/get_page.py
```

With options:

```bash
echo '{
  "page_id": "456789",
  "include_body": true,
  "body_format": "storage"
}' | python scripts/pages/get_page.py
```

#### Example Output

```json
{
  "id": "456789",
  "status": "current",
  "title": "My New Page",
  "spaceId": "123456",
  "parentId": null,
  "authorId": "user123",
  "createdAt": "2024-01-15T10:30:00.000Z",
  "version": {
    "number": 1,
    "authorId": "user123",
    "createdAt": "2024-01-15T10:30:00.000Z"
  },
  "body": {
    "storage": {
      "value": "<p>This is the page content.</p>",
      "representation": "storage"
    }
  },
  "_links": {
    "webui": "/spaces/MYSPACE/pages/456789/My+New+Page"
  }
}
```

---

### Update Page

**Script:** `scripts/pages/update_page.py`

Updates an existing page. Requires the current version number to prevent conflicts.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to update |
| title | string | Yes | - | The new title of the page |
| body | string | Yes | - | The new page content in storage format |
| version_number | integer | Yes | - | The current version number (for optimistic locking) |

#### Example Usage

```bash
echo '{
  "page_id": "456789",
  "title": "Updated Page Title",
  "body": "<p>Updated content here.</p>",
  "version_number": 1
}' | python scripts/pages/update_page.py
```

#### Example Output

```json
{
  "id": "456789",
  "status": "current",
  "title": "Updated Page Title",
  "spaceId": "123456",
  "parentId": null,
  "authorId": "user123",
  "createdAt": "2024-01-15T10:30:00.000Z",
  "version": {
    "number": 2,
    "authorId": "user456",
    "createdAt": "2024-01-15T11:45:00.000Z"
  },
  "_links": {
    "webui": "/spaces/MYSPACE/pages/456789/Updated+Page+Title"
  }
}
```

**Note:** The version_number must match the current version of the page. If someone else has modified the page since you retrieved it, the update will fail with a conflict error. Retrieve the page again to get the latest version number.

---

### Delete Page

**Script:** `scripts/pages/delete_page.py`

Deletes a page. By default, moves the page to trash. Use purge to permanently delete.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to delete |
| purge | boolean | No | false | If true, permanently delete instead of moving to trash |

#### Example Usage

Move to trash:

```bash
echo '{"page_id": "456789"}' | python scripts/pages/delete_page.py
```

Permanently delete:

```bash
echo '{
  "page_id": "456789",
  "purge": true
}' | python scripts/pages/delete_page.py
```

#### Example Output

```json
{
  "success": true,
  "page_id": "456789",
  "purged": false
}
```

---

### List Pages

**Script:** `scripts/pages/list_pages.py`

Lists pages with optional filters. Supports pagination.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| space_id | string | No | - | Filter pages by space ID |
| title | string | No | - | Filter pages by exact title match |
| status | string | No | - | Filter by status: "current", "trashed", "draft" |
| limit | integer | No | 25 | Maximum number of results (1-250) |
| cursor | string | No | - | Pagination cursor from previous response |

#### Example Usage

List all pages in a space:

```bash
echo '{"space_id": "123456"}' | python scripts/pages/list_pages.py
```

List with filters:

```bash
echo '{
  "space_id": "123456",
  "status": "current",
  "limit": 50
}' | python scripts/pages/list_pages.py
```

Paginate results:

```bash
echo '{
  "space_id": "123456",
  "cursor": "eyJpZCI6IjEyMzQ1NiJ9"
}' | python scripts/pages/list_pages.py
```

#### Example Output

```json
{
  "results": [
    {
      "id": "456789",
      "status": "current",
      "title": "Page One",
      "spaceId": "123456",
      "parentId": null,
      "authorId": "user123",
      "createdAt": "2024-01-15T10:30:00.000Z",
      "version": {
        "number": 1,
        "authorId": "user123",
        "createdAt": "2024-01-15T10:30:00.000Z"
      }
    },
    {
      "id": "456790",
      "status": "current",
      "title": "Page Two",
      "spaceId": "123456",
      "parentId": "456789",
      "authorId": "user123",
      "createdAt": "2024-01-15T11:00:00.000Z",
      "version": {
        "number": 3,
        "authorId": "user456",
        "createdAt": "2024-01-16T09:15:00.000Z"
      }
    }
  ],
  "_links": {
    "next": "/wiki/api/v2/pages?cursor=eyJpZCI6IjQ1Njc5MCJ9"
  }
}
```

**Note:** The `_links.next` field contains the cursor for the next page of results. Extract the cursor parameter and pass it in subsequent requests to paginate.

---

## Storage Format Reference

Confluence uses a storage format based on XHTML. Common elements:

```xml
<!-- Paragraphs -->
<p>Regular paragraph text.</p>

<!-- Headings -->
<h1>Heading 1</h1>
<h2>Heading 2</h2>

<!-- Lists -->
<ul>
  <li>Unordered item</li>
</ul>
<ol>
  <li>Ordered item</li>
</ol>

<!-- Links -->
<a href="https://example.com">External link</a>

<!-- Bold and italic -->
<strong>Bold text</strong>
<em>Italic text</em>

<!-- Code blocks -->
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">python</ac:parameter>
  <ac:plain-text-body><![CDATA[print("Hello")]]></ac:plain-text-body>
</ac:structured-macro>

<!-- Info panel -->
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>Information message</p></ac:rich-text-body>
</ac:structured-macro>
```

## Error Handling

All scripts exit with code 1 on errors and print error details to stderr:

- **Invalid JSON input:** The input could not be parsed as JSON
- **Missing required parameters:** Required fields are not provided
- **API errors:** HTTP errors from Confluence (404 not found, 403 forbidden, etc.)
- **Authentication errors:** Invalid credentials or missing environment configuration

Example error output:

```
Error: Missing required parameters: ['space_id', 'title']
```

```
Error: API request failed: 404 Not Found - Page not found
```

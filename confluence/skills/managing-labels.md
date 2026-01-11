# Managing Confluence Labels

This guide covers operations for managing labels on Confluence pages using the provided scripts.

## Overview

Confluence labels are keywords or tags that help organize and categorize content. Labels make it easier to find related pages and enable content filtering through CQL queries. Each page can have multiple labels, and the same label can be applied to many pages.

## Scripts

All scripts read JSON input from stdin and output JSON results to stdout. Errors are written to stderr with a non-zero exit code.

### Add Label

**Script:** `scripts/labels/add_label.py`

Adds a label to a Confluence page.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to label |
| label | string | Yes | - | The label text to add (lowercase, no spaces) |

#### Example Usage

```bash
echo '{
  "page_id": "456789",
  "label": "reviewed"
}' | python scripts/labels/add_label.py
```

Add a multi-word label (use hyphens):

```bash
echo '{
  "page_id": "456789",
  "label": "needs-update"
}' | python scripts/labels/add_label.py
```

#### Example Output

```json
{
  "id": "label-123456",
  "name": "reviewed",
  "prefix": ""
}
```

**Note:** Labels are automatically converted to lowercase. Spaces are not allowed in label names; use hyphens or underscores instead.

---

### Get Labels

**Script:** `scripts/labels/get_labels.py`

Retrieves all labels on a page with pagination support.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to get labels from |
| limit | integer | No | 25 | Maximum number of results (1-250) |
| cursor | string | No | - | Pagination cursor from previous response |

#### Example Usage

Get labels with default limit:

```bash
echo '{"page_id": "456789"}' | python scripts/labels/get_labels.py
```

Get more labels:

```bash
echo '{
  "page_id": "456789",
  "limit": 100
}' | python scripts/labels/get_labels.py
```

Paginate results:

```bash
echo '{
  "page_id": "456789",
  "cursor": "eyJpZCI6IjEyMzQ1NiJ9"
}' | python scripts/labels/get_labels.py
```

#### Example Output

```json
{
  "results": [
    {
      "id": "label-123456",
      "name": "reviewed",
      "prefix": ""
    },
    {
      "id": "label-123457",
      "name": "documentation",
      "prefix": ""
    },
    {
      "id": "label-123458",
      "name": "api-reference",
      "prefix": ""
    }
  ],
  "_links": {
    "next": "/wiki/api/v2/pages/456789/labels?cursor=eyJpZCI6ImxhYmVsLTEyMzQ1OCJ9"
  }
}
```

**Note:** The `_links.next` field contains the cursor for the next page of results. Extract the cursor parameter and pass it in subsequent requests to paginate.

---

### Remove Label

**Script:** `scripts/labels/remove_label.py`

Removes a label from a page.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to remove the label from |
| label_id | string | Yes | - | The ID of the label to remove (from get_labels response) |

#### Example Usage

```bash
echo '{
  "page_id": "456789",
  "label_id": "label-123456"
}' | python scripts/labels/remove_label.py
```

#### Example Output

```json
{
  "success": true,
  "page_id": "456789",
  "label_id": "label-123456"
}
```

---

## Label Best Practices

1. **Use consistent naming:** Establish naming conventions for your team (e.g., `status-draft`, `team-engineering`)
2. **Keep labels lowercase:** Labels are case-insensitive and stored in lowercase
3. **Avoid spaces:** Use hyphens or underscores for multi-word labels
4. **Use prefixes for categories:** Group related labels with prefixes (e.g., `project-alpha`, `project-beta`)
5. **Limit label count:** Too many labels reduce their effectiveness; aim for 3-7 meaningful labels per page

## Searching by Label

Labels are searchable using CQL. See the [Searching Content](searching-content.md) guide for details.

Example CQL queries:

```
label=reviewed
label=documentation AND space=DEV
label IN (reviewed, published)
```

## Label Permissions

- **Adding labels:** Requires "Edit" permission on the page
- **Removing labels:** Requires "Edit" permission on the page
- **Viewing labels:** Requires "View" permission on the page

## Error Handling

All scripts exit with code 1 on errors and print error details to stderr:

- **Invalid JSON input:** The input could not be parsed as JSON
- **Missing required parameters:** Required fields are not provided
- **API errors:** HTTP errors from Confluence (404 not found, 403 forbidden, etc.)
- **Authentication errors:** Invalid credentials or missing environment configuration

Example error output:

```
Error: Missing required parameters: ['page_id', 'label']
```

```
Error: API request failed: 403 Forbidden - You do not have permission to edit this page
```

```
Error: API request failed: 404 Not Found - Page not found
```

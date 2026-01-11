# Searching Confluence Content

This guide covers searching Confluence content using CQL (Confluence Query Language).

## Overview

CQL (Confluence Query Language) is a powerful query language for searching Confluence content. It allows you to find pages, blog posts, comments, and attachments based on various criteria like content type, space, labels, creation date, and more.

## Scripts

All scripts read JSON input from stdin and output JSON results to stdout. Errors are written to stderr with a non-zero exit code.

### Search Content

**Script:** `scripts/search/search_content.py`

Searches Confluence content using a CQL query.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | CQL query string |
| limit | integer | No | 25 | Maximum number of results (1-250) |
| cursor | string | No | - | Pagination cursor from previous response |

#### Example Usage

Simple search:

```bash
echo '{"query": "type=page"}' | python scripts/search/search_content.py
```

Search with limit:

```bash
echo '{
  "query": "text ~ \"kubernetes\" AND space=DEV",
  "limit": 50
}' | python scripts/search/search_content.py
```

Paginate results:

```bash
echo '{
  "query": "type=page AND space=DEV",
  "cursor": "eyJpZCI6IjEyMzQ1NiJ9"
}' | python scripts/search/search_content.py
```

#### Example Output

```json
{
  "results": [
    {
      "content": {
        "id": "456789",
        "type": "page",
        "status": "current",
        "title": "Kubernetes Deployment Guide",
        "spaceId": "123456",
        "_links": {
          "webui": "/spaces/DEV/pages/456789/Kubernetes+Deployment+Guide"
        }
      },
      "excerpt": "This guide covers <strong>Kubernetes</strong> deployment strategies..."
    },
    {
      "content": {
        "id": "456790",
        "type": "page",
        "status": "current",
        "title": "Container Orchestration",
        "spaceId": "123456",
        "_links": {
          "webui": "/spaces/DEV/pages/456790/Container+Orchestration"
        }
      },
      "excerpt": "Using <strong>Kubernetes</strong> for container orchestration..."
    }
  ],
  "_links": {
    "next": "/wiki/api/v2/content/search?cql=text+~+%22kubernetes%22&cursor=eyJpZCI6IjQ1Njc5MCJ9"
  }
}
```

---

## CQL Syntax Reference

### Basic Structure

CQL queries consist of fields, operators, and values:

```
field operator value
```

Multiple conditions can be combined:

```
field1 operator1 value1 AND field2 operator2 value2
field1 operator1 value1 OR field2 operator2 value2
```

### Available Fields

| Field | Description | Supported Operators |
|-------|-------------|---------------------|
| type | Content type (page, blogpost, comment, attachment) | =, !=, IN |
| space | Space KEY (e.g., DEV, HR) - NOT space name | =, !=, IN |
| title | Page or content title | =, !=, ~, !~ |
| text | Full-text content search | ~ (contains), !~ (not contains) |
| label | Content labels | =, !=, IN |
| creator | User who created the content | =, !=, IN |
| created | Creation date | =, !=, >, >=, <, <= |
| lastmodified | Last modification date | =, !=, >, >=, <, <= |
| ancestor | Parent page ID (includes nested children) | =, !=, IN |
| parent | Direct parent page ID | =, !=, IN |

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| = | Exact match | `type=page` |
| != | Not equal | `space!=ARCHIVE` |
| ~ | Contains (text search) | `text ~ "kubernetes"` |
| !~ | Does not contain | `text !~ "deprecated"` |
| IN | Match any in list | `label IN (reviewed, published)` |
| AND | Both conditions must match | `type=page AND space=DEV` |
| OR | Either condition can match | `space=DEV OR space=QA` |
| >, >=, <, <= | Date/number comparisons | `created >= 2024-01-01` |

### Date Formats

Dates can be specified in these formats:

- `yyyy-MM-dd` (e.g., `2024-01-15`)
- `yyyy/MM/dd` (e.g., `2024/01/15`)

### Built-in Functions

| Function | Description | Example |
|----------|-------------|---------|
| currentUser() | The logged-in user | `creator=currentUser()` |
| startOfDay() | Beginning of today | `created >= startOfDay()` |
| endOfDay() | End of today | `created <= endOfDay()` |
| startOfWeek() | Beginning of current week | `lastmodified >= startOfWeek()` |
| endOfWeek() | End of current week | `lastmodified <= endOfWeek()` |
| startOfMonth() | Beginning of current month | `created >= startOfMonth()` |
| endOfMonth() | End of current month | `created <= endOfMonth()` |
| startOfYear() | Beginning of current year | `created >= startOfYear()` |
| endOfYear() | End of current year | `created <= endOfYear()` |

---

## Common Query Patterns

### Find Pages in a Space

```cql
type=page AND space=DEV
```

### Full-Text Search

```cql
text ~ "error handling"
```

### Search by Title

```cql
title ~ "API Guide"
```

### Find Labeled Content

```cql
label=reviewed
label IN (reviewed, published, approved)
```

### Find Content by Creator

```cql
creator=currentUser()
creator="john.doe@example.com"
```

### Find Recently Created Content

```cql
created >= 2024-01-01
created >= startOfWeek()
```

### Find Recently Modified Content

```cql
lastmodified >= startOfDay()
lastmodified >= 2024-01-01 AND lastmodified <= 2024-01-31
```

### Combine Multiple Conditions

```cql
type=page AND space=DEV AND label=reviewed
text ~ "kubernetes" AND space IN (DEV, OPS) AND created >= 2024-01-01
type=page AND (label=draft OR label=review-needed)
```

### Find Child Pages

```cql
ancestor=456789
parent=456789
```

### Find All Content Types

```cql
type IN (page, blogpost, comment, attachment)
```

### Exclude Specific Content

```cql
type=page AND space!=ARCHIVE
text ~ "api" AND label!=deprecated
```

---

## Important Notes

### Space Keys vs Space Names

**CRITICAL:** The `space` field uses the space KEY (e.g., "DEV", "HR"), NOT the space name or title.

**Correct:**
```cql
space=DEV
space IN (DEV, QA, PROD)
```

**INCORRECT (will cause errors):**
```cql
space="Development Team"
space.title="Development Team"
space.name="Development"
```

### Text Search Requires Quotes

When searching for phrases or text containing spaces, use quotes:

```cql
text ~ "error handling"
title ~ "API Reference Guide"
```

### Case Sensitivity

- CQL keywords (AND, OR, IN) are case-insensitive
- Field names are case-insensitive
- Values are generally case-insensitive for text searches

---

## Error Handling

All scripts exit with code 1 on errors and print error details to stderr:

- **Invalid JSON input:** The input could not be parsed as JSON
- **Missing required parameters:** Required fields are not provided
- **Invalid CQL syntax:** The query string contains syntax errors
- **API errors:** HTTP errors from Confluence (400 bad request, 403 forbidden, etc.)

Example error output:

```
Error: Missing required parameters: ['query']
```

```
Error: API request failed: 400 Bad Request - Invalid CQL query syntax
```

```
Error: API request failed: 400 Bad Request - Unknown field: space.title
```

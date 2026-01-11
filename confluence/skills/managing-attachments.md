# Managing Confluence Attachments

This guide covers operations for managing attachments on Confluence pages using the provided scripts.

## Overview

Confluence attachments are files uploaded to pages, such as images, documents, PDFs, and other media. Attachments can be embedded in page content or downloaded by users. Each attachment maintains version history when updated.

## Scripts

All scripts read JSON input from stdin and output JSON results to stdout. Errors are written to stderr with a non-zero exit code.

### Get Attachments

**Script:** `scripts/attachments/get_attachments.py`

Retrieves all attachments on a page with pagination support.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_id | string | Yes | - | The ID of the page to get attachments from |
| limit | integer | No | 25 | Maximum number of results (1-250) |
| cursor | string | No | - | Pagination cursor from previous response |

#### Example Usage

Get attachments with default limit:

```bash
echo '{"page_id": "456789"}' | python scripts/attachments/get_attachments.py
```

Get more attachments:

```bash
echo '{
  "page_id": "456789",
  "limit": 100
}' | python scripts/attachments/get_attachments.py
```

Paginate results:

```bash
echo '{
  "page_id": "456789",
  "cursor": "eyJpZCI6IjEyMzQ1NiJ9"
}' | python scripts/attachments/get_attachments.py
```

#### Example Output

```json
{
  "results": [
    {
      "id": "att123456",
      "status": "current",
      "title": "architecture-diagram.png",
      "mediaType": "image/png",
      "mediaTypeDescription": "PNG Image",
      "comment": "Updated system architecture",
      "fileSize": 245678,
      "webuiLink": "/pages/viewpageattachments.action?pageId=456789",
      "downloadLink": "/wiki/download/attachments/456789/architecture-diagram.png",
      "version": {
        "number": 2,
        "authorId": "user123",
        "createdAt": "2024-01-15T10:30:00.000Z"
      }
    },
    {
      "id": "att123457",
      "status": "current",
      "title": "requirements.pdf",
      "mediaType": "application/pdf",
      "mediaTypeDescription": "PDF Document",
      "comment": "Project requirements v1.0",
      "fileSize": 1234567,
      "webuiLink": "/pages/viewpageattachments.action?pageId=456789",
      "downloadLink": "/wiki/download/attachments/456789/requirements.pdf",
      "version": {
        "number": 1,
        "authorId": "user456",
        "createdAt": "2024-01-14T09:00:00.000Z"
      }
    }
  ],
  "_links": {
    "next": "/wiki/api/v2/pages/456789/attachments?cursor=eyJpZCI6ImF0dDEyMzQ1NyJ9"
  }
}
```

**Note:** The `_links.next` field contains the cursor for the next page of results. Extract the cursor parameter and pass it in subsequent requests to paginate.

---

### Delete Attachment

**Script:** `scripts/attachments/delete_attachment.py`

Deletes an attachment from Confluence.

#### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| attachment_id | string | Yes | - | The ID of the attachment to delete |
| purge | boolean | No | false | If true, permanently delete instead of moving to trash |

#### Example Usage

Move to trash (can be restored):

```bash
echo '{"attachment_id": "att123456"}' | python scripts/attachments/delete_attachment.py
```

Permanently delete:

```bash
echo '{
  "attachment_id": "att123456",
  "purge": true
}' | python scripts/attachments/delete_attachment.py
```

#### Example Output

```json
{
  "success": true,
  "attachment_id": "att123456",
  "purged": false
}
```

---

## Attachment Information

### Common Media Types

| Extension | Media Type | Description |
|-----------|------------|-------------|
| .png | image/png | PNG Image |
| .jpg, .jpeg | image/jpeg | JPEG Image |
| .gif | image/gif | GIF Image |
| .pdf | application/pdf | PDF Document |
| .doc, .docx | application/msword | Word Document |
| .xls, .xlsx | application/vnd.ms-excel | Excel Spreadsheet |
| .ppt, .pptx | application/vnd.ms-powerpoint | PowerPoint Presentation |
| .zip | application/zip | ZIP Archive |
| .txt | text/plain | Plain Text |

### File Size Limits

Confluence has configurable attachment size limits. The default maximum file size is typically:
- Cloud: 250 MB per file
- Data Center/Server: Configurable by administrator

### Attachment Versioning

When uploading a file with the same name as an existing attachment:
- A new version is created
- Previous versions are preserved
- Version history can be viewed in the Confluence UI

---

## Embedding Attachments in Pages

Attachments can be referenced in page content using Confluence storage format:

### Images

```xml
<ac:image>
  <ri:attachment ri:filename="architecture-diagram.png"/>
</ac:image>
```

With size constraints:

```xml
<ac:image ac:width="600">
  <ri:attachment ri:filename="architecture-diagram.png"/>
</ac:image>
```

### File Links

```xml
<ac:link>
  <ri:attachment ri:filename="requirements.pdf"/>
  <ac:plain-text-link-body><![CDATA[Download Requirements]]></ac:plain-text-link-body>
</ac:link>
```

---

## Attachment Permissions

- **Viewing attachments:** Requires "View" permission on the page
- **Uploading attachments:** Requires "Add Attachments" permission
- **Deleting attachments:** Requires "Remove Attachments" permission or space admin rights

---

## Searching Attachments

Attachments can be found using CQL. See the [Searching Content](searching-content.md) guide for details.

Example CQL queries:

```cql
type=attachment AND space=DEV
type=attachment AND title ~ ".pdf"
type=attachment AND ancestor=456789
```

---

## Error Handling

All scripts exit with code 1 on errors and print error details to stderr:

- **Invalid JSON input:** The input could not be parsed as JSON
- **Missing required parameters:** Required fields are not provided
- **API errors:** HTTP errors from Confluence (404 not found, 403 forbidden, etc.)
- **Authentication errors:** Invalid credentials or missing environment configuration

Example error output:

```
Error: Missing required parameters: ['page_id']
```

```
Error: API request failed: 403 Forbidden - You do not have permission to delete attachments
```

```
Error: API request failed: 404 Not Found - Attachment not found
```

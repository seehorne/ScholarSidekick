# ScholarSidekick API Reference

Complete API documentation for the ScholarSidekick backend.

## Base URL

```
http://localhost:5001
```

## Response Format

All endpoints return JSON responses. Successful responses return relevant data with HTTP 200 status. Errors return appropriate HTTP status codes with error details.

## Endpoints

### System

#### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### Welcome
```
GET /
```

**Response:**
```json
{
  "message": "Welcome to ScholarSidekick API",
  "version": "1.0.0"
}
```

---

## Google Docs Integration

### Get Authorization URL

Get the Google OAuth2 authorization URL to start the authentication flow.

```
GET /api/google/auth/url
```

**Query Parameters:**
- `redirect_uri` (optional): Custom redirect URI

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "random_state_string"
}
```

### OAuth Callback

Handles the OAuth2 callback after user authorization.

```
GET /api/google/auth/callback?code=xxx&state=xxx
```

This endpoint is automatically called by Google after user authorization.

**Response:**
```json
{
  "message": "Successfully authenticated with Google",
  "token_received": true
}
```

### Check Authentication Status

```
GET /api/google/auth/status
```

**Response:**
```json
{
  "authenticated": true,
  "has_token": true
}
```

### Logout

Clear Google authentication session.

```
POST /api/google/auth/logout
```

**Response:**
```json
{
  "message": "Successfully logged out from Google"
}
```

### Fetch Document by ID

```
GET /api/google/document/<document_id>
```

**Query Parameters:**
- `token` (optional): Access token if not using session

**Response:**
```json
{
  "document_id": "ABC123XYZ",
  "title": "Meeting Notes",
  "content": "Full document text...",
  "metadata": {
    "title": "Meeting Notes",
    "document_id": "ABC123XYZ",
    "revision_id": "123"
  }
}
```

### Fetch Document from URL

```
POST /api/google/document/from-url
```

**Request Body:**
```json
{
  "url": "https://docs.google.com/document/d/ABC123.../edit",
  "token_info": {
    "token": "optional_if_using_session"
  }
}
```

**Response:**
```json
{
  "document_id": "ABC123XYZ",
  "title": "Meeting Notes",
  "content": "Full document text...",
  "metadata": {...}
}
```

---

## Meetings API

### Create Meeting

Create a new meeting with transcript and extract cards.

**Now supports Google Docs integration!**

```
POST /api/meetings/
```

**Option 1: Direct Transcript**
```json
{
  "title": "Weekly 1:1 - Alice & Bob",
  "description": "Optional description",
  "transcript": "Alice: How is the project? Bob: Going well!",
  "agenda_items": ["Project status", "Q4 planning"],
  "meeting_date": "2025-11-26T10:00:00",
  "requested_card_types": ["tldr", "todo", "action_item"]
}
```

**Option 2: Google Docs URL** (requires authentication)
```json
{
  "google_doc_url": "https://docs.google.com/document/d/ABC123.../edit",
  "agenda_items": ["Project status", "Q4 planning"],
  "meeting_date": "2025-11-27T10:00:00",
  "requested_card_types": ["tldr", "todo"]
}
```

**Option 3: Google Docs ID** (requires authentication)
```json
{
  "google_doc_id": "ABC123XYZ",
  "title": "Optional - will use doc title if not provided",
  "meeting_date": "2025-11-27T10:00:00"
}
```

**Option 4: With Token Info** (for API usage without session)
```json
{
  "google_doc_url": "https://docs.google.com/document/d/ABC123.../edit",
  "token_info": {
    "token": "ya29.xxx",
    "refresh_token": "xxx",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "xxx",
    "client_secret": "xxx"
  },
  "meeting_date": "2025-11-27T10:00:00"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Weekly 1:1 - Alice & Bob",
  "description": "Optional description",
  "transcript": "Alice: How is the project? Bob: Going well!",
  "agenda_items": ["Project status", "Q4 planning"],
  "uncovered_agenda_items": [],
  "meeting_date": "2025-11-26T10:00:00",
  "created_at": "2025-11-26T10:05:00",
  "updated_at": "2025-11-26T10:05:00",
  "cards": [...],
  "canvases": [...]
}
```

### List Meetings

```
GET /api/meetings/
```

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Weekly 1:1",
    "description": null,
    "meeting_date": "2025-11-26T10:00:00",
    "created_at": "2025-11-26T10:05:00",
    ...
  }
]
```

### Get Meeting

```
GET /api/meetings/{meeting_id}
```

**Response:** Meeting object with all cards and canvases

### Update Meeting

```
PUT /api/meetings/{meeting_id}
```

**Request Body:** Partial meeting object with fields to update

### Delete Meeting

```
DELETE /api/meetings/{meeting_id}
```

**Response:**
```json
{
  "message": "Meeting deleted successfully"
}
```

### Re-extract Cards

Re-run card extraction with different card types.

```
POST /api/meetings/{meeting_id}/reextract
```

**Request Body:**
```json
{
  "requested_card_types": ["tldr", "todo", "decision"]
}
```

---

## Cards API

### Create Card

Create a manual card.

```
POST /api/cards/
```

**Request Body:**
```json
{
  "meeting_id": 1,
  "canvas_id": 1,
  "card_type": "todo",
  "title": "Complete documentation",
  "content": "Write API documentation for all endpoints",
  "status": "draft",
  "assigned_to": "Alice",
  "due_date": "2025-12-01T00:00:00",
  "position_x": 100,
  "position_y": 200,
  "tags": ["documentation", "api"]
}
```

**Card Types:**
- `tldr` - Meeting summary
- `todo` - To-do item
- `action_item` - Action item with owner
- `decision` - Decision made
- `question` - Open question
- `discussion_point` - Discussion topic
- `follow_up` - Follow-up item
- `custom` - Custom type

**Card Status:**
- `draft` - Initial state
- `active` - In progress
- `completed` - Finished
- `archived` - Archived

### List Cards

```
GET /api/cards/
```

**Query Parameters:**
- `meeting_id` (optional): Filter by meeting
- `canvas_id` (optional): Filter by canvas
- `skip` (optional): Records to skip
- `limit` (optional): Max records (default: 100)

### Get Card

Get card with updates and child cards.

```
GET /api/cards/{card_id}
```

**Response:**
```json
{
  "id": 1,
  "card_type": "todo",
  "title": "Complete documentation",
  "content": "Write API docs",
  "status": "active",
  "updates": [...],
  "child_cards": [...]
}
```

### Update Card

```
PUT /api/cards/{card_id}
```

**Request Body:** Partial card object with fields to update

### Delete Card

```
DELETE /api/cards/{card_id}
```

### Add Card Update

Add an update or ping to a card.

```
POST /api/cards/{card_id}/updates
```

**Request Body:**
```json
{
  "author": "Alice",
  "content": "Updated the documentation",
  "is_ping": true,
  "pinged_user": "Bob"
}
```

### Get Card Updates

```
GET /api/cards/{card_id}/updates
```

### Batch Update Positions

Update positions of multiple cards at once.

```
POST /api/cards/batch-update-positions
```

**Request Body:**
```json
{
  "updates": [
    {
      "card_id": 1,
      "position_x": 150,
      "position_y": 250
    },
    {
      "card_id": 2,
      "position_x": 300,
      "position_y": 100
    }
  ]
}
```

---

## Canvas API

### Create Canvas

```
POST /api/canvas/
```

**Request Body:**
```json
{
  "meeting_id": 1,
  "title": "Main Canvas",
  "description": "Primary workspace for meeting cards"
}
```

### List Canvases

```
GET /api/canvas/
```

**Query Parameters:**
- `meeting_id` (optional): Filter by meeting

### Get Canvas

Get canvas with all cards.

```
GET /api/canvas/{canvas_id}
```

**Response:**
```json
{
  "id": 1,
  "meeting_id": 1,
  "title": "Main Canvas",
  "description": "Primary workspace",
  "created_at": "2025-11-26T10:05:00",
  "updated_at": "2025-11-26T10:05:00",
  "cards": [...]
}
```

### Update Canvas

```
PUT /api/canvas/{canvas_id}
```

**Request Body:** Partial canvas object

### Delete Canvas

```
DELETE /api/canvas/{canvas_id}
```

---

## Error Responses

### 404 Not Found
```json
{
  "error": "Meeting not found"
}
```

### 400 Bad Request
```json
{
  "error": "Validation error message"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Examples

### Complete Workflow

```bash
# 1. Create a meeting
curl -X POST http://localhost:5001/api/meetings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sprint Planning",
    "transcript": "Team discussed upcoming features...",
    "agenda_items": ["Feature A", "Feature B"],
    "meeting_date": "2025-11-26T10:00:00",
    "requested_card_types": ["tldr", "todo", "action_item"]
  }'

# 2. List all cards from the meeting
curl http://localhost:5001/api/cards/?meeting_id=1

# 3. Update a card status
curl -X PUT http://localhost:5001/api/cards/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# 4. Add a ping to a card
curl -X POST http://localhost:5001/api/cards/1/updates \
  -H "Content-Type: application/json" \
  -d '{
    "author": "Alice",
    "content": "Task completed!",
    "is_ping": true,
    "pinged_user": "Bob"
  }'
```

---

## Rate Limits

Currently no rate limits are enforced.

## Authentication

Currently no authentication is required. This is planned for future releases.

## Versioning

Current version: **1.0.0**

API version is included in the root endpoint response.

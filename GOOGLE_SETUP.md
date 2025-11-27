# Google Docs Integration Setup Guide

This guide explains how to set up Google Docs integration for ScholarSidekick.

## Overview

Users can now provide meeting transcripts directly from Google Docs by:
1. Authenticating with their Google account
2. Providing a Google Docs URL or document ID
3. The system automatically fetches the document content

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 2. Enable Required APIs

1. In your Google Cloud project, go to **APIs & Services** > **Library**
2. Enable the following APIs:
   - **Google Docs API**
   - **Google Drive API** (for file access)

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External** (for testing) or **Internal** (for organization)
   - App name: **ScholarSidekick**
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add the following scopes:
     - `https://www.googleapis.com/auth/documents.readonly`
     - `https://www.googleapis.com/auth/drive.readonly`
   - Test users: Add your email (for testing)

4. Create OAuth client ID:
   - Application type: **Web application**
   - Name: **ScholarSidekick Backend**
   - Authorized redirect URIs:
     - `http://localhost:5001/api/google/auth/callback` (development)
     - Add your production URL when deploying

5. Click **Create**

6. Download the JSON file (it will be named something like `client_secret_xxx.json`)

### 4. Configure Your Application

**Option A: Using the JSON file (Recommended for Development)**

1. Rename the downloaded file to `client_secrets.json`
2. Place it in the root directory of ScholarSidekick:
   ```
   ScholarSidekick/
   ├── client_secrets.json  <-- Here
   ├── app/
   ├── run.py
   └── ...
   ```
3. The `.env` file already points to this: `GOOGLE_CLIENT_SECRETS_FILE=client_secrets.json`

**Option B: Using Environment Variable (Recommended for Production)**

1. Open the downloaded JSON file and copy its contents
2. Set the environment variable:
   ```bash
   export GOOGLE_CLIENT_CONFIG='{"web":{"client_id":"...","client_secret":"..."}}'
   ```
3. Or add to your `.env` file:
   ```
   GOOGLE_CLIENT_CONFIG={"web":{"client_id":"YOUR_ID","client_secret":"YOUR_SECRET",...}}
   ```

### 5. Add to .gitignore

Make sure `client_secrets.json` is in your `.gitignore`:

```
# Google OAuth credentials
client_secrets.json
```

## Usage

### Authentication Flow

#### 1. Get Authorization URL

```bash
curl http://localhost:5001/api/google/auth/url
```

Response:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "random_state_string"
}
```

#### 2. Redirect User to Authorization URL

The user visits the `authorization_url` and grants permissions.

#### 3. Handle Callback

After authorization, Google redirects to:
```
http://localhost:5001/api/google/auth/callback?code=xxx&state=xxx
```

This endpoint automatically exchanges the code for an access token and stores it in the session.

### Using Google Docs with Meetings

#### Option 1: Create Meeting with Google Docs URL

```bash
curl -X POST http://localhost:5001/api/meetings/ \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "title": "Weekly Team Meeting",
    "google_doc_url": "https://docs.google.com/document/d/ABC123.../edit",
    "agenda_items": ["Status updates", "Planning"],
    "meeting_date": "2025-11-27T10:00:00",
    "requested_card_types": ["tldr", "todo", "action_item"]
  }'
```

#### Option 2: Create Meeting with Document ID

```bash
curl -X POST http://localhost:5001/api/meetings/ \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "google_doc_id": "ABC123XYZ456",
    "agenda_items": ["Status updates"],
    "meeting_date": "2025-11-27T10:00:00"
  }'
```

Note: If no title is provided, the Google Doc's title will be used automatically.

#### Option 3: Pass Token Directly (API Usage)

```bash
curl -X POST http://localhost:5001/api/meetings/ \
  -H "Content-Type: application/json" \
  -d '{
    "google_doc_url": "https://docs.google.com/document/d/ABC123.../edit",
    "token_info": {
      "token": "ya29.xxx",
      "refresh_token": "xxx",
      "token_uri": "https://oauth2.googleapis.com/token",
      "client_id": "xxx",
      "client_secret": "xxx"
    },
    "meeting_date": "2025-11-27T10:00:00"
  }'
```

### Fetch Document Directly

```bash
# Get document by ID
curl http://localhost:5001/api/google/document/ABC123XYZ \
  -H "Cookie: session=YOUR_SESSION_COOKIE"

# Get document from URL
curl -X POST http://localhost:5001/api/google/document/from-url \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "url": "https://docs.google.com/document/d/ABC123.../edit"
  }'
```

### Check Authentication Status

```bash
curl http://localhost:5001/api/google/auth/status \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### Logout

```bash
curl -X POST http://localhost:5001/api/google/auth/logout \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

## API Endpoints

### Google Authentication

- `GET /api/google/auth/url` - Get OAuth authorization URL
- `GET /api/google/auth/callback` - OAuth callback (handles redirect)
- `GET /api/google/auth/status` - Check authentication status
- `POST /api/google/auth/logout` - Clear session

### Google Documents

- `GET /api/google/document/<document_id>` - Fetch document by ID
- `POST /api/google/document/from-url` - Fetch document from URL

### Enhanced Meetings Endpoint

`POST /api/meetings/` now accepts:
- `transcript` (string) - Direct transcript text
- `google_doc_url` (string) - Google Docs URL
- `google_doc_id` (string) - Document ID
- `token_info` (object) - Optional token for API usage

If `google_doc_url` or `google_doc_id` is provided, the system will:
1. Check for authentication
2. Fetch the document content
3. Use it as the transcript
4. Optionally use the document title if no title provided

## Security Notes

### Development
- Sessions are stored in Flask sessions (cookie-based)
- `SECRET_KEY` should be changed from default
- HTTP cookies are acceptable for localhost

### Production
- Store tokens in database with encryption
- Use HTTPS only (`SESSION_COOKIE_SECURE=True`)
- Use a strong random `SECRET_KEY`
- Consider token refresh logic
- Implement proper user management
- Use database-backed sessions (Redis, etc.)

## Troubleshooting

### "Google OAuth configuration not found"
- Make sure `client_secrets.json` exists in the root directory
- OR make sure `GOOGLE_CLIENT_CONFIG` environment variable is set

### "Not authenticated"
- Complete the OAuth flow first using `/api/google/auth/url`
- Make sure you're sending the session cookie with requests

### "Invalid Google Docs URL"
- URL must be in format: `https://docs.google.com/document/d/DOCUMENT_ID/edit`
- Or just provide the `document_id` directly

### "Failed to fetch Google Doc"
- Make sure the document is accessible by the authenticated user
- Check that Google Docs API is enabled in your project
- Verify the user granted the required permissions

## Example: Complete Flow

```python
import requests

BASE_URL = "http://localhost:5001"

# 1. Get authorization URL
response = requests.get(f"{BASE_URL}/api/google/auth/url")
auth_data = response.json()
print(f"Visit: {auth_data['authorization_url']}")

# 2. User visits URL and authorizes
# Google redirects to callback, which stores token in session

# 3. Use session to create meeting with Google Doc
session = requests.Session()  # Maintains cookies
response = session.post(f"{BASE_URL}/api/meetings/", json={
    "google_doc_url": "https://docs.google.com/document/d/YOUR_DOC_ID/edit",
    "agenda_items": ["Status", "Planning"],
    "meeting_date": "2025-11-27T10:00:00",
    "requested_card_types": ["tldr", "todo"]
})

meeting = response.json()
print(f"Created meeting: {meeting['title']}")
print(f"Transcript: {meeting['transcript'][:100]}...")
```

## Testing

Install the packages:
```bash
pip install -r requirements.txt
```

Run the server:
```bash
python run.py
```

Test the Google integration:
```bash
# Check if configured
curl http://localhost:5001/api/google/auth/url

# Should return authorization URL if configured correctly
```

## Next Steps

1. Set up Google Cloud project
2. Download credentials
3. Configure application
4. Test OAuth flow
5. Create meetings from Google Docs!

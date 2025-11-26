# Quick Start Guide

## Getting Started in 3 Steps

### 1. Install Dependencies

```bash
# The virtual environment is already created and packages installed
# If you need to reinstall:
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python run.py
```

The server will start at `http://localhost:5001`

### 3. Test the API

You can test endpoints using curl, Python requests, or any HTTP client.

## Testing the API

### Option 1: Using cURL

Create a meeting:
```bash
curl -X POST "http://localhost:5001/api/meetings/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly 1:1",
    "transcript": "Alice: How is the project going? Bob: Great, I finished the feature.",
    "agenda_items": ["Project status", "Next steps"],
    "meeting_date": "2025-11-26T10:00:00",
    "requested_card_types": ["tldr", "todo"]
  }'
```

### Option 2: Using the Example Script

Install requests library:
```bash
pip install requests
```

Run the example:
```bash
python example_usage.py
```

This will demonstrate the complete workflow.

### Option 3: Using Python Requests

```python
import requests

response = requests.get('http://localhost:5001/health')
print(response.json())  # {'status': 'healthy'}
```

## API Workflow

### 1. Create a Meeting
```
POST /api/meetings/
```
- Uploads transcript and agenda
- Automatically extracts cards
- Creates a canvas
- Returns meeting with generated cards

### 2. Edit Cards
```
PUT /api/cards/{id}
GET /api/cards/{id}
```
- View and edit generated cards
- Update titles, content, status
- Assign to users, set due dates

### 3. Work on Canvas
```
GET /api/canvas/{id}
POST /api/cards/
POST /api/cards/batch-update-positions
```
- View all cards on canvas
- Add new cards
- Link cards together
- Drag and position cards

### 4. Collaborate
```
POST /api/cards/{id}/updates
GET /api/cards/{id}/updates
```
- Add updates to cards
- Ping collaborators
- Track conversation history

## Sample Workflow

1. **Upload transcript** with agenda items
2. **Review extracted cards** - TL;DR, TODOs, action items
3. **Edit cards** to refine content
4. **Add manual cards** for additional context
5. **Link cards** to show relationships
6. **Add updates** and ping team members
7. **Track progress** with status changes

## Card Types

- `tldr` - Meeting summary
- `todo` - General to-do items
- `action_item` - Specific actions with owners
- `decision` - Decisions made
- `question` - Open questions
- `discussion_point` - Important discussions
- `follow_up` - Follow-up items
- `custom` - Custom card types

## Next Steps

### Adding LLM Integration

The extraction service (`app/services/extraction_service.py`) has placeholder methods ready for LLM integration:

1. Add your API key to `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   ```

2. Update the extraction methods to use real LLM calls

3. Implement intelligent:
   - Card extraction
   - Agenda coverage analysis
   - Transcript segmentation

### Database Migration

To switch from SQLite to PostgreSQL:

1. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/scholarsidekick
   ```

2. The code will automatically work with PostgreSQL

### Adding Authentication

Add user authentication to:
- Track card ownership
- Secure pings between users
- Control access to meetings

## Troubleshooting

**Port already in use:**
```bash
# Change port in .env
API_PORT=5002
```

**Database errors:**
```bash
# Delete database and restart
rm scholarsidekick.db
python run.py
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

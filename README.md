# ScholarSidekick

A collaborative tool for turning meeting transcripts into actionable, interconnected cards on a shared canvas.

## Overview

ScholarSidekick helps teams transform their weekly one-on-one meeting transcripts into organized, collaborative workspaces. The system:

1. **Extracts** meaningful cards from meeting transcripts (TL;DR, TODOs, decisions, etc.)
2. **Organizes** cards on a collaborative canvas
3. **Enables** ongoing collaboration with updates and pings between team members

## Features

- **Transcript Processing**: Upload meeting transcripts and agenda items
- **Google Docs Integration**: Import transcripts directly from Google Docs
- **Smart Extraction**: Extract different types of cards (TL;DR, TODO, Action Items, Decisions, etc.)
- **Agenda Tracking**: Identify which agenda items were covered vs. missed
- **Collaborative Canvas**: Visual workspace for organizing and linking cards
- **Card Linking**: Create hierarchies by linking cards to each other
- **Updates & Pings**: Keep collaborators informed with updates and notifications
- **Flexible Organization**: Drag-and-drop positioning, tagging, and status tracking
- **OAuth2 Authentication**: Secure Google account integration

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: Flask-SQLAlchemy with SQLite (easily switchable to PostgreSQL)
- **Serialization**: Marshmallow schemas
- **Google Integration**: Google Docs API, OAuth2

## Quick Start

**For complete setup and running instructions, see [GETTING_STARTED.md](GETTING_STARTED.md)**

### One-Command Start

```bash
# Clone and setup
git clone <repository-url>
cd ScholarSidekick
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd tool-code && npm install && cd ..

# Start both backend and frontend
./start-dev.sh
```

Then open http://localhost:3000

### Prerequisites

- Python 3.8+ - Backend runtime
- Node.js 16+ and npm - Frontend runtime  
- Git - Version control

### Installation

- Environment configuration
- Google Docs integration setup
- Frontend setup
- Troubleshooting

**👉 See [GETTING_STARTED.md](GETTING_STARTED.md) for the complete guide**

## Documentation

Comprehensive documentation is available:

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete setup and running guide (START HERE!)
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation and examples
- **[GOOGLE_SETUP.md](GOOGLE_SETUP.md)** - Google Docs integration setup
- **[GOOGLE_INTEGRATION.md](GOOGLE_INTEGRATION.md)** - Google Docs feature overview
- **[TESTING.md](TESTING.md)** - Testing guide and results

## API Endpoints (Summary)

### Meetings

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 3 steps
- **[Setup Complete](SETUP_COMPLETE.md)** - Overview of what's been built
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Testing Guide](TESTING.md)** - Test results and testing instructions

## API Documentation

The Flask application provides a RESTful API. You can test endpoints using:
- **curl** - See examples below
- **Postman** - Import the endpoints
- **Python requests** - See `example_usage.py`

## API Endpoints

### Meetings
- `POST /api/meetings/` - Create meeting and extract cards
- `GET /api/meetings/` - List all meetings
- `GET /api/meetings/{id}` - Get meeting details
- `PUT /api/meetings/{id}` - Update meeting
- `DELETE /api/meetings/{id}` - Delete meeting
- `POST /api/meetings/{id}/reextract` - Re-extract cards with different types

### Cards
- `POST /api/cards/` - Create a new card
- `GET /api/cards/` - List cards (filterable by meeting/canvas)
- `GET /api/cards/{id}` - Get card details with updates
- `PUT /api/cards/{id}` - Update card
- `DELETE /api/cards/{id}` - Delete card
- `POST /api/cards/{id}/updates` - Add update/ping to card
- `GET /api/cards/{id}/updates` - Get card updates
- `POST /api/cards/batch-update-positions` - Update multiple card positions

### Canvas
- `POST /api/canvas/` - Create a new canvas
- `GET /api/canvas/` - List canvases
- `GET /api/canvas/{id}` - Get canvas with all cards
- `PUT /api/canvas/{id}` - Update canvas
- `DELETE /api/canvas/{id}` - Delete canvas

## Data Models

### Meeting
- Stores transcript, agenda items, and metadata
- Tracks which agenda items were not covered
- Links to cards and canvases

### Card
- Represents extracted or manually created items
- Types: TL;DR, TODO, Action Item, Decision, Question, etc.
- Supports linking (parent-child relationships)
- Tracks position on canvas
- Includes status, assignment, due dates, and tags

### Canvas
- Visual workspace for organizing cards
- Associated with a meeting
- Contains positioned cards

### Card Update
- Updates and pings on cards
- Tracks author and optional pinged user
- Maintains collaboration history

## Card Types

- **TL;DR**: High-level meeting summaries
- **TODO**: General to-do items
- **Action Item**: Specific action items with owners
- **Decision**: Decisions made during meeting
- **Question**: Open questions or clarifications needed
- **Discussion Point**: Important topics discussed
- **Follow-up**: Items requiring follow-up
- **Custom**: User-defined card types

## LLM Integration (Coming Soon)

The current implementation includes placeholder methods for:
- Card extraction from transcripts
- Agenda coverage analysis
- Transcript segment identification

These will be replaced with actual LLM API calls (OpenAI, Anthropic, etc.) to provide intelligent extraction and analysis.

## Database Schema

The application uses SQLAlchemy ORM with the following main tables:
- `meetings` - Meeting records
- `cards` - Card items
- `canvases` - Canvas workspaces
- `card_updates` - Updates and pings

## Development

### Running Tests
```bash
pytest
```

## Project Structure

```
ScholarSidekick/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flask application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Marshmallow schemas
│   ├── api/
│   │   ├── meetings.py      # Meeting endpoints
│   │   ├── cards.py         # Card endpoints
│   │   └── canvas.py        # Canvas endpoints
│   └── services/
│       └── extraction_service.py  # Card extraction logic
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## License

MIT

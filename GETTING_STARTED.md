# ScholarSidekick - Getting Started Guide

Complete guide for setting up and running ScholarSidekick (backend + frontend).

## Table of Contents
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [First Time Setup](#first-time-setup)
- [Running the Application](#running-the-application)
- [Google Docs Integration (Optional)](#google-docs-integration-optional)
- [Development Workflow](#development-workflow)
- [API Usage](#api-usage)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

**If everything is already set up:**

```bash
cd /Users/seehorn/Downloads/Development/ScholarSidekick
./start-dev.sh
```

Then open your browser to:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5001

**To stop:**
```bash
./stop-dev.sh
```

---

## Prerequisites

### Required
- **Python 3.8+** - Backend runtime
- **Node.js 16+** and **npm** - Frontend runtime
- **Git** - Version control

### Check Your Setup
```bash
# Check Python
python --version  # Should be 3.8 or higher

# Check Node.js
node --version    # Should be 16 or higher
npm --version

# Check Git
git --version
```

---

## First Time Setup

### 1. Clone the Repository (if not already done)

```bash
git clone <repository-url>
cd ScholarSidekick
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Or on Windows
.venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "from app.main import create_app; app = create_app(); print('✅ Backend ready!')"
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd tool-code

# Install Node dependencies
npm install

# Return to project root
cd ..
```

### 4. Environment Configuration

The `.env` file is already configured with defaults:

```bash
# View current configuration
cat .env
```

**Default settings:**
```env
DATABASE_URL=sqlite:///./scholarsidekick.db
API_HOST=0.0.0.0
API_PORT=5001
SECRET_KEY=dev-secret-key-change-in-production
GOOGLE_CLIENT_SECRETS_FILE=client_secrets.json
```

**For production**, update `SECRET_KEY`:
```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY=$SECRET_KEY" >> .env
```

---

## Running the Application

### Method 1: One-Command Startup (Recommended)

**Start both backend and frontend:**
```bash
./start-dev.sh
```

This script:
- ✅ Checks dependencies
- ✅ Clears ports if needed
- ✅ Starts backend (Flask) on port 5001
- ✅ Starts frontend (React/Vite) on port 3000
- ✅ Verifies both are healthy
- ✅ Shows URLs and log locations

**Stop both services:**
```bash
./stop-dev.sh
```

### Method 2: Manual (Two Terminals)

**Terminal 1 - Backend:**
```bash
cd /Users/seehorn/Downloads/Development/ScholarSidekick
source .venv/bin/activate  # Activate virtual environment
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/seehorn/Downloads/Development/ScholarSidekick/tool-code
npm run dev
```

**Stop:** Press `Ctrl+C` in each terminal

### Method 3: Backend Only

If you only need the API (no frontend):

```bash
source .venv/bin/activate
python run.py
```

API will be available at http://localhost:5001

---

## Access Points

Once running:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend UI | http://localhost:3000 | Main application interface |
| Backend API | http://localhost:5001 | RESTful API endpoints |
| Health Check | http://localhost:5001/health | Service status |
| API Docs | See [API_REFERENCE.md](API_REFERENCE.md) | Complete API documentation |

---

## Google Docs Integration (Optional)

To enable importing transcripts from Google Docs:

### 1. Setup Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Docs API** and **Google Drive API**
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URI: `http://localhost:5001/api/google/auth/callback`
6. Download credentials as `client_secrets.json`

### 2. Configure Application

```bash
# Place credentials in project root
mv ~/Downloads/client_secret_*.json client_secrets.json
```

### 3. Test Google Integration

```bash
# Start the application
./start-dev.sh

# In another terminal, test OAuth
curl http://localhost:5001/api/google/auth/url

# Run the example script
source .venv/bin/activate
python example_google_docs.py
```

**For detailed setup instructions, see [GOOGLE_SETUP.md](GOOGLE_SETUP.md)**

---

## Development Workflow

### Making Changes

**Backend (Python):**
- Edit files in `app/` directory
- Flask auto-reloads on file changes (debug mode)
- View logs: `tail -f backend.log`

**Frontend (React/TypeScript):**
- Edit files in `tool-code/` directory
- Vite provides hot module replacement (instant updates)
- View logs: `tail -f frontend.log`

### Project Structure

```
ScholarSidekick/
├── app/                      # Backend (Flask)
│   ├── api/                 # API endpoints
│   │   ├── meetings.py      # Meeting management
│   │   ├── cards.py         # Card operations
│   │   ├── canvas.py        # Canvas management
│   │   └── google.py        # Google Docs integration
│   ├── services/            # Business logic
│   │   ├── extraction_service.py
│   │   └── google_docs_service.py
│   ├── models.py            # Database models
│   ├── schemas.py           # Validation schemas
│   ├── database.py          # Database config
│   └── main.py              # Flask app
│
├── tool-code/               # Frontend (React + Vite)
│   ├── components/          # React components
│   ├── services/            # API client
│   ├── App.tsx              # Main app component
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
│
├── run.py                   # Backend entry point
├── start-dev.sh             # Start both services
├── stop-dev.sh              # Stop both services
├── requirements.txt         # Python dependencies
└── .env                     # Environment configuration
```

### Running Tests

**Backend tests:**
```bash
source .venv/bin/activate

# Run comprehensive test suite
python comprehensive_test.py

# Run quick smoke tests
python quick_test.py

# Run specific test file
python test_api.py
```

**Frontend tests:**
```bash
cd tool-code

# Type check
npm run build

# Run tests (if configured)
npm test
```

---

## API Usage

### Example: Create a Meeting

**With direct transcript:**
```bash
curl -X POST http://localhost:5001/api/meetings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly 1:1",
    "transcript": "Alice: How is the project? Bob: Going well!",
    "meeting_date": "2025-11-29T10:00:00",
    "agenda_items": ["Project status", "Next steps"],
    "requested_card_types": ["tldr", "todo", "action_item"]
  }'
```

**With Google Docs URL:**
```bash
# First authenticate
curl http://localhost:5001/api/google/auth/url
# Visit the returned URL to authorize

# Then create meeting
curl -X POST http://localhost:5001/api/meetings/ \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION" \
  -d '{
    "google_doc_url": "https://docs.google.com/document/d/ABC.../edit",
    "meeting_date": "2025-11-29T10:00:00"
  }'
```

### Example: List Cards

```bash
# Get all cards
curl http://localhost:5001/api/cards/

# Get cards for specific meeting
curl http://localhost:5001/api/cards/?meeting_id=1

# Get specific card
curl http://localhost:5001/api/cards/1
```

### Example: Update Card Status

```bash
curl -X PUT http://localhost:5001/api/cards/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "assigned_to": "Alice"
  }'
```

**For complete API documentation, see [API_REFERENCE.md](API_REFERENCE.md)**

---

## Troubleshooting

### Port Already in Use

**Port 5001 (Backend):**
```bash
# Find and kill process
lsof -ti:5001 | xargs kill -9

# Or change port in .env
echo "API_PORT=5002" >> .env
```

**Port 3000 (Frontend):**
```bash
# Vite will auto-try 3001, 3002, etc.
# Or manually kill
lsof -ti:3000 | xargs kill -9
```

### Backend Won't Start

**Check Python environment:**
```bash
source .venv/bin/activate
python --version
pip list | grep -i flask
```

**Reinstall dependencies:**
```bash
pip install --upgrade -r requirements.txt
```

**Check for errors:**
```bash
python run.py
# Look for error messages
```

### Frontend Won't Start

**Reinstall dependencies:**
```bash
cd tool-code
rm -rf node_modules package-lock.json
npm install
```

**Check for errors:**
```bash
npm run dev
# Look for error messages
```

### CORS Errors

If you see CORS errors in browser console:

1. **Verify backend is running:** `curl http://localhost:5001/health`
2. **Check CORS config** in `app/main.py` (already configured)
3. **Verify frontend URL** is making requests to `http://localhost:5001`

### Database Issues

**Reset database:**
```bash
# Stop application
./stop-dev.sh

# Delete database
rm scholarsidekick.db

# Restart (database recreates automatically)
./start-dev.sh
```

### Google OAuth Issues

**"OAuth configuration not found":**
- Ensure `client_secrets.json` exists in project root
- Or set `GOOGLE_CLIENT_CONFIG` environment variable

**"Not authenticated":**
- Complete OAuth flow: `GET /api/google/auth/url`
- Visit returned URL and authorize
- Ensure cookies are being sent with requests

**"Failed to fetch Google Doc":**
- Verify document is accessible by authenticated user
- Check Google Docs API is enabled in your project
- Confirm user granted required permissions

### View Logs

```bash
# Backend logs
tail -f backend.log

# Frontend logs
tail -f frontend.log

# Both at once
tail -f backend.log frontend.log
```

### Clean Restart

```bash
# Stop everything
./stop-dev.sh

# Clean up
rm -f backend.log frontend.log backend.pid frontend.pid
rm -f scholarsidekick.db

# Restart
./start-dev.sh
```

---

## Common Commands Reference

### Daily Development

```bash
# Start application
./start-dev.sh

# Check if running
curl http://localhost:5001/health

# View logs
tail -f backend.log
tail -f frontend.log

# Stop application
./stop-dev.sh
```

### Backend Development

```bash
# Activate environment
source .venv/bin/activate

# Run backend only
python run.py

# Run tests
python comprehensive_test.py

# Install new package
pip install package-name
pip freeze > requirements.txt
```

### Frontend Development

```bash
# Run frontend only
cd tool-code && npm run dev

# Build for production
npm run build

# Install new package
npm install package-name
```

### Database Management

```bash
# View database
sqlite3 scholarsidekick.db ".tables"
sqlite3 scholarsidekick.db "SELECT * FROM meetings;"

# Reset database
rm scholarsidekick.db
python run.py  # Auto-recreates
```

---

## What's Next?

### Start Building Features

1. **Backend:** Add new endpoints in `app/api/`
2. **Frontend:** Create components in `tool-code/components/`
3. **Database:** Update models in `app/models.py`
4. **API Integration:** Connect frontend to backend

### Enable LLM Integration

The extraction service has placeholders ready:

```python
# In app/services/extraction_service.py
# Add your LLM API calls to extract cards from transcripts
```

See `app/services/extraction_service.py` for implementation.

### Deploy to Production

**Backend options:**
- Railway
- Render
- Heroku
- AWS Elastic Beanstalk
- Google Cloud Run

**Frontend options:**
- Vercel
- Netlify
- Cloudflare Pages

**Or serve frontend from Flask** (see [RUNNING_FULLSTACK.md](RUNNING_FULLSTACK.md))

---

## Additional Documentation

- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
- **[GOOGLE_SETUP.md](GOOGLE_SETUP.md)** - Google Docs integration setup
- **[GOOGLE_INTEGRATION.md](GOOGLE_INTEGRATION.md)** - Google Docs feature overview
- **[TESTING.md](TESTING.md)** - Testing guide and results
- **[README.md](README.md)** - Project overview

---

## Support

### Getting Help

1. Check this guide first
2. Review error messages in logs
3. Check the specific documentation:
   - API issues → [API_REFERENCE.md](API_REFERENCE.md)
   - Google Docs → [GOOGLE_SETUP.md](GOOGLE_SETUP.md)
   - Testing → [TESTING.md](TESTING.md)

### Quick Health Check

```bash
# Backend
curl http://localhost:5001/health
# Should return: {"status": "healthy"}

# Frontend
curl -I http://localhost:3000
# Should return: HTTP/1.1 200 OK

# Database
python -c "from app.database import db; from app.main import create_app; app = create_app(); print('✅ Database OK')"
```

---

## Summary

### To get started:
1. ✅ Install prerequisites (Python, Node.js)
2. ✅ Run backend setup (virtual env + pip install)
3. ✅ Run frontend setup (npm install)
4. ✅ Start application (`./start-dev.sh`)
5. ✅ Open http://localhost:3000

### You now have:
- ✅ Flask backend on port 5001
- ✅ React frontend on port 3000
- ✅ Auto-reload on file changes
- ✅ Google Docs integration ready
- ✅ Comprehensive test suite
- ✅ Complete documentation

**Happy coding! 🚀**

---

**Version:** 1.2.0  
**Last Updated:** November 29, 2025  
**Status:** ✅ Production Ready

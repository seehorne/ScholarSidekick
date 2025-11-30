# API Directory - Vercel Deployment

This directory contains requirements and configuration for deploying ScholarSidekick's Flask backend to Vercel.

## Structure

```
api/
├── requirements.txt   # Python dependencies for Vercel deployment
└── README.md         # This file
```

## How It Works

### Local Development
When running locally with `./start-dev.sh`, the Flask app runs normally from `run.py`.

### Vercel Deployment
When deployed to Vercel:
1. Vercel reads `vercel.json` in the project root
2. Builds the Flask backend from `run.py` using `@vercel/python`
3. Builds the React frontend from `tool-code/`
4. Routes `/api/*` requests to the Flask app
5. Routes all other requests to the frontend

**No wrapper code needed!** Vercel uses your `run.py` directly and automatically converts it to serverless functions.

## requirements.txt

This file lists Python dependencies for Vercel deployment. It's similar to the main `requirements.txt` but optimized for serverless deployment (minimal dependencies for faster cold starts).

## Key Differences from Local

| Aspect | Local Development | Vercel Serverless |
|--------|------------------|-------------------|
| Runtime | Long-running Flask server | Serverless functions |
| State | In-memory state persists | Stateless (no persistence between requests) |
| Database | SQLite file works | Must use cloud DB (PostgreSQL, etc.) |
| Cold Starts | None | ~1-2s on first request after idle |
| Scaling | Manual | Automatic |
| Entry Point | `run.py` script | Flask app object from `run.py` |

## Environment Variables

Set these in Vercel dashboard (Project → Settings → Environment Variables):
- `GEMINI_API_KEY` - For LLM features
- `DATABASE_URL` - Cloud database connection string (PostgreSQL recommended)
- `SECRET_KEY` - Flask secret key for sessions
- `GOOGLE_CLIENT_SECRETS` - Base64 encoded Google OAuth credentials (optional)

## Limitations

- **10 second timeout** on free tier (60s on Pro)
- **50MB deployment size** limit
- **No persistent file storage** (use cloud storage for uploads)
- **Cold starts** on first request after ~5 minutes of inactivity
- **SQLite doesn't work** - use PostgreSQL, MySQL, or other cloud database

## Testing Locally with Vercel

You can test the Vercel deployment locally:

```bash
# Install Vercel CLI
npm install -g vercel

# Run in Vercel development mode
vercel dev
```

This simulates the Vercel serverless environment on your machine.

## Deployment

See [VERCEL_DEPLOYMENT.md](../VERCEL_DEPLOYMENT.md) for complete deployment instructions.

## Quick Deploy

```bash
npm install -g vercel
vercel login
vercel --prod
```

# Vercel Deployment Guide for ScholarSidekick

This guide walks you through deploying ScholarSidekick to Vercel, which will host both your React frontend and Flask backend.

## 📋 Prerequisites

1. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional, for command-line deployment)
   ```bash
   npm install -g vercel
   ```
3. **GitHub Account** (recommended for automatic deployments)

---

## 🚀 Deployment Methods

### Method 1: Deploy via GitHub (Recommended)

This method enables automatic deployments on every push to your repository.

#### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Vercel deployment"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/ScholarSidekick.git

# Push to GitHub
git push -u origin main
```

#### Step 2: Import to Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Click **"Import Git Repository"**
4. Select your ScholarSidekick repository
5. Vercel will auto-detect the configuration from `vercel.json`
6. Click **"Deploy"**

#### Step 3: Configure Environment Variables

In the Vercel dashboard, add these environment variables:

```
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=your_production_database_url
SECRET_KEY=your_secret_key_here
```

**How to add environment variables:**
1. Go to your project in Vercel
2. Click **"Settings"**
3. Click **"Environment Variables"**
4. Add each variable for Production, Preview, and Development

---

### Method 2: Deploy via Vercel CLI

#### Step 1: Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate.

#### Step 2: Deploy

```bash
# From the project root
cd /Users/seehorn/Downloads/Development/ScholarSidekick

# Deploy to production
vercel --prod

# Or deploy to preview first
vercel
```

The CLI will guide you through the setup process.

---

## 🔧 How It Works

Vercel reads the `vercel.json` configuration which tells it to:

1. **Build the Flask backend** from `run.py` using `@vercel/python`
2. **Build the React frontend** from `tool-code/` using `@vercel/static-build`
3. **Route `/api/*` requests** to the Flask backend
4. **Route all other requests** to the React frontend

### Configuration: `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "run.py",
      "use": "@vercel/python"
    },
    {
      "src": "tool-code/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "run.py"
    },
    {
      "src": "/(.*)",
      "dest": "/tool-code/dist/index.html"
    }
  ]
}
```

**What this means:**
- Vercel converts your Flask app to serverless functions automatically
- No wrapper code needed - uses `run.py` directly
- All routes in your Flask app work as expected

---

## 🌐 Post-Deployment Configuration

### Update Frontend API URL

After deployment, you'll get a URL like `https://your-app.vercel.app`

**Option 1: Environment Variable (Recommended)**

In Vercel dashboard, add:
```
VITE_API_URL=https://your-app.vercel.app/api
```

Then update your frontend code to use:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';
```

**Option 2: Hardcode in Production Build**

Update `tool-code/src/services/api.ts` or wherever you define your API base URL:

```typescript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api'  // Relative URL in production
  : 'http://localhost:5001';
```

### Configure CORS

Update `app/main.py` to allow your Vercel domain:

```python
from flask_cors import CORS

app = create_app()

# Add your Vercel URL
CORS(app, origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app",
    "https://*.vercel.app"  # Allow all Vercel preview deployments
])
```

---

## 💾 Database Considerations

### Option 1: SQLite (Not Recommended for Production)

Vercel's serverless functions are stateless - SQLite won't persist between invocations.

### Option 2: PostgreSQL (Recommended)

Use a managed database service:

**Vercel Postgres:**
```bash
# Install Vercel Postgres in your project
vercel postgres create
```

**Or use external providers:**
- [Supabase](https://supabase.com) - Free tier available
- [Railway](https://railway.app) - PostgreSQL with free tier
- [Neon](https://neon.tech) - Serverless PostgreSQL
- [PlanetScale](https://planetscale.com) - MySQL alternative

**Update DATABASE_URL:**
```bash
vercel env add DATABASE_URL
# Enter: postgresql://user:password@host:5432/database
```

**Update `app/database.py`:**
```python
# Use PostgreSQL adapter
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

# For PostgreSQL
engine = create_engine(DATABASE_URL)
```

### Option 3: Vercel KV (For Simple Data)

For simple key-value storage:

```bash
vercel kv create
```

---

## 🔐 Google OAuth Configuration

If using Google Docs integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Update OAuth redirect URIs to include your Vercel URL:
   ```
   https://your-app.vercel.app/api/google/auth/callback
   ```
3. Download updated `client_secrets.json`
4. Add as environment variable in Vercel:
   ```bash
   # Convert to base64
   cat client_secrets.json | base64
   
   # Add to Vercel
   vercel env add GOOGLE_CLIENT_SECRETS
   # Paste the base64 string
   ```
5. Update `app/services/google_docs_service.py` to decode:
   ```python
   import base64
   import json
   
   secrets_b64 = os.getenv("GOOGLE_CLIENT_SECRETS")
   if secrets_b64:
       secrets = json.loads(base64.b64decode(secrets_b64))
   ```

---

## 🧪 Testing Your Deployment

### 1. Test Frontend

Visit your Vercel URL: `https://your-app.vercel.app`

### 2. Test Backend API

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Should return: {"status": "healthy"}
```

### 3. Test Full Flow

1. Go to your app
2. Paste a transcript
3. Generate cards
4. Verify everything works

---

## 🔄 Continuous Deployment

Once connected to GitHub, Vercel automatically:
- **Production Deployment:** Every push to `main` branch
- **Preview Deployment:** Every pull request
- **Environment Variables:** Shared across deployments

### Branch Strategy

```bash
# Development
git checkout -b feature/new-feature
# Make changes
git commit -m "Add feature"
git push origin feature/new-feature
# Create PR on GitHub → Vercel creates preview deployment

# Production
git checkout main
git merge feature/new-feature
git push origin main
# → Vercel deploys to production
```

---

## 📊 Monitoring & Logs

### View Logs

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click **"Deployments"**
4. Click on a deployment
5. View **"Runtime Logs"** for API errors
6. View **"Build Logs"** for build errors

### Analytics

Vercel provides:
- Page views
- API function invocations
- Response times
- Error rates

Access at: **Project → Analytics**

---

## 🐛 Troubleshooting

### Build Fails

**Error: "Command failed: npm run build"**

**Solution:**
1. Test build locally:
   ```bash
   cd tool-code
   npm run build
   ```
2. Fix any TypeScript errors
3. Commit and push

### API Functions Timeout

**Error: "Function execution timed out"**

**Solution:**
- Vercel free tier: 10s timeout
- Optimize slow operations
- Or upgrade to Pro for 60s timeout

### CORS Errors

**Error: "Access-Control-Allow-Origin"**

**Solution:**
Update `app/main.py`:
```python
CORS(app, origins=["https://your-app.vercel.app"])
```

### Database Connection Fails

**Error: "Could not connect to database"**

**Solution:**
- Verify DATABASE_URL is set in Vercel
- Use a cloud database (not SQLite)
- Check database allows connections from Vercel IPs

### Environment Variables Not Working

**Error: "API key not found"**

**Solution:**
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Ensure variables are set for **Production** environment
3. Redeploy after adding variables

---

## 💰 Pricing

### Vercel Free Tier Includes:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Serverless function executions
- ✅ Automatic HTTPS
- ✅ Preview deployments
- ✅ Analytics

### Limits:
- 10s function timeout (Pro: 60s)
- 50MB function size
- 6s build time for hobby

**For most development/personal projects, the free tier is sufficient.**

---

## 🎯 Production Checklist

Before going live:

- [ ] Test all features locally
- [ ] Set up production database (PostgreSQL/MySQL)
- [ ] Configure all environment variables in Vercel
- [ ] Update Google OAuth redirect URIs
- [ ] Test API endpoints
- [ ] Enable Vercel Analytics
- [ ] Set up custom domain (optional)
- [ ] Configure error monitoring (Sentry, etc.)
- [ ] Test on mobile devices
- [ ] Review security settings
- [ ] Set up backup strategy for database

---

## 🌟 Custom Domain (Optional)

### Add Custom Domain

1. Go to Vercel Dashboard → Your Project
2. Click **"Settings"** → **"Domains"**
3. Add your domain: `scholarsidekick.com`
4. Update DNS records as instructed by Vercel
5. Vercel automatically provisions SSL certificate

### Update Google OAuth

Don't forget to update Google Cloud Console with new domain:
```
https://scholarsidekick.com/api/google/auth/callback
```

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [Flask on Vercel](https://vercel.com/guides/using-flask-with-vercel)

---

## 🆘 Getting Help

### Vercel Support
- [Community Discord](https://vercel.com/discord)
- [GitHub Discussions](https://github.com/vercel/vercel/discussions)
- [Support](https://vercel.com/support)

### Common Issues
1. Check deployment logs in Vercel dashboard
2. Test build locally first: `npm run build`
3. Verify environment variables are set
4. Check Vercel status page for outages

---

## 📝 Quick Deploy Commands

```bash
# Clone and deploy
git clone <your-repo>
cd ScholarSidekick
vercel --prod

# Deploy specific branch
git checkout feature-branch
vercel

# Deploy with custom name
vercel --name scholar-sidekick-staging

# View logs
vercel logs <deployment-url>
```

---

## 🎉 You're Done!

Your ScholarSidekick app should now be live at:
- **Production**: `https://your-app.vercel.app`
- **API**: `https://your-app.vercel.app/api/`

Every push to `main` will trigger a new deployment automatically.

**Happy deploying! 🚀**

---

**Last Updated:** November 29, 2025  
**Vercel Version:** 2  
**Status:** ✅ Production Ready

# 🚀 Quick Deploy to Vercel

## One-Time Setup (5 minutes)

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login
```bash
vercel login
```

### 3. Deploy
```bash
cd /Users/seehorn/Downloads/Development/ScholarSidekick
vercel --prod
```

That's it! ✨

---

## Via GitHub (Automatic Deployments)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ScholarSidekick.git
git push -u origin main
```

### 2. Import to Vercel
1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your repo
4. Click "Deploy"

---

## Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

```
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://... (for production)
```

---

## After Deployment

Your app will be live at:
- **Frontend:** https://your-app.vercel.app
- **API:** https://your-app.vercel.app/api

---

## Troubleshooting

### Build fails?
```bash
# Test locally first
cd tool-code
npm run build
```

### API not working?
- Check environment variables are set
- View logs in Vercel dashboard → Deployments → Runtime Logs

### CORS errors?
Update `app/main.py` with your Vercel URL in CORS origins

---

## Full Documentation

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for complete guide.

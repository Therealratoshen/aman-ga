# 🚀 Vercel Deployment Guide

Deploy the Aman ga? frontend to Vercel in 5 minutes!

## Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:
```bash
cd aman-ga
git add -A
git commit -m "Ready for deployment"
git push origin main
```

## Step 2: Deploy to Vercel

### Option A: Vercel CLI (Fastest)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to frontend folder
cd frontend

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name? aman-ga
# - Directory? ./
# - Override settings? N

# Production deploy
vercel --prod
```

### Option B: Vercel Dashboard

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your `aman-ga` repository
4. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
5. Click "Deploy"

## Step 3: Configure Environment Variables

In Vercel Dashboard:
1. Go to Project Settings → Environment Variables
2. Add:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-url.com
   ```
3. Click "Save"

## Step 4: Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your domain: `aman-ga.com` (or any domain)
3. Follow DNS configuration instructions

## Step 5: Test Deployment

After deployment completes:
- **Preview URL:** https://aman-ga-xxxx.vercel.app
- **Production URL:** https://aman-ga.vercel.app

Test these features:
- ✅ Login page loads
- ✅ Animations work (blobs, hover effects)
- ✅ Forms are interactive
- ✅ Responsive on mobile

## Automatic Deployments

Vercel automatically deploys when you push to GitHub:
```bash
git push origin main
# Vercel will auto-deploy in ~1 minute
```

## Troubleshooting

### Build Fails
```bash
# Test build locally
cd frontend
npm run build
```

### API Not Working
- Make sure `NEXT_PUBLIC_API_URL` is set in Vercel
- Check backend is deployed and accessible

### Styling Issues
- Verify Tailwind CSS is installed: `npm install`
- Check `tailwind.config.js` exists

## Cost

**Vercel Free Tier:**
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Automatic SSL
- ✅ Custom domains
- Perfect for POC and startups!

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ⏳ Deploy backend (Railway/Render)
3. ⏳ Set up Supabase database
4. ⏳ Configure environment variables

---

**Ready to deploy?** Run `vercel` in the frontend folder!

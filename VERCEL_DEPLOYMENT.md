# CuraGenie Vercel Deployment Guide

This guide will help you deploy CuraGenie to Vercel successfully.

## 🚀 Quick Deployment Steps

### Prerequisites
- Vercel account (free tier is fine)
- GitHub repository with this code
- Backend deployed on Railway/Render/similar service

### 1. Backend Deployment (Choose one)

#### Option A: Railway (Recommended)
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Select the `backend` folder as root directory
4. Set these environment variables:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/db
   SECRET_KEY=your-super-secret-key-here
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   ```

#### Option B: Render
1. Go to [Render.com](https://render.com)
2. Create new Web Service from GitHub
3. Set root directory to `backend`
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### 2. Frontend Deployment on Vercel

#### Step 1: Connect Repository
1. Go to [Vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Set root directory to `frontend`

#### Step 2: Configure Environment Variables
In Vercel dashboard, add these environment variables:

```bash
# Required - Update with your backend URL
NEXT_PUBLIC_API_URL=https://your-backend-api.railway.app

# Optional - Supabase credentials (if using)
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-key

# App Configuration
NEXT_PUBLIC_APP_NAME=CuraGenie
NEXT_PUBLIC_APP_VERSION=2.0.0-production
NEXT_PUBLIC_ENVIRONMENT=production
```

#### Step 3: Deploy
1. Click "Deploy"
2. Wait for build to complete
3. Your app will be available at `https://your-project.vercel.app`

## 🔧 Configuration Files

### Frontend - vercel.json
The project includes a pre-configured `vercel.json` with:
- Next.js framework detection
- Security headers
- Function timeouts
- Production optimizations

### Environment Files
- `.env.local` - Local development
- `.env.production` - Production deployment template

## 🔍 Troubleshooting

### Common Issues

#### 1. Build Fails
- Check if all dependencies are listed in `package.json`
- Verify TypeScript types are correct
- Check build logs in Vercel dashboard

#### 2. API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` points to your backend
- Check CORS settings in backend
- Ensure backend is deployed and accessible

#### 3. Authentication Not Working
- Verify backend auth endpoints are working
- Check environment variables are set correctly
- Ensure JWT secret keys match between frontend/backend

#### 4. Styling Issues
- Tailwind CSS should work out of the box
- Check if all CSS imports are correct

## 🔒 Security Checklist

- [ ] Remove debug mode in production (`NEXT_PUBLIC_ENABLE_DEBUG=false`)
- [ ] Set secure CORS origins
- [ ] Use HTTPS for all API calls
- [ ] Secure JWT secret keys
- [ ] Enable security headers (already configured)

## 📊 Performance Optimization

The frontend is already optimized with:
- Next.js App Router for better performance
- Static generation where possible
- Image optimization
- Code splitting
- Tree shaking

## 🚨 Important Notes

1. **Backend Dependency**: The frontend requires a running backend API
2. **Environment Variables**: Must be set in Vercel dashboard (not in code)
3. **CORS**: Backend must allow your Vercel domain
4. **Database**: Backend needs a PostgreSQL database (Railway provides this)

## 📞 Support

If you encounter issues:
1. Check Vercel function logs
2. Check backend logs
3. Verify all environment variables
4. Test auth endpoints manually

## 🎉 Success!

Once deployed, you should have:
- ✅ Frontend running on Vercel
- ✅ Backend running on Railway/Render
- ✅ Database connected
- ✅ Authentication working
- ✅ File uploads working (if configured)

Your CuraGenie application is now live! 🚀

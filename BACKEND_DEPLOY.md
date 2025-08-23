# 🚀 Deploy CuraGenie Backend - Quick Guide

## Option 1: Railway (Recommended - Free & Easy)

1. **Go to** [Railway.app](https://railway.app)
2. **Sign up/Login** with GitHub
3. **Click "New Project"** → **"Deploy from GitHub repo"**
4. **Select** your `harshguptakiet/Cura-Genie` repository
5. **Configure**:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements-minimal.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

6. **Set Environment Variables**:
   ```
   DATABASE_URL=sqlite:///./curagenie.db
   SECRET_KEY=your-super-secret-key-here-make-it-long
   CORS_ORIGINS=https://your-frontend.vercel.app,https://*.vercel.app
   DEBUG=false
   ```

7. **Deploy!** Railway will give you a URL like: `https://your-app.railway.app`

## Option 2: Render (Also Free)

1. **Go to** [Render.com](https://render.com)
2. **Sign up/Login** with GitHub
3. **New Web Service** → **Connect GitHub**
4. **Select** your `Cura-Genie` repository
5. **Configure**:
   - **Name**: `curagenie-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements-minimal.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

6. **Environment Variables**: Same as Railway above

## Option 3: Vercel (Serverless)

Actually, let's just use Railway or Render since they're better for FastAPI backends.

---

## 🔄 After Backend is Deployed

1. **Copy your backend URL** (e.g., `https://curagenie-backend.railway.app`)

2. **Update Vercel Environment Variables**:
   - Go to your Vercel dashboard
   - Click on your frontend project
   - Go to Settings → Environment Variables
   - Update: `NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app`
   - **Redeploy** your frontend

3. **Test**: Your app should now work!

---

## 🆘 If You Get Errors

### Backend Deployment Fails
- Check build logs in Railway/Render
- Make sure `requirements-minimal.txt` is correct
- Verify Python version compatibility

### Frontend Still Shows localhost Error
- Make sure you updated `NEXT_PUBLIC_API_URL` in Vercel
- Redeploy the frontend after changing environment variables
- Check browser developer tools for CORS errors

### CORS Errors
- Add your Vercel frontend URL to `CORS_ORIGINS` in backend
- Format: `https://your-app.vercel.app,https://*.vercel.app`

---

## ✅ Success Checklist

- [ ] Backend deployed and showing "healthy" status
- [ ] Backend URL accessible (visit `/health` endpoint)
- [ ] Frontend environment variables updated
- [ ] Frontend redeployed
- [ ] Login/signup working

**Your app should now be fully deployed and working!** 🎉

# 🚀 CuraGenie - Live Website Deployment Plan

## 🎯 **BEST OPTIONS FOR LIVE DEPLOYMENT**

Based on your setup, here are the **3 best deployment options** ranked by ease and cost:

---

## 🥇 **OPTION 1: Railway + Vercel (RECOMMENDED)**
**💰 Cost: ~$5-10/month | ⏱️ Time: 30 minutes | 🔧 Difficulty: Easy**

### ✅ **Why This is Best:**
- ✅ **Cheapest**: Railway $5/month, Vercel free
- ✅ **Easiest**: No server management
- ✅ **Auto-scaling**: Handles traffic spikes
- ✅ **Built-in SSL**: HTTPS included
- ✅ **CI/CD**: Auto-deploy on git push

### 📋 **Quick Setup:**

#### **Step 1: Push to GitHub (5 minutes)**
```powershell
# In your project directory
git init
git add .
git commit -m "Initial deployment"
git remote add origin https://github.com/YourUsername/curagenie.git
git push -u origin main
```

#### **Step 2: Deploy Backend on Railway (10 minutes)**
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `curagenie` repository
4. **Configure:**
   - **Root Directory**: `backend`
   - **Build Command**: Leave default
   - **Start Command**: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables:**
```env
DATABASE_URL=sqlite:////app/data/curagenie.db
SECRET_KEY=your-secret-key-here-32-chars-minimum
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
ENABLE_REAL_GENOMIC_ANALYSIS=true
MAX_FILE_SIZE_MB=100
```

6. **Add Volume:**
   - Create volume: `curagenie-data` (1GB)
   - Mount path: `/app/data`

7. **Deploy** and copy your Railway URL (e.g., `https://your-app.up.railway.app`)

#### **Step 3: Deploy Frontend on Vercel (10 minutes)**
1. Go to [vercel.com](https://vercel.com) and sign up
2. Click "New Project" → Import from GitHub
3. Select your repository
4. **Configure:**
   - **Framework**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`

5. **Add Environment Variables:**
```env
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_PUBLIC_ENABLE_GENOMICS=true
NEXT_PUBLIC_ENABLE_MRI_ANALYSIS=true
```

6. **Deploy** and get your Vercel URL (e.g., `https://your-app.vercel.app`)

#### **Step 4: Update CORS (5 minutes)**
- Go back to Railway
- Update `CORS_ORIGINS` to include your Vercel URL:
```env
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### 🎉 **DONE! Your app is live at:**
- **🌐 Frontend**: `https://your-app.vercel.app`
- **🔗 API**: `https://your-railway-app.up.railway.app`

---

## 🥈 **OPTION 2: Digital Ocean App Platform**
**💰 Cost: ~$12/month | ⏱️ Time: 45 minutes | 🔧 Difficulty: Medium**

### ✅ **Why This is Good:**
- All-in-one platform
- Built-in database options
- Good performance
- Simple scaling

### 📋 **Quick Setup:**
1. Sign up at [digitalocean.com](https://www.digitalocean.com/products/app-platform)
2. Create new App → Connect GitHub
3. **Add 2 Components:**
   - **Backend**: Python service (Dockerfile in `backend/`)
   - **Frontend**: Static site (Node.js build from `frontend/`)
4. Configure environment variables (same as Railway)
5. Deploy

---

## 🥉 **OPTION 3: VPS with Docker**
**💰 Cost: ~$5-20/month | ⏱️ Time: 2 hours | 🔧 Difficulty: Advanced**

### ✅ **Why This is Good:**
- Full control
- Can handle any traffic
- Cheapest for high usage
- Custom configurations

### 📋 **Quick Setup:**
1. **Get VPS:** DigitalOcean, Linode, or Vultr ($5-10/month)
2. **Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```
3. **Deploy with Docker Compose:**
```bash
git clone https://github.com/YourUsername/curagenie.git
cd curagenie
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# Edit environment files
docker-compose -f docker-compose.prod.yml up -d
```
4. **Configure Nginx + SSL** (using Certbot)

---

## 🚀 **PRODUCTION-READY OPTIMIZATIONS**

### 🔐 **Essential Security Setup:**
```env
# Strong secret key (32+ characters)
SECRET_KEY=your-super-secure-random-key-32-chars-minimum

# Restrict CORS to your domain only
CORS_ORIGINS=https://yourdomain.com

# Enable production mode
DEBUG=false
ENVIRONMENT=production
```

### 📊 **Performance Optimizations:**
```env
# Database optimization
MAX_VARIANTS_STORE=1000

# File upload limits
MAX_FILE_SIZE_MB=100

# Enable all features
ENABLE_REAL_GENOMIC_ANALYSIS=true
ENABLE_ENHANCED_MRI=true
ENABLE_ML=true
```

### 🔍 **Monitoring Setup:**
- Enable health checks: `/health` endpoint
- Set up uptime monitoring (UptimeRobot free)
- Monitor error logs in Railway/Vercel dashboard

---

## 📱 **CUSTOM DOMAIN SETUP (OPTIONAL)**

### **For Railway Backend:**
1. Railway dashboard → Settings → Domains
2. Add custom domain: `api.yourdomain.com`
3. Update DNS: `CNAME api.yourdomain.com → your-app.up.railway.app`

### **For Vercel Frontend:**
1. Vercel dashboard → Settings → Domains  
2. Add custom domain: `yourdomain.com`
3. Update DNS as instructed by Vercel

### **Update Environment Variables:**
```env
# Railway
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Vercel  
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## ✅ **DEPLOYMENT CHECKLIST**

### **Before Going Live:**
- [ ] GitHub repository created and pushed
- [ ] Railway backend deployed and healthy
- [ ] Vercel frontend deployed successfully
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Health endpoints responding (`/health`)
- [ ] VCF file upload tested
- [ ] Genome browser displaying data
- [ ] Timeline showing events
- [ ] Custom domain configured (optional)

### **Testing Your Live Site:**
```bash
# Test backend API
curl https://your-railway-app.up.railway.app/health

# Test frontend
curl https://your-app.vercel.app/api/health

# Test specific features
curl https://your-railway-app.up.railway.app/api/genomic/variants/1
```

---

## 🎯 **RECOMMENDED NEXT STEPS**

### **1. START WITH OPTION 1 (Railway + Vercel)**
- **Fastest to deploy** (30 minutes)
- **Most cost-effective** (~$5/month)
- **Easiest to maintain**
- **Perfect for MVP and testing**

### **2. Test Everything:**
- Upload a VCF file
- Check genome browser
- Test timeline events
- Try AI chatbot
- Verify MRI analysis

### **3. Scale Later:**
- Monitor usage and performance
- Add custom domain when ready
- Upgrade resources as needed
- Consider Option 2 or 3 for high traffic

---

## 🆘 **NEED HELP?**

### **Common Issues:**
1. **Build Fails**: Check environment variables in deployment dashboard
2. **CORS Errors**: Verify `CORS_ORIGINS` includes your frontend URL
3. **Database Issues**: Ensure volume is properly mounted (Railway)
4. **File Upload Fails**: Check `MAX_FILE_SIZE_MB` and upload directory

### **Debug Commands:**
```bash
# Check Railway logs
railway logs

# Check Vercel logs  
vercel logs

# Test APIs locally first
docker-compose up -d
curl http://localhost:8001/health
```

---

## 🎉 **FINAL RESULT**

After following Option 1, you'll have:

- ✅ **Live Website**: `https://your-app.vercel.app`
- ✅ **Real VCF Processing**: Upload and analyze genomic data
- ✅ **Interactive Genome Browser**: Visualize variants
- ✅ **AI Medical Chatbot**: Get health insights
- ✅ **Secure & Scalable**: Production-ready infrastructure
- ✅ **Auto-Deploy**: Push to GitHub = automatic updates

**Total Time: ~30 minutes | Total Cost: ~$5/month**

🚀 **Ready to make CuraGenie live? Start with Option 1 now!** 🚀

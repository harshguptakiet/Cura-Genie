# 🚀 CuraGenie Enhanced Genomic Analysis - Startup Guide

## Overview
This guide will help you start both the **Enhanced Backend** (with minimal dependencies) and the **Frontend** for the CuraGenie Enhanced Genomic Analysis system.

## 🎯 What We've Built

### Backend Services (Simplified - No numpy/pandas dependencies)
- ✅ **Variant Annotation Service** - ClinVar and gnomAD integration
- ✅ **ML Prediction Service** - Disease risk prediction (Diabetes, Alzheimer's, Brain Tumor)
- ✅ **Report Generation Service** - Comprehensive analysis reports
- ✅ **Enhanced Genomic Processor** - Orchestrates all services
- ✅ **FastAPI Backend** - RESTful API endpoints

### Frontend (Next.js + React + Modern UI)
- ✅ **Enhanced Genomic Analysis Page** - New comprehensive interface
- ✅ **Modern UI Components** - Radix UI + Tailwind CSS
- ✅ **Real-time Updates** - Progress tracking and status updates
- ✅ **Responsive Design** - Works on all devices
- ✅ **Sample Data Support** - Built-in test VCF data

## 🚀 Quick Start

### Option 1: Use Batch Scripts (Recommended for Windows)

#### 1. Start the Enhanced Backend
```bash
# Double-click this file or run from command line:
start-simple-backend.bat
```
**Expected Output:**
```
🚀 Starting CuraGenie Enhanced Genomic Analysis Backend...
📊 Services initialized:
   ✅ Variant Annotation Service
   ✅ ML Prediction Service 
   ✅ Report Generation Service
   ✅ Enhanced Genomic Processor
🌐 API available at: http://localhost:8000
📚 API docs at: http://localhost:8000/docs
```

#### 2. Start the Frontend (in a new terminal)
```bash
# Double-click this file or run from command line:
start-frontend.bat
```
**Expected Output:**
```
🚀 Starting CuraGenie Frontend...
🔄 Starting Next.js development server on http://localhost:3000
```

### Option 2: Manual Commands

#### 1. Start Backend
```bash
cd backend
python main_simple.py
```

#### 2. Start Frontend
```bash
cd frontend
npm run dev
```

## 🌐 Access Points

### Backend API
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Frontend
- **Main App**: http://localhost:3000
- **Enhanced Genomic Page**: http://localhost:3000/enhanced-genomic

## 🧪 Testing the System

### 1. Backend Health Check
Visit: http://localhost:8000/health
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": 1234567890.123,
  "services": {
    "variant_annotation": "available",
    "ml_prediction": "available",
    "report_generation": "available"
  }
}
```

### 2. Frontend Backend Connection
- Go to: http://localhost:3000/enhanced-genomic
- Look for the "Backend Connected" green badge
- If you see "Backend Disconnected", ensure the backend is running

### 3. Quick API Test
Visit: http://localhost:8000/api/test/quick
**Expected Response:**
```json
{
  "success": true,
  "services_tested": [
    "variant_annotation",
    "ml_prediction", 
    "report_generation",
    "enhanced_processor"
  ],
  "message": "All services are working correctly!"
}
```

## 📊 Using the Enhanced Genomic Analysis

### 1. Navigate to the Page
- Go to: http://localhost:3000/enhanced-genomic
- Ensure you see "Backend Connected" status

### 2. Input VCF Data
- **Option A**: Use sample data (click "Load Sample Data")
- **Option B**: Paste your own VCF content
- **Option C**: Upload a VCF file (future enhancement)

### 3. Start Analysis
- Click "Start Analysis"
- Watch real-time progress updates
- View comprehensive results in organized tabs

### 4. Review Results
The system provides results in organized tabs:
- **Summary**: Executive overview and risk assessment
- **Diseases**: Detailed analysis for each supported disease
- **Variants**: Top variants and their significance
- **Technical**: Processing details and limitations

## 🔧 Troubleshooting

### Backend Won't Start
**Problem**: `ModuleNotFoundError: No module named 'requests_cache'`
**Solution**: The simplified backend uses only packages that are already installed. Ensure you're running `main_simple.py`, not `main_enhanced.py`.

**Problem**: Port 8000 already in use
**Solution**: 
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process
taskkill /PID <PID> /F
```

### Frontend Won't Start
**Problem**: `npm` not found
**Solution**: Install Node.js from https://nodejs.org/

**Problem**: Port 3000 already in use
**Solution**: 
```bash
# Find process using port 3000
netstat -ano | findstr :3000
# Kill the process
taskkill /PID <PID> /F
```

### Connection Issues
**Problem**: Frontend shows "Backend Disconnected"
**Solution**: 
1. Ensure backend is running on http://localhost:8000
2. Check backend console for errors
3. Verify no firewall blocking the connection

## 📁 File Structure

```
Cura-Genie/
├── backend/
│   ├── services/
│   │   ├── variant_annotation_simple.py      # Simplified variant annotation
│   │   ├── ml_prediction_simple.py           # ML disease prediction
│   │   ├── report_generator_simple.py        # Report generation
│   │   └── enhanced_genomic_processor_simple.py # Main orchestrator
│   ├── main_simple.py                        # Simplified FastAPI app
│   └── requirements-minimal-enhanced.txt     # Minimal dependencies
├── frontend/
│   ├── src/
│   │   ├── app/enhanced-genomic/page.tsx    # New analysis page
│   │   ├── lib/enhanced-genomic-service.ts  # API service layer
│   │   └── components/                       # UI components
│   └── package.json                          # Frontend dependencies
├── start-simple-backend.bat                  # Backend startup script
├── start-frontend.bat                        # Frontend startup script
└── STARTUP_GUIDE.md                          # This file
```

## 🎯 What Happens During Analysis

### 1. VCF Parsing
- Parse VCF content without external libraries
- Validate variant data
- Extract genomic coordinates and changes

### 2. Variant Annotation
- Query ClinVar for clinical significance
- Query gnomAD for population frequency
- Calculate functional impact (simplified SIFT/PolyPhen-2)

### 3. ML Prediction
- Extract 20 genomic features
- Run disease-specific models:
  - **Diabetes**: Gradient Boosting
  - **Alzheimer's**: Random Forest
  - **Brain Tumor**: Random Forest

### 4. Report Generation
- Executive summary with overall risk
- Disease-specific assessments
- Variant prioritization
- Technical details and limitations

## 🚀 Performance Targets

- **Processing Time**: Under 60 seconds for standard exome VCF
- **Real-time Updates**: Progress tracking every 2 seconds
- **Scalability**: Batch processing for large datasets
- **Reliability**: Graceful error handling and fallbacks

## 🔮 Future Enhancements

- **File Upload**: Direct VCF file upload support
- **Batch Processing**: Multiple VCF files simultaneously
- **Advanced ML**: More sophisticated disease models
- **Real Databases**: Integration with actual genomic databases
- **User Management**: Authentication and user profiles
- **Export Options**: PDF reports, CSV data export

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all services are running
3. Check the troubleshooting section above
4. Ensure ports 8000 and 3000 are available

## 🎉 Success Indicators

You'll know everything is working when you see:
- ✅ Backend: "All services are working correctly!"
- ✅ Frontend: "Backend Connected" green badge
- ✅ Analysis: Real-time progress updates
- ✅ Results: Comprehensive genomic risk assessment

---

**Happy Genomic Analysis! 🧬✨**

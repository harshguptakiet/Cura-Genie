@echo off
echo ========================================
echo    CuraGenie Enhanced Backend v2.0
echo ========================================
echo.
echo Starting Enhanced Genomic Analysis Backend...
echo.
echo Features:
echo - Real-time VCF processing (target: 60 seconds)
echo - ML disease prediction (Diabetes, Alzheimer's, Brain Tumors)
echo - Variant annotation (ClinVar, gnomAD, SIFT, PolyPhen-2)
echo - Comprehensive reporting system
echo.
echo Target Processing Time: 60 seconds
echo Supported Diseases: Diabetes, Alzheimer's, Brain Tumors
echo Annotation Sources: ClinVar, gnomAD, SIFT, PolyPhen-2
echo.
echo ========================================
echo.

cd backend

echo Installing enhanced dependencies...
pip install -r requirements.txt

echo.
echo Starting Enhanced Backend...
echo API will be available at: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main_enhanced.py

pause

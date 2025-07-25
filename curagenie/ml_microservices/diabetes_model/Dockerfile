FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install flask pandas joblib xgboost
EXPOSE 8000
CMD ["python", "inference_xgb.py"]

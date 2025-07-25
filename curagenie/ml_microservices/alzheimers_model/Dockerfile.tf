FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install flask tensorflow numpy
EXPOSE 8001
CMD ["python", "inference_seq_tf.py"]

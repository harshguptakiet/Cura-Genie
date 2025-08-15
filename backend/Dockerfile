FROM python:3.11-slim as builder

# Install system dependencies for building and runtime libs needed by OpenCV/TensorFlow
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime libs needed by OpenCV/TensorFlow
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r curagenie && useradd -r -g curagenie curagenie

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories and set permissions (match docker-compose volumes)
RUN mkdir -p /app/data/uploads /app/data /app/logs && \
    chown -R curagenie:curagenie /app

# Switch to non-root user
USER curagenie

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the application with Gunicorn for production
CMD ["gunicorn", "app:app", "-w", "1", "--timeout", "120", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]

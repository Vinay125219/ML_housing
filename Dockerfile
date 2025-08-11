# Use the official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Docker CLI for Streamlit service management
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with specific versions to avoid compatibility issues
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install streamlit  # Add Streamlit installation

# Verify installations
RUN pip list

# Copy all files into the container
COPY . .

# Create necessary directories and ensure proper permissions
RUN mkdir -p housinglogs models data mlruns logs shared

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 mlops && chown -R mlops:mlops /app
USER mlops

# Expose ports for different services
# 8000: FastAPI housing service
# 8002: Retraining service
# 5000: MLflow tracking server
# 9090: Prometheus
# 3000: Grafana
# 8501: Streamlit UI (new)
EXPOSE 8000 8002 5000 9090 3000 8501

# Set environment variables for service discovery
ENV PROMETHEUS_URL=http://prometheus:9090
ENV MLFLOW_TRACKING_URI=http://mlflow:5000

# Make startup script executable
RUN chmod +x startup.sh

# Use startup script to ensure proper initialization
CMD ["/app/startup.sh"]
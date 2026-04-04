FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose gRPC port
EXPOSE 50053

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "
import grpc
try:
    channel = grpc.insecure_channel('localhost:50053')
    channel.subscribe(lambda state: None, try_to_connect=True)
    print('healthy')
except:
    exit(1)
"

# Run the service
CMD ["python", "main.py"]

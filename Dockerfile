# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Default command (redundant since docker-compose sets it, but good to have)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

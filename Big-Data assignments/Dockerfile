# Use Python 3.11.10 slim image as base
FROM python:3.11.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./backend ./backend


CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

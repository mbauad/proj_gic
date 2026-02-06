FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
# gcc and python3-dev might be needed for some compilation
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY flask_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn
RUN pip install gunicorn

# Copy application code
COPY flask_app/ .

# Expose port (internal)
EXPOSE 5001

# Run command
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5001", "app:app"]

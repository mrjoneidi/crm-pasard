
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (e.g., for psycopg2 if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure instance and uploads directories exist
RUN mkdir -p instance uploads

# Expose port
EXPOSE 5000

# Default command (can be overridden)
CMD ["python", "app.py"]

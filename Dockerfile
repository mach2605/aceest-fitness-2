# Dockerfile for ACEest Fitness v1.0 (development image)
FROM python:3.11-slim

# Set working directory
WORKDIR /usr/src/app  

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /usr/src/app   

ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=5001
EXPOSE 5001

CMD ["python", "app.py"]
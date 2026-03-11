# Use a lightweight Python base image
FROM python:3.9-slim

# Set environment variables to prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fonts/ ./fonts/

# Copy application code
COPY . .

# Expose the port Streamlit runs on (Cloud Run expects 8080 by default)
EXPOSE 8080

# Run Streamlit
# --server.port=8080 tells Streamlit to listen on the port Cloud Run exposes
# --server.address=0.0.0.0 makes it accessible externally
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
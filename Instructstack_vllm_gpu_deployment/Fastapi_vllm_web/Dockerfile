# Use a slim Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set root working directory
WORKDIR /FASTAPI

# Copy app code from host into container's /FASTAPI/app
COPY app/ app/

# Copy requirements.txt into /FASTAPI
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 9000

# Final working directory will be /FASTAPI
WORKDIR /FASTAPI/app

# Run the app on port 9000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]

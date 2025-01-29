# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy required files
COPY requirements.txt .
COPY app.py .
COPY templates/ ./templates/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
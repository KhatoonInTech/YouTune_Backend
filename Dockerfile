# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Ensure the /app directory exists
RUN mkdir -p /app

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8080"]

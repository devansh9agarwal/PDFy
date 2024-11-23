# Use an official Python image as a base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
libreoffice \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /app

# Expose the port your Flask app runs on
EXPOSE 5000

# Set the default command to run the Flask application
CMD ["python", "app.py"]

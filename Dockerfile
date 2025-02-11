# Use the official Python image.
FROM python:3.10-slim

# Prevents Python from writing .pyc files to disk.
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures output is logged to the console.
ENV PYTHONUNBUFFERED=1

# Set the working directory.
WORKDIR /app

# Copy and install dependencies.
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files.
COPY . /app/

# Expose port 80.
EXPOSE 80

# Command to run the application.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
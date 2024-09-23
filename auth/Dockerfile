FROM python:3.10-slim-bullseye

# Install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential libpq-dev \
  && pip install --no-cache-dir --upgrade pip

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt /app

# Install Python dependencies
RUN pip install --no-cache-dir --requirement /app/requirements.txt

# Copy the application code
COPY . /app

# Expose the application port
EXPOSE 5000

# Command to run the application
CMD ["python3", "server.py"]

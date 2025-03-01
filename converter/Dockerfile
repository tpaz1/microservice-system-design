# Use a lightweight base image
FROM python:3.10-slim-bullseye AS builder

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary system dependencies for both amd64 and arm64
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 libpq-dev=13.20-0+deb11u1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt .

# Install Python dependencies inside a virtual environment
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Use a minimal final image
FROM python:3.10-slim-bullseye

# Create a non-root user for security
RUN useradd --create-home appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . /app

# Set permissions for the non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Set environment variable to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python3", "consumer.py"]

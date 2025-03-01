# Use a lightweight base image
FROM python:3.10-slim-bullseye AS builder

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary system dependencies with pinned versions
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential=12.9 libpq-dev=13.20-0+deb11u1 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt .

# Install Python dependencies inside a virtual environment with pinned versions
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip==25.0.1 && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Use a minimal final image
FROM python:3.10-slim-bullseye

# Install only the necessary runtime dependencies with pinned versions
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  libpq5=13.20-0+deb11u1 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd --create-home appuser
WORKDIR /app

# Copy built environment from the builder stage
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
CMD ["python3", "server.py"]

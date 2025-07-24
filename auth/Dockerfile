#####################
##  Builder Stage  ##
#####################
FROM python:3.10-slim-bullseye AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Inject credentials at build time via build-args
ARG DEBIAN_REMOTE_URL
ARG PIP_INDEX_URL

# Configure apt to use JFrog Debian remote
RUN echo "deb [trusted=yes] $DEBIAN_REMOTE_URL bullseye main" > /etc/apt/sources.list.d/jfrog.list

# Install build dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
     build-essential=12.9 libpq-dev=13.21-0+deb11u1 \
  && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/jfrog.list

WORKDIR /app

COPY ./requirements.txt .

# Use virtualenv and pip from JFrog PyPI remote
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir --index-url "$PIP_INDEX_URL" -r requirements.txt

#####################
##  Final Stage    ##
#####################
FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

ARG DEBIAN_REMOTE_URL

# Configure apt to use JFrog Debian remote
RUN echo "deb [trusted=yes] $DEBIAN_REMOTE_URL bullseye main" > /etc/apt/sources.list.d/jfrog.list

# Install runtime dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
     libpq5=13.21-0+deb11u1 \
  && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/jfrog.list

# Security: run as non-root
RUN useradd --create-home appuser
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . /app

RUN chown -R appuser:appuser /app
USER appuser

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 5000

CMD ["python3", "server.py"]

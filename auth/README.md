# Secure Dockerfile for Python Application

## Overview
This Dockerfile is designed to build a secure, lightweight, and efficient Python-based application container. The multi-stage build approach ensures that only the necessary components are included in the final image, reducing attack surfaces and improving security.

## Security Enhancements
### 1️⃣ **Use of a Minimal Base Image**
- **Base image:** `python:3.10-slim-bullseye` is used instead of a full Debian image to minimize vulnerabilities.
- **Final image:** The runtime container does not include unnecessary development tools, reducing the attack surface.

### 2️⃣ **Non-Root User for Execution**
- A dedicated **non-root user (`appuser`)** is created to avoid running the application as root.
- Prevents privilege escalation in case of security breaches.

### 3️⃣ **Multi-Stage Build for Optimization**
- Uses a **builder stage** to install dependencies and a **final stage** to copy only necessary artifacts.
- **Benefit:** Keeps the final image **small and secure** by excluding build-time dependencies.

### 4️⃣ **Dependency Pinning for Security & Stability**
- **APT Packages:** `libpq-dev=13.20-0+deb11u1` and `build-essential=12.9` are pinned to avoid supply chain attacks from unverified updates.
- **Pip Packages:** `pip==25.0.1` is pinned to ensure compatibility and security.

### 5️⃣ **Minimal System Dependencies**
- Uses `--no-install-recommends --no-install-suggests` with `apt-get install` to install only necessary packages.
- Cleans up unused files using `apt-get clean && rm -rf /var/lib/apt/lists/*` to reduce the attack surface.

### 6️⃣ **Virtual Environment for Python Dependencies**
- A virtual environment (`/opt/venv`) is created to isolate dependencies from system-wide Python packages.
- Prevents unintended package conflicts and enhances security.

### 7️⃣ **Environment Variables Security**
- `DEBIAN_FRONTEND=noninteractive` is set to prevent interactive prompts and ensure automated builds.
- The `PATH` variable is modified to prioritize the virtual environment (`/opt/venv/bin`).

### 8️⃣ **Proper File & User Permissions**
- The application directory (`/app`) is owned by `appuser`, preventing unauthorized access by other system users.
- The `COPY --from=builder` command ensures only required files are transferred to the final image.

### 9️⃣ **Entry Point Security**
- Uses `ENTRYPOINT ["python3", "server.py"]` instead of `CMD`, Blocking attackers from overriding the cmd at runtime.


## Summary
This Dockerfile follows security best practices by **reducing attack surfaces, enforcing least privilege, and optimizing performance**. By implementing these enhancements, the resulting container is **secure, lightweight, and production-ready**.
# Secure CI Pipeline for Auth Service

## Objective
- Implement a security-focused CI pipeline to **ensure software quality, security, and compliance**.
- Use **JFrog Artifactory, XRay, Cosign, Hadolint, and Frogbot** to enhance **security** and **traceability**.

---

## Trigger: Why Pull Request Events?
```yaml
on:
  pull_request:
    branches:
      - main
```
- The pipeline runs **on every PR to `main`**, enforcing **security checks before merging**.
- This **prevents vulnerabilities and misconfigurations from reaching production**.

---

## 1️⃣ Step 1: Checkout Code
```yaml
- name: Checkout Code
  uses: actions/checkout@v4
```
- **Ensures we are working with the latest changes in the PR.**

---

## 2️⃣ Step 2: Python Setup & Unit Tests
```yaml
- name: Set Up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'

- name: Install Dependencies
  run: |
    pip install --upgrade pip
    pip install --no-cache-dir -r auth/requirements.txt

- name: Run Unit Tests
  run: pytest auth/test_server.py
```
- Sets up Python **in a reproducible environment**.
- Runs **unit tests** to verify core functionality **before building**.

---

## 3️⃣ Step 3: Security Scanning with Frogbot
```yaml
- name: Frogbot by JFrog  
  uses: jfrog/frogbot@v2.25.0
  env:
    JF_URL: ${{ vars.JF_URL }}
    JF_ACCESS_TOKEN: ${{ secrets.JF_ACCESS_TOKEN }}
    JF_GIT_TOKEN: ${{ secrets.JF_GIT_TOKEN }}
```
- **Scans dependencies and Git repository for vulnerabilities**.
- **Comments on the PR** with detected issues.

---

## 4️⃣ Step 4: Authenticate with JFrog Artifactory
```yaml
- name: Authenticate with JFrog Artifactory
  run: |
    echo "${{ secrets.JF_ACCESS_TOKEN }}" | docker login setompaz.jfrog.io --username "${{ secrets.JF_USER }}" --password-stdin
```
- **Required to pull and push artifacts securely**.

---

## 5️⃣ Step 5: Linting Dockerfile for Security Issues
```yaml
- name: Install Hadolint
  run: |
    curl -sSL https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 -o /usr/local/bin/hadolint
    chmod +x /usr/local/bin/hadolint

- name: Lint Dockerfile for Security Best Practices
  run: hadolint auth/Dockerfile
```
- **Prevents misconfigurations and detects security risks.**

---

## 6️⃣ Step 6: Build Docker Image & Generate SBOM
```yaml
- name: build Docker Image Before Scanning
  run: docker build -t $IMAGE_NAME ./auth

- name: Install Syft for SBOM Generation
  run: |
    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

- name: Generate SBOM (Software Bill of Materials)
  run: |
    syft $IMAGE_NAME -o json > sbom.json
    cat sbom.json

- name: Upload SBOM as an Artifact
  uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: sbom.json
```
- **Ensures software transparency and compliance.**

---

## 7️⃣ Step 7: XRay Vulnerability Scanning
```yaml
- name: Run XRay Scan Locally
  run: jf docker scan $IMAGE_NAME --output json > xray-scan-results.json

- name: Upload XRay Scan Results as an Artifact
  uses: actions/upload-artifact@v4
  with:
    name: xray-scan-results
    path: xray-scan-results.json

- name: Fail if Critical Vulnerabilities Exist
  run: |
    if grep -q '"severity": "Critical"' xray-scan-results.json; then
      echo "❌ Critical vulnerabilities found! Failing build..."
      exit 1
    fi
    echo "✅ No critical vulnerabilities found."
```
- **Fails build if critical vulnerabilities are found.**

---

## 8️⃣ Step 8: Secure Docker Build & Push
```yaml
- name: Enable Docker BuildKit & Secure Buildx
  run: |
    export DOCKER_BUILDKIT=1
    docker buildx create --use

- name: Build & Push Multi-Arch Secure Docker Image
  run: |
    jf docker login tompazus.jfrog.io
    jf docker buildx build --platform linux/amd64 \
      --tag $IMAGE_NAME \
      --file auth/Dockerfile \
      --push \
      auth/
```
- **Ensures cross-platform compatibility and optimized builds.**

---

## 9️⃣ Step 9: Sign Image with Cosign
```yaml
- name: Install Cosign for Image Signing
  run: |
    COSIGN_VERSION=$(curl -s "https://api.github.com/repos/sigstore/cosign/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")')
    wget "https://github.com/sigstore/cosign/releases/download/${COSIGN_VERSION}/cosign-linux-amd64"
    chmod +x cosign-linux-amd64
    sudo mv cosign-linux-amd64 /usr/local/bin/cosign
    cosign version

- name: Sign Docker Image with Cosign
  run: |
    echo "${{ secrets.COSIGN_PRIVATE_KEY }}" > cosign.key
    chmod 600 cosign.key
    cosign sign --key cosign.key --upload=true $IMAGE_NAME -y
```
- **Ensures image integrity & authenticity, preventing tampered deployments.**

---

## 🔟 Step 10: Publish Build Info & Final XRay Scan
```yaml
- name: Publish Build Info with JFrog CLI
  env:
    JFROG_CLI_BUILD_NAME: auth-build
    JFROG_CLI_BUILD_NUMBER: ${{ github.run_number }}
  run: |
    jf rt build-collect-env
    jf rt build-add-git
    jf rt build-publish

- name: Run XRay Vulnerability Scan and Attach to Build
  run: |
    jf rt build-scan auth-build ${{ github.run_number }}
```
- **Provides traceability and ensures no vulnerabilities before deployment.**

---

## 🌟 Summary of Security Enhancements
✔ **PR-Based Pipeline** → No insecure code reaches `main`.
✔ **Frogbot Scanning** → Identifies vulnerabilities before merge.
✔ **Dockerfile Linting** → Prevents misconfigurations.
✔ **SBOM Generation** → Enables software transparency.
✔ **XRay Scanning** → Fails build if vulnerabilities exist.
✔ **Signed Docker Images** → Prevents tampered deployments.
✔ **JFrog Artifactory Integration** → End-to-End security.

---

## 🚀 Conclusion: Why This Pipeline?
- **Automates security across the software supply chain.**
- **Prevents critical vulnerabilities from reaching production.**
- **Meets DevSecOps best practices for CI/CD.**

💡 **This approach ensures security is built-in from the start.** 🚀
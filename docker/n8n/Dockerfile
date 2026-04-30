FROM docker.n8n.io/n8nio/n8n:1.38.1

# Switch to root to install system deps
USER root

# --- System-level tools useful for AI + automation workflows ---
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    curl \
    jq \
    git \
    ca-certificates

# --- Python tooling ---
# NOTE: --break-system-packages is REQUIRED on Alpine (PEP 668)
RUN pip3 install --no-cache-dir --break-system-packages \
    requests

# Drop back to node user (important)
USER node
``
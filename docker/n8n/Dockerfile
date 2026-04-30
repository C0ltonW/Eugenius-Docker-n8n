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

# --- Optional Python tooling (keep minimal for now) ---
# You can add libs later as you need them
RUN pip3 install --no-cache-dir \
    requests

# Drop back to node user (important)
USER node

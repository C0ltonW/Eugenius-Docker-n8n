# Eugenius-Docker-n8n

A lightweight, profile-based Docker orchestration tool for running **n8n locally** with durable data, optional local AI services, and a clean, Python-driven workflow.

This project is designed for **local development only**. Each developer runs their own instance. There is no multi-user or shared environment.

---

## What This Is

- A **local n8n development environment**
- Durable across restarts (no lost workflows or credentials)
- Profile-based (core, ai, tools, heavy)
- AI-ready, but **not AI-locked**
- Simple Python orchestration (no Docker CLI sprawl)

---

## What This Is NOT

This project is **not**:

- A production / HA n8n deployment
- A multi-user setup
- A Kubernetes solution
- A queue-mode / Redis-backed cluster
- A hosted or managed service

The goal is **boring, predictable local development**.

---

## Requirements

- Docker Desktop (with Docker Compose v2)
- Python 3.9+
- (WSL users) Docker Desktop WSL integration enabled

---

## Quick Start

### 1. Clone the repo

```bash
git clone <repo-url>
cd n8n-orchestrator
```

> **WSL users:** clone into your Linux home directory  
> `/mnt/c/...`  
> `/home/<you>/...`

---

### 2. Create `.env`

```bash
cp templates/env.default .env
```

Fill in **only** these required values:

```env
N8N_ENCRYPTION_KEY=<openssl rand -hex 32>
POSTGRES_PASSWORD=<anything>
```

️ **Important:**  
Do **not** change `N8N_ENCRYPTION_KEY` once set.  
Changing it will make stored credentials unreadable.

---

### 3. Start n8n

```bash
./orch up
```

Access n8n at:

```
http://localhost:5678
```

---

## Profiles

Profiles control **what services exist**, not behavior.

| Profile | Services |
|------|---------|
| `core` | n8n + Postgres |
| `ai` | core + Ollama |
| `tools` | core + Adminer |
| `dev` | core + Ollama + Adminer |
| `heavy` | core + runtime tuning |

Example:

```bash
./orch --profile ai up
```

---

## Data Persistence

Data is persisted via **named Docker volumes**:

- Postgres stores workflows, executions, and credentials
- n8n config is persisted
- Binary data is stored on the filesystem

You can safely:
- stop containers
- rebuild images
- restart Docker

 **Data is not lost**

The **only** destructive command is:

```bash
./orch destroy --yes
```

---

## Custom n8n Image

This repo includes a minimal custom n8n image at:

```
docker/n8n/Dockerfile
```

This allows you to:
- add system dependencies
- use Python scripts in workflows
- extend later without refactoring

If the Dockerfile exists, it is used automatically.

---

## AI Usage (Important)

### AI Is Optional and Decoupled

This project **does not depend on Ollama**.

Ollama is included **only** as:
- a local testing AI
- a development convenience
- a replaceable sidecar

You are **not locked in**.

---

### How AI Is Accessed

n8n interacts with AI **via HTTP**, not plugins or custom nodes.

That means you can use:
- Ollama (local)
- OpenAI
- Azure OpenAI
- Anthropic
- Any internal or hosted model

No changes to orchestration are required.

---

### Ollama (Local Testing Only)

If you enable the `ai` or `dev` profile, Ollama runs locally at:

```
http://localhost:11434
```

From inside n8n, use:

```
http://host.docker.internal:11434
```

This works on:
- WSL + Docker Desktop
- macOS
- Linux

---

### Example Workflow

An example Ollama workflow is provided:

```
examples/ollama_http_example.json
```

This demonstrates:
- HTTP-based AI calls
- local model usage
- zero coupling to Ollama itself

You can import it directly into n8n.

---

## Binary / File Handling

This setup uses filesystem-based binary storage:

```
/files
```

This is intentional and recommended for:
- AI responses
- large payloads
- generated artifacts

The directory is backed by a Docker volume and is persistent.

---

## Common Commands

```bash
./orch up
./orch down
./orch logs
./orch ps
./orch destroy --yes
```

---

## License

MIT

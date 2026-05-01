# Security Policy

## Supported Scope

This project is intended for **local development and self-hosted environments**.
It is **not** designed to be exposed directly to the public internet without additional hardening.

## Security Assumptions

- Services are assumed to run on trusted networks
- Secrets are supplied via environment variables
- No automatic secrets rotation is provided

## Responsible Disclosure

If you discover a security vulnerability:

1. **Do not** open a public GitHub issue
2. Use GitHub Security Advisories or contact the maintainer privately

We will respond as quickly as possible.

## User Responsibility

Running this software in production environments is done **at your own risk**.
You are responsible for:

- Network security
- Authentication
- TLS termination
- Compliance and data protection requirements

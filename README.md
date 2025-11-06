# 🎁 Gift Registry Web App

A full-stack web app for creating and sharing gift registries for birthdays, weddings, and holidays.

## Features
- 👤 User registration & login (JWT)
- 🛍️ Create and share gift registries
- 🔍 Search gifts
- 🧾 Prevent duplicate purchases (atomic “buy” locks)
- 🌐 Shareable registry links
- 🐳 Dockerized for easy setup

---

This repository contains:
- FastAPI backend (Postgres, RabbitMQ, Redis, Celery, SendGrid)
- React + Tailwind frontend (Vite)
- Browser extension (Chrome/Edge/Firefox)
- GitHub Actions CI workflow
- Docker Compose for local/dev deployment

See `DEPLOYMENT_AND_SECRETS.md` for secrets and deployment checklist.

## Security & Deployment Checklist
- Configure production secrets (use Vault / GitHub Secrets): `JWT_SECRETS`, `JWT_CURRENT_KID`, `SENDGRID_API_KEY`, `RABBITMQ_URL`, `REDIS_URL`, `DATABASE_URL`
- Use Traefik or Nginx for TLS termination (HTTPS). Ensure HSTS, secure cookies, and Strict-Transport-Security headers.
- Register OAuth callback URIs for SSO providers to point to `https://api.YOURDOMAIN.com/api/oauth/<provider>/callback`
- Rotate JWT keys by adding a new `kid` entry and switching `JWT_CURRENT_KID`.
- Monitor Celery queues and RabbitMQ health; use KEDA or HPA in Kubernetes for autoscaling workers.

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

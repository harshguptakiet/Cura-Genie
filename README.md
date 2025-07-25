# CuraGenie: Production-Ready AI Genomics Platform

## Overview
CuraGenie is an AI-driven healthcare genomics platform delivering personalized health risk insights by integrating genomic data, clinical diagnostics, and ML-based disease detection. This monorepo contains all core services and shared utilities for the platform.

## Features
- Secure backend (Flask, SQLAlchemy, RBAC, audit logging, rate limiting)
- Real data integration (VCF/FASTQ parsing, S3 upload, PostgreSQL)
- Authentication (Firebase Auth)
- Frontend (Next.js + Chakra UI): dashboards, risk scores, recommendations, alerts, consent management
- Monitoring: Prometheus, Grafana dashboards
- Centralized logging: ELK stack (Elasticsearch + Kibana)
- Responsive, accessible UI/UX
- CI/CD pipeline (GitHub Actions)
- Dockerized deployment

## Quick Start
1. Clone the repo and install Docker.
2. Run `docker-compose up` to start backend, frontend, database, Prometheus, Grafana, Elasticsearch, and Kibana.
3. Access:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:5000
   - Grafana: http://localhost:3001
   - Kibana: http://localhost:5601
4. Log in with Firebase Auth (see `.env` for config).
5. Upload genomic data, view risk scores, recommendations, and system metrics.

## Monitoring & Logging
- Prometheus scrapes backend metrics (`/metrics` endpoint).
- Grafana dashboards visualize metrics and logs.
- Backend logs are shipped to Elasticsearch for search/analysis in Kibana.

## Security & Compliance
- All sensitive actions are logged and rate-limited.
- Role-based access control (RBAC) for endpoints.
- Consent management for data/ML features.
- Secrets/configs via environment variables.

## Development & Testing
- Frontend: Next.js + Chakra UI, responsive and accessible.
- Backend: Flask, modular API endpoints, real data integration.
- Run tests: `pytest` in backend, `npm test` in frontend.

## Deployment
- Docker Compose for local orchestration.
- Ready for cloud deployment (AWS/GCP/Azure).
- CI/CD via GitHub Actions.

## Onboarding
- See code comments and API docs for endpoint usage.
- Use provided dashboards for monitoring and troubleshooting.
- All main pages are responsive and accessible.

## Contact & Support
- For issues, open a GitHub issue or contact the maintainer.

---

CuraGenie is designed for secure, scalable, and compliant healthcare genomics applications. All best practices for production, monitoring, logging, and user experience are integrated.

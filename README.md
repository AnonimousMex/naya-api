# NAYÁ — API

Backend FastAPI del proyecto Nayá: una app de seguimiento emocional para niños,
con vistas diferenciadas para terapeutas y tutores.

## Stack

- **API**: FastAPI 0.115 + SQLModel + Alembic
- **Base de datos**: PostgreSQL
- **Cache/colas**: Redis
- **Observabilidad**:
  - **Prometheus** + **Grafana** para métricas (HTTP + custom de dominio)
  - **Sentry** para captura de errores con scrubbing de PII
  - Logs estructurados JSON con `request_id` propagado por contextvars
- **CI/CD**: GitHub Actions (tests, build, scan, deploy)
- **Tests**: pytest (87 unit tests)

## Quick start

```bash
# Levantar todo (Postgres, Redis, FastAPI, Prometheus, Grafana, pgAdmin)
make up

# Aplicar migraciones y sembrar datos
make migrate
make seed

# Listo. Servicios:
# - API:        http://localhost:8000/docs
# - Métricas:   http://localhost:8000/metrics
# - Prometheus: http://localhost:9090
# - Grafana:    http://localhost:3000  (admin/admin)
```

Ver `make help` para todos los comandos disponibles.

## CI/CD Pipeline

El pipeline de GitHub Actions está organizado en tres workflows con
**múltiples fases en paralelo** para feedback rápido:

### `🧪 CI - Backend Tests` (corre en cada push y PR)

```
        ┌─→ 🎨 Lint (ruff)
        │
push ───┼─→ 🔒 Security scan (bandit + pip-audit)        ┐
        │                                                ├─→ 📊 CI Summary
        ├─→ 🧪 Unit tests (pytest + coverage)            │
        │                                                │
        └─→ 🐳 Docker build verify                       ┘
```

### `🐳 Build & Publish Docker` (corre en push a `main` o `stage`)

```
                    ┌─→ 🛡️  Vulnerability scan (Trivy)
                    │
🏗️ Build & push ────┼─→ 📋 Generate SBOM (anchore)        ┐
                    │                                     ├─→ 📦 Release summary
                    └─→ 💨 Smoke test                     ┘
```

La imagen queda publicada en GHCR:
```bash
docker pull ghcr.io/anonimousmex/naya-api:latest
```

### `🚀 Deploy to Cloud Run` (manual, vía workflow_dispatch)

Despliegue selectivo a `staging` o `production` con secrets
provenientes de **GCP Secret Manager** — nunca de GitHub.

Detalles completos en [.github/CICD.md](.github/CICD.md).

## Estructura del proyecto

```
app/
├── api/              # Routers + controllers + services por dominio
│   ├── auth/
│   ├── patients/
│   ├── therapists/
│   ├── parents/
│   ├── activities/
│   ├── games/
│   └── test/         # Activity-results y métricas diferenciadas
├── core/             # Logger, settings, middleware, sentry, metrics
├── models/           # Modelos SQLModel compartidos
├── utils/            # Security, email
├── scripts/          # Seed de la BD
└── main.py           # Entry point FastAPI

tests/                # 87 unit tests (pytest)
migrations/           # Alembic
grafana/              # Dashboards y provisioning
prometheus/           # Configuración de scrape
```

## Convenciones

- **Branches**: `feat/<NNN>-<descripcion>`, `fix/<descripcion>`, `chore/<descripcion>`, `docs/<descripcion>`
- **Integration branch**: `stage` (los PRs de feature van acá primero)
- **Release**: `stage → main` para promover a producción
- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, etc.)

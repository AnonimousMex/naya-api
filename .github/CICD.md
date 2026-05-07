# CI/CD — Naya API

Pipeline real correspondiente al diagrama de arquitectura:

```
Push → GitHub → Actions ┬─→ pytest (tests.yml)
                        ├─→ build & push imagen (docker-publish.yml)
                        └─→ deploy a Cloud Run (deploy.yml, manual)
```

## Workflows

### 1. `tests.yml` — corre en cada push y PR
- Setup Python 3.11 + cache de pip.
- `pip install -r requirements.txt`.
- Inyecta variables dummy de `.env` para que `pydantic-settings` cargue.
- Corre `pytest tests/ -v`.
- Si los tests fallan, el workflow falla y el PR se bloquea.

**Branches**: `main`, `master`, `develop`.

### 2. `docker-publish.yml` — corre cuando los tests pasan en `main`
- Se dispara via `workflow_run` (espera a que `tests.yml` termine).
- Solo construye si los tests pasaron.
- Build multi-stage con Buildx + cache de capas en GHCR (`type=gha`).
- Push a `ghcr.io/<org>/<repo>` con tags:
  - `latest` (solo si está en branch default)
  - `<branch>` (ej. `main`)
  - `sha-<short>` (commit corto)
  - `vX.Y.Z` (si fue tag git)

**Permisos requeridos**: `packages: write` (ya está en el workflow). El token automático `GITHUB_TOKEN` basta — no necesitas crear un PAT.

### 3. `deploy.yml` — manual (workflow_dispatch)
- Despliega la imagen publicada a Google Cloud Run.
- Permite elegir environment (`staging` / `production`) y tag de imagen.
- Lee secrets sensibles (DB, JWT, Sentry, SMTP) desde **GCP Secret Manager**, NO desde GitHub.
- Despliegue automático en push a `main` está comentado en el workflow — descoméntalo cuando estés listo.

## Lo que necesitas hacer una sola vez

### A. Habilitar GHCR (cero configuración manual)
GHCR está activo por defecto en cualquier repo público. La primera vez que el workflow `docker-publish.yml` corra y publique una imagen:
1. La imagen aparece en `https://github.com/<tu-usuario>/<tu-repo>/pkgs/container/<repo>`.
2. Por defecto es **privada**. Si querés que sea pública, ve al package → Settings → Change visibility → Public.

Si tu repo es privado, el workflow funciona igual pero solo tú podrás pull la imagen autenticado.

### B. Configurar deploy a GCP Cloud Run (opcional, solo si querés desplegar de verdad)

#### B.1. En GCP Console
```bash
# 1. Crear proyecto (si no tienes)
gcloud projects create naya-api-prod --name="Naya API"

# 2. Habilitar APIs
gcloud services enable run.googleapis.com \
                       artifactregistry.googleapis.com \
                       secretmanager.googleapis.com \
  --project=naya-api-prod

# 3. Crear service account para el deploy
gcloud iam service-accounts create gh-deployer \
  --display-name="GitHub Actions Deployer" \
  --project=naya-api-prod

# 4. Darle los roles mínimos
PROJECT_ID=naya-api-prod
SA_EMAIL=gh-deployer@${PROJECT_ID}.iam.gserviceaccount.com

for role in run.admin iam.serviceAccountUser secretmanager.secretAccessor; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" --role="roles/$role"
done

# 5. Generar key JSON
gcloud iam service-accounts keys create ~/gh-deployer.json \
  --iam-account=$SA_EMAIL
```

#### B.2. En GitHub
Repo → **Settings** → **Secrets and variables** → **Actions** → New repository secret:

| Secret | Valor |
|---|---|
| `GCP_SA_KEY` | Pegar contenido completo de `~/gh-deployer.json` |

#### B.3. Crear los secrets de la app en GCP Secret Manager
```bash
echo -n "<password real>" | gcloud secrets create naya-db-password --data-file=- --project=$PROJECT_ID
echo -n "<jwt secret 32+ bytes>" | gcloud secrets create naya-jwt-secret --data-file=- --project=$PROJECT_ID
# ...y así todos los demás (DB_USER, DB_HOST, REDIS_*, SMTP_*, SENTRY_DSN, etc.)
```

#### B.4. Disparar el deploy
GitHub repo → **Actions** → **🚀 Deploy to Cloud Run** → **Run workflow** → elegir environment.

## Validación local del workflow de tests

Corré la misma suite que correrá GitHub Actions:

```bash
docker compose exec fastapi pytest tests/ -v
```

Si pasa local, pasará en CI (es la misma versión de Python y las mismas deps).

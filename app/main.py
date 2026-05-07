from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from app.api.games.detectiveEmociones.detective_router import detective_router
from app.api.games.memociones.memociones_router import memociones_router
from app.api.energies.energy_router import energy_router
from app.api.patients.patient_router import patients_router
from app.api.test.test_router import test_router
from app.api.therapists.therapist_router import therapist_router
from app.api.animals.animal_router import animals_router
from app.api.games.game_router import game_router
from app.api.games.y_ese_ruido.y_ese_ruido_router import y_ese_ruido_router
from app.api.specialties.specialty_router import specialty_router
from app.api.professional_experience.professional_experience_router import professional_experience_router
from app.api.parents.parent_router import parent_router

from .core import metrics
from .core.database import engine
from .core.logger import logger
from .core.middleware import RequestContextMiddleware
from .core.sentry import init_sentry
from .core.settings import settings

# Sentry debe inicializarse lo antes posible en el ciclo de vida de la app.
# Es no-op silencioso si SENTRY_DSN está vacío.
_sentry_active = init_sentry()
if _sentry_active:
    logger.info(
        "sentry.initialized",
        extra={
            "event": "sentry.initialized",
            "environment": settings.SENTRY_ENVIRONMENT,
            "traces_sample_rate": settings.SENTRY_TRACES_SAMPLE_RATE,
        },
    )

from .api.auth.auth_router import auth_router
from .api.badges.badge_router import badge_router
from .api.test.activity_results_router import activity_results_router

# Imports defensivos para registrar modelos en SQLAlchemy metadata antes
# de que se compile cualquier mapper. Sin esto, relationships con
# back_populates a clases no cargadas hacen que el mapper falle al primer
# uso (síntoma: requests cuelgan cuando se inicializa el mapper de Emotion).
from app.api.activities.activity_model import ActivityModel  # noqa: F401, E402
from app.api.parents.parent_model import ParentChildModel  # noqa: F401, E402
from app.api.pictures.picture_animal_emotion_model import (  # noqa: F401, E402
    PictureAnimalEmotionModel,
)
from app.api.pictures.picture_model import PictureModel  # noqa: F401, E402


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # startup
    logger.info("app.startup", extra={"event": "app.startup", "project": settings.PROJECT_NAME})
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("db.ready", extra={"event": "db.ready"})
    except Exception as e:
        metrics.DB_CONNECTION_ERRORS.inc()
        logger.error(
            "db.connection_failed",
            extra={"event": "db.connection_failed", "error": str(e)},
            exc_info=True,
        )
    metrics.API_UP.set(1)
    yield
    # shutdown
    metrics.API_UP.set(0)
    logger.info("app.shutdown", extra={"event": "app.shutdown"})


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1}/openapi.json",
    lifespan=lifespan,
)

# Middleware (orden: CORS más afuera, contexto/log más adentro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)

# Prometheus: histogram con buckets adaptados a APIs web; expone /metrics
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.get("/version", tags=["Diagnostics"])
async def get_version():
    """Devuelve metadatos del despliegue actual (útil para health checks
    y para verificar qué versión/commit está corriendo en cada ambiente)."""
    return {
        "project": settings.PROJECT_NAME,
        "environment": settings.SENTRY_ENVIRONMENT,
        "release": settings.SENTRY_RELEASE or "unspecified",
    }


@app.get("/sentry-debug", include_in_schema=False)
async def sentry_debug():
    """
    Endpoint de validación: provoca una división por cero para confirmar
    que Sentry captura el evento. Disponible siempre que SENTRY_ENVIRONMENT
    no sea "production". En production responde 404 para no exponerlo.
    """
    if (settings.SENTRY_ENVIRONMENT or "").lower() == "production":
        raise HTTPException(status_code=404)
    division_by_zero = 1 / 0  # noqa: F841 — provoca ZeroDivisionError a propósito
    return {"status": "unreachable"}


# Router con varios tipos de errores de prueba (solo no-prod).
if (settings.SENTRY_ENVIRONMENT or "").lower() != "production":
    from .core.sentry_debug import sentry_debug_router
    app.include_router(sentry_debug_router)


app.include_router(patients_router, prefix=settings.API_V1, tags=["Patients"])
app.include_router(therapist_router, prefix=settings.API_V1, tags=["Therapist"])
app.include_router(animals_router, prefix=settings.API_V1, tags=["Animals"])
app.include_router(memociones_router, prefix=settings.API_V1, tags=["MEMOCIONES"])
app.include_router(game_router, prefix=settings.API_V1, tags=["Games"])
app.include_router(energy_router, prefix=settings.API_V1, tags=["Energy"])
app.include_router(test_router, prefix=settings.API_V1, tags=["Test"])
app.include_router(detective_router, prefix=settings.API_V1, tags=["Detective"])
app.include_router(y_ese_ruido_router, prefix=settings.API_V1, tags=["YEseRuido"])
app.include_router(badge_router, prefix=settings.API_V1, tags=["Badges"])
app.include_router(specialty_router, prefix=settings.API_V1, tags=["Specialties"])
app.include_router(professional_experience_router, prefix=settings.API_V1, tags=["Professional Experience"])
app.include_router(parent_router, prefix=settings.API_V1, tags=["Parents"])

app.include_router(auth_router, prefix=settings.API_V1, tags=["Auth"])
app.include_router(activity_results_router, prefix=settings.API_V1, tags=["Activity Results"])

import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

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

from .core.settings import settings

from .api.auth.auth_router import auth_router
from .api.badges.badge_router import badge_router
from sqlalchemy.engine.url import make_url


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)
# main.py (abajo)
@app.get("/health")
def health():
    return {"status": "ok"}
@app.get("/debug/db")
def debug_db():
    url = make_url(settings.DATABASE_URL_EFFECTIVE)
    return {
        "driver": url.drivername,
        "host": url.host,
        "port": url.port,
        "database": url.database,
        "sslmode": "require" if "sslmode=require" in str(url) else "?"
    }
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        traceback.print_exc()  # se imprime en logs de Render
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "detail": str(e)},
        )

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

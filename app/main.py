from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.games.memociones.memociones_router import memociones_router
from app.api.energies.energy_router import energy_router
from app.api.patients.patient_router import patients_router
from app.api.test.test_router import test_router
from app.api.therapists.therapist_router import therapist_router
from app.api.animals.animal_router import animals_router
from app.api.games.game_router import game_router
from app.api.games.y_ese_ruido.y_ese_ruido_router import y_ese_ruido_router

from .core.settings import settings

from app.api.patients.patient_router import patients_router
from .api.auth.auth_router import auth_router
from .api.badges.badge_router import badge_router


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


app.include_router(patients_router, prefix=settings.API_V1, tags=["Patients"])
app.include_router(therapist_router, prefix=settings.API_V1, tags=["Therapist"])
app.include_router(animals_router, prefix=settings.API_V1, tags=["Animals"])
app.include_router(memociones_router, prefix=settings.API_V1, tags=["MEMOCIONES"])
app.include_router(game_router, prefix=settings.API_V1, tags=["Games"])
app.include_router(energy_router, prefix=settings.API_V1, tags=["Energy"])
app.include_router(test_router, prefix=settings.API_V1, tags=["Test"])
app.include_router(y_ese_ruido_router, prefix=settings.API_V1, tags=["YEseRuido"])
app.include_router(badge_router, prefix=settings.API_V1, tags=["Badges"])

app.include_router(auth_router, prefix=settings.API_V1, tags=["Auth"])

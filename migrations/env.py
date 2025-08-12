# migrations/env.py
from logging.config import fileConfig
import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# IMPORTA settings desde tu app
from app.core.settings import settings

# Importa TODOS los modelos para que entren al metadata
from app.models.user_model import UserModel
from app.api.therapists.therapist_model import TherapistModel
from app.api.animals.animal_model import AnimalModel
from app.api.patients.patient_model import PatientModel
from app.api.auth.auth_model import VerificationCodeModel, ConnectionModel
from app.api.pictures.picture_model import PictureModel
from app.api.pictures.picture_animal_emotion_model import PictureAnimalEmotionModel
from app.api.emotions.emotion_model import (
    EmotionModel,
    TestVeredictModel,
    VeredictModel,
    TestAnswerModel,
    AnswerModel,
    StoryModel,
    EmotionResultsModel,
    EmotionDescriptionModel,
    SituationModel,
)
from app.api.test.questions_model import QuestionModel
from app.api.test.test_model import TestModel
from app.api.specialties.specialty_model import SpecialtyModel, SpecialtyTherapistModel
from app.api.professional_experience.professional_experience_model import ProfessionalExperienceModel
from app.models.game_model import GameModel
from app.models.game_history_archivements_model import GameHistoryAchievementsModel
from app.api.energies.energy_model import EnergyModel
from app.api.advices.advice_model import AdviceModel
from app.api.advices.advices_show_model import AdvicesShownModel
from app.api.activities.activity_model import ActivityModel
from pathlib import Path
from dotenv import load_dotenv

# Carga el .env desde el root del proyecto
ROOT_DIR = Path(__file__).resolve().parents[1]  # carpeta del repo
load_dotenv(ROOT_DIR / ".env")
# --- util: asegurar sslmode=require en la URL ---
def ensure_sslmode_require(db_url: str) -> str:
    """
    Asegura que la URL tenga sslmode=require.
    Preserva otros query params si ya existen.
    """
    parsed = urlparse(db_url)
    q = dict(parse_qsl(parsed.query)) if parsed.query else {}
    if q.get("sslmode") != "require":
        q["sslmode"] = "require"
    new_query = urlencode(q)
    return urlunparse(parsed._replace(query=new_query))

# Usa la URL desde settings y normalízala
database_url = os.getenv("DATABASE_URL", "").strip()
if not database_url:
    # intenta leer desde settings si lo tienes implementado
    # OJO: si settings.DATABASE_URL es una propiedad que arma con DB_*
    # te devolverá el host del contenedor, no Supabase.
    try:
        database_url = getattr(settings, "DATABASE_URL", "") or getattr(settings, "DATABASE_URL_EFFECTIVE", "")
    except Exception:
        database_url = ""

if not database_url:
    raise RuntimeError("DATABASE_URL no configurada. Exporta la URL de Supabase o configúrala en .env.")
database_url = ensure_sslmode_require(database_url)

# Alembic config
config = context.config
# fuerza la URL en runtime (alembic.ini puede quedar vacío)
config.set_main_option("sqlalchemy.url", database_url)

# Logging desde alembic.ini (opcional)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Migrations en 'offline' (sin engine)."""
    url = config.get_main_option("sqlalchemy.url")
    url = ensure_sslmode_require(url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,          # útil para detectar cambios de tipos
        compare_server_default=True # útil para defaults
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Migrations en 'online' (con engine/connection)."""
    section = config.get_section(config.config_ini_section, {}) or {}
    # engine_from_config permite pasar connect_args aquí:
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"sslmode": "require"},
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

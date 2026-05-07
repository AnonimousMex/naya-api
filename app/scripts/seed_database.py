"""
Seed completo de la BD con datos variados para nutrir métricas.

Idempotente: usa upserts por columna única (email, name, etc). Se puede
ejecutar varias veces sin duplicar.

Uso:
    docker compose exec fastapi python -m app.scripts.seed_database
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from uuid import uuid4, UUID

from sqlmodel import Session, select

from app.api.activities.activity_model import ActivityModel
from app.api.animals.animal_model import AnimalModel
from app.api.auth.auth_model import AdviceModel, ConnectionModel
from app.api.badges.badge_model import BadgeModel, UserBadgeModel
from app.api.emotions.emotion_model import (
    AnswerModel,
    EmotionDescriptionModel,
    EmotionModel,
    SituationModel,
    StoryModel,
    TestAnswerModel,
)
from app.api.energies.energy_model import EnergyModel
from app.api.games.y_ese_ruido.y_ese_ruido_model import (
    SoundsGameCluesModel,
    SoundsGameSoundsModel,
)
from app.api.parents.parent_model import ParentChildModel
from app.api.patients.patient_model import PatientModel
from app.api.pictures.picture_animal_emotion_model import PictureAnimalEmotionModel
from app.api.pictures.picture_model import PictureModel
from app.api.professional_experience.professional_experience_model import (
    ProfessionalExperienceModel,
)
from app.api.specialties.specialty_model import SpecialtyModel, SpecialtyTherapistModel
from app.api.test.questions_model import QuestionModel
from app.api.test.test_model import TestModel
from app.api.therapists.therapist_model import TherapistModel
from app.constants.user_constants import (
    ActivityTypes,
    CopingCategories,
    TriggerCategories,
    UserRoles,
)
from app.core.database import engine
from app.core.logger import logger
from app.models.game_history_archivements_model import GameHistoryAchievementsModel
from app.models.game_model import GameModel
from app.models.user_model import UserModel
from app.utils.security import get_password_hash


# Para que el seed sea reproducible
random.seed(42)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _get_or_create(session: Session, model, defaults: Optional[dict] = None, **kwargs):
    stmt = select(model)
    for k, v in kwargs.items():
        stmt = stmt.where(getattr(model, k) == v)
    instance = session.exec(stmt).first()
    if instance:
        return instance, False
    data = {**(defaults or {}), **kwargs}
    instance = model(**data)
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance, True


# ----------------------------------------------------------------------
# Seeders
# ----------------------------------------------------------------------


def seed_emotions(session: Session) -> Dict[str, EmotionModel]:
    # EmotionModel re-declara id sin default_factory, así que lo proveemos.
    names = ["Miedo", "Tristeza", "Felicidad", "Enojo", "Vergüenza"]
    out = {}
    for n in names:
        e, _ = _get_or_create(session, EmotionModel, name=n, defaults={"id": uuid4()})
        out[n] = e
    # descripciones
    descriptions = {
        "Miedo": "Emoción de alerta y autoprotección.",
        "Tristeza": "Emoción asociada a la pérdida o desconexión.",
        "Felicidad": "Emoción de bienestar y plenitud.",
        "Enojo": "Emoción que aparece ante un límite traspasado.",
        "Vergüenza": "Emoción autoevaluativa sobre la propia conducta.",
    }
    for name, e in out.items():
        existing = session.exec(
            select(EmotionDescriptionModel).where(
                EmotionDescriptionModel.emotion_id == e.id
            )
        ).first()
        if not existing:
            session.add(
                EmotionDescriptionModel(
                    id=uuid4(), emotion_id=e.id, description=descriptions[name]
                )
            )
    session.commit()
    return out


def seed_animals(session: Session) -> List[AnimalModel]:
    rows = [
        ("Leon", "Valentía", "#FFB347", "lion"),
        ("Conejo", "Curiosidad", "#FFD1DC", "rabbit"),
        ("Tortuga", "Paciencia", "#77DD77", "turtle"),
        ("Zorro", "Astucia", "#FFA07A", "fox"),
        ("Búho", "Sabiduría", "#B19CD9", "owl"),
    ]
    animals = []
    for name, desc, color, key in rows:
        a, _ = _get_or_create(
            session,
            AnimalModel,
            name=name,
            defaults={"description": desc, "color_ui": color, "animal_key": key},
        )
        animals.append(a)
    return animals


def seed_pictures_and_emotion_pictures(session: Session, animals, emotions):
    # 1 picture base por animal/emoción
    for animal in animals:
        for emotion in emotions.values():
            pic, _ = _get_or_create(
                session,
                PictureModel,
                picture=f"https://cdn.naya.local/{animal.animal_key}/{emotion.name.lower()}.png",
                defaults={"is_profile": False},
            )
            existing = session.exec(
                select(PictureAnimalEmotionModel).where(
                    PictureAnimalEmotionModel.id_picture == pic.id,
                    PictureAnimalEmotionModel.id_animal == animal.id,
                    PictureAnimalEmotionModel.id_emotion == emotion.id,
                )
            ).first()
            if not existing:
                session.add(
                    PictureAnimalEmotionModel(
                        id_picture=pic.id, id_animal=animal.id, id_emotion=emotion.id
                    )
                )
    session.commit()


def seed_activities(session: Session) -> List[ActivityModel]:
    """
    Activities incluyen mindfulness exercises Y los 3 juegos como activities
    espejo (con UUIDs deterministas) para que el frontend pueda etiquetar
    `activity_id` al registrar resultados desde un juego.
    """
    # UUIDs deterministas de los juegos — exportados a CREDENTIALS.md.
    # El frontend los puede hardcodear como constantes.
    rows = [
        # Mindfulness exercises (UUIDs aleatorios)
        (None, "Respira", "Ejercicio de respiración", ActivityTypes.AUDITORY),
        (None, "Mira y Escucha", "Atención plena", ActivityTypes.VISUAL),
        (None, "Mueve el cuerpo", "Movimiento expresivo", ActivityTypes.KINESTESICO),
        # Activities espejo de juegos (UUIDs estables)
        (
            UUID("11111111-1111-1111-1111-111111111111"),
            "Memociones",
            "Juego de memoria emocional",
            ActivityTypes.VISUAL,
        ),
        (
            UUID("22222222-2222-2222-2222-222222222222"),
            "Detective",  # title.max_length = 20
            "Identificar la emoción en una situación",
            ActivityTypes.VISUAL,
        ),
        (
            UUID("33333333-3333-3333-3333-333333333333"),
            "Y Ese Ruido",
            "Reconocer la emoción a partir de un sonido",
            ActivityTypes.AUDITORY,
        ),
    ]
    out = []
    for fixed_id, title, desc, t in rows:
        defaults = {
            "description": desc,
            "image_url": f"https://cdn.naya.local/activities/{title}.png",
            "type": t,
        }
        if fixed_id is not None:
            defaults["id"] = fixed_id
        a, _ = _get_or_create(session, ActivityModel, title=title, defaults=defaults)
        out.append(a)
    return out


def seed_games(session: Session) -> List[GameModel]:
    rows = [
        ("Memociones", "Juego de memoria emocional"),
        ("Detective", "Detective de emociones"),
        ("Y Ese Ruido", "Identifica el sonido"),
    ]
    out = []
    for name, desc in rows:
        g, _ = _get_or_create(
            session,
            GameModel,
            name=name,
            defaults={
                "description": desc,
                "image_url": f"https://cdn.naya.local/games/{name}.png",
            },
        )
        out.append(g)
    return out


def seed_advices(session: Session) -> List[AdviceModel]:
    rows = [
        ("Respira hondo", "Tres respiraciones profundas pueden bajar la ansiedad."),
        ("Habla con alguien", "Compartir lo que sientes ayuda a procesarlo."),
        ("Camina 5 min", "Mover el cuerpo regula el estrés."),
        ("Dibuja tu día", "Expresar con dibujo libera tensión."),
        ("Toma agua", "La hidratación apoya la regulación emocional."),
    ]
    out = []
    for title, desc in rows:
        a, _ = _get_or_create(
            session, AdviceModel, title=title, defaults={"description": desc}
        )
        out.append(a)
    return out


def seed_badges(session: Session) -> List[BadgeModel]:
    rows = [
        ("Primer paso", "Completaste tu primera actividad"),
        ("Constancia", "Completaste 7 actividades"),
        ("Maestro emocional", "Identificaste 5 emociones distintas"),
    ]
    out = []
    for title, desc in rows:
        b, _ = _get_or_create(
            session,
            BadgeModel,
            title=title,
            defaults={
                "description": desc,
                "image_path": f"/badges/{title.lower().replace(' ', '_')}.png",
            },
        )
        out.append(b)
    return out


def seed_specialties(session: Session) -> List[SpecialtyModel]:
    names = ["Infantil", "Adolescentes", "Familiar", "Trauma", "Ansiedad"]
    out = []
    for n in names:
        s, _ = _get_or_create(session, SpecialtyModel, name=n)
        out.append(s)
    return out


def seed_situations(session: Session, emotions: Dict[str, EmotionModel]) -> int:
    """
    Pobla `situations` (usadas por memociones via /api/v1/pairs).
    Crea 2 situaciones por emoción para que el juego pueda armar pares
    variados sin repetir.
    """
    rows = [
        ("Miedo", "Truenos en la noche", "Hay una tormenta y se va la luz."),
        ("Miedo", "Sombras en la pared", "Veo formas raras en mi cuarto."),
        ("Tristeza", "Día sin amigos", "Nadie quiso jugar conmigo en el recreo."),
        ("Tristeza", "Mascota perdida", "Mi gato no llegó a casa."),
        ("Felicidad", "Premio sorpresa", "Me regalaron lo que más quería."),
        ("Felicidad", "Visita inesperada", "Vinieron mis primos a jugar."),
        ("Enojo", "Juguete roto", "Mi hermano rompió mi juguete favorito."),
        ("Enojo", "Me interrumpieron", "Estaba contando algo y nadie me escuchó."),
        ("Vergüenza", "Mancha en la ropa", "Me manché frente a toda la clase."),
        ("Vergüenza", "Equivoqué la respuesta", "Dije algo mal frente a todos."),
    ]
    created = 0
    for emo_name, title, story in rows:
        emo = emotions.get(emo_name)
        if not emo:
            continue
        existing = session.exec(
            select(SituationModel).where(SituationModel.title == title)
        ).first()
        if existing:
            continue
        session.add(
            SituationModel(
                title=title,
                story=story,
                emotion_id=emo.id,
                image_url=f"https://cdn.naya.local/situations/{title.lower().replace(' ', '_')}.png",
            )
        )
        created += 1
    session.commit()
    return created


def seed_sounds(session: Session, emotions: Dict[str, EmotionModel]) -> int:
    """Pobla sounds_game_sounds + sounds_game_clues (usadas por /sounds)."""
    rows = [
        ("Miedo", "miedo_truenos.mp3", "Truenos", "Sonido de tormenta intensa.", "Respira profundo y cuenta a 5.", "tormenta"),
        ("Tristeza", "tristeza_lluvia.mp3", "Lluvia suave", "Lluvia constante en la ventana.", "Recuerda algo que te haga sonreír.", "lluvia"),
        ("Felicidad", "felicidad_risa.mp3", "Risa de niños", "Niños jugando y riendo.", "Sonríe y disfruta el sonido.", "risa"),
        ("Enojo", "enojo_golpes.mp3", "Golpes en la mesa", "Golpes secos y repetitivos.", "Cuenta a 10 antes de actuar.", "golpes"),
        ("Vergüenza", "verguenza_silencio.mp3", "Silencio incómodo", "Pausa larga en una conversación.", "Está bien sentir vergüenza, pasa pronto.", "silencio"),
    ]
    created = 0
    for emo_name, audio_path, title, body, tip, highlight in rows:
        emo = emotions.get(emo_name)
        if not emo:
            continue
        existing = session.exec(
            select(SoundsGameSoundsModel).where(
                SoundsGameSoundsModel.audio_path == audio_path
            )
        ).first()
        if existing:
            continue
        sound = SoundsGameSoundsModel(audio_path=audio_path, emotion_id=emo.id)
        session.add(sound)
        session.commit()
        session.refresh(sound)
        session.add(
            SoundsGameCluesModel(
                sound_id=sound.id,
                title=title,
                body=body,
                tip=tip,
                highlight=highlight,
            )
        )
        created += 1
    session.commit()
    return created


def seed_stories_and_questions(
    session: Session, emotions: Dict[str, EmotionModel]
) -> List[Tuple[StoryModel, List[QuestionModel]]]:
    """
    Crea una historia por emoción, con 2 preguntas (cada pregunta con un
    trigger_category diferente) y 3 answers por pregunta (cada answer con
    una emoción asociada y un score 1-5).
    """
    triggers_pool = list(TriggerCategories)
    catalog = []

    story_defs = [
        ("Una noche de tormenta", emotions["Miedo"], "Truenos despiertan al niño."),
        ("Día sin amigos", emotions["Tristeza"], "Nadie quiso jugar."),
        ("Premio sorpresa", emotions["Felicidad"], "Le dan un regalo inesperado."),
        ("Juguete roto", emotions["Enojo"], "Su hermano rompió el juguete."),
        ("Mancha en la ropa", emotions["Vergüenza"], "Una mancha frente a todos."),
    ]

    for title, emo, stage1 in story_defs:
        story, _ = _get_or_create(
            session,
            StoryModel,
            title=title,
            defaults={
                "stage_1": stage1,
                "stage_2": "El niño elige cómo afrontar la situación.",
                "image_url": f"https://cdn.naya.local/stories/{title.lower().replace(' ', '_')}.png",
                "emotion_id": emo.id,
            },
        )
        questions_for_story = []
        for i in range(2):
            trigger = triggers_pool[(story.title.__hash__() + i) % len(triggers_pool)]
            q, _ = _get_or_create(
                session,
                QuestionModel,
                story_id=story.id,
                question=f"¿Qué sientes cuando esto pasa? (#{i + 1})",
                defaults={"trigger_category": trigger.value},
            )
            # 3 respuestas por pregunta — cubren 3 emociones distintas para
            # producir distribuciones realistas
            answer_options = [
                (
                    f"Me asustan las sombras que se mueven en mi cuarto.",
                    emotions["Miedo"],
                    4,
                ),
                (f"Tengo miedo de estar solo.", emotions["Miedo"], 5),
                (
                    f"No quiero dormir si no dejan la luz prendida.",
                    emotions["Miedo"],
                    3,
                ),
                (f"Me siento triste cuando nadie me habla.", emotions["Tristeza"], 4),
                (f"Cuando juego con amigos me siento bien.", emotions["Felicidad"], 5),
                (f"Me enoja cuando me interrumpen.", emotions["Enojo"], 3),
                (f"Me da pena equivocarme frente a otros.", emotions["Vergüenza"], 2),
                (f"Ruidos fuertes me lastiman.", emotions["Miedo"], 3),
                (f"Cuando me abrazan me siento feliz.", emotions["Felicidad"], 5),
            ]
            for text, emo_obj, score in random.sample(answer_options, 3):
                _get_or_create(
                    session,
                    AnswerModel,
                    question_id=q.id,
                    answer_text=text,
                    defaults={"emotion_id": emo_obj.id, "score": score},
                )
            questions_for_story.append(q)
        catalog.append((story, questions_for_story))
    return catalog


def seed_users_and_roles(session: Session) -> dict:
    """Crea 2 terapeutas, 4 niños/pacientes y 2 tutores. Devuelve dict."""
    pwd_hash = get_password_hash("Password123")

    # therapists
    therapists = []
    for i, (name, email) in enumerate(
        [("ana", "ana.therapist@naya.local"), ("luis", "luis.therapist@naya.local")]
    ):
        u, _ = _get_or_create(
            session,
            UserModel,
            email=email,
            defaults={
                "name": name,
                "password": pwd_hash,
                "is_verified": True,
                "user_kind": UserRoles.THERAPIST,
            },
        )
        t, _ = _get_or_create(
            session,
            TherapistModel,
            user_id=u.id,
            defaults={
                "description": f"Terapeuta {name} con enfoque infantil.",
                "phone": f"55{i}1234567",
                "street": f"Av. {i + 1}",
                "city": "CDMX",
                "state": "CDMX",
                "postal_code": "01000",
                "code_conection": f"T{i:03d}",
            },
        )
        therapists.append((u, t))

    # patients (children) — el "user" del paciente representa al niño
    patients = []
    children_data = [
        ("sofia", "sofia.child@naya.local"),
        ("mateo", "mateo.child@naya.local"),
        ("valentina", "valentina.child@naya.local"),
        ("emiliano", "emiliano.child@naya.local"),
    ]
    for name, email in children_data:
        u, _ = _get_or_create(
            session,
            UserModel,
            email=email,
            defaults={
                "name": name,
                "password": pwd_hash,
                "is_verified": True,
                "user_kind": UserRoles.PATIENT,
            },
        )
        p, _ = _get_or_create(
            session,
            PatientModel,
            user_id=u.id,
            defaults={"is_connected": True},
        )
        patients.append((u, p))

    # parents (tutores)
    parents = []
    for name, email in [
        ("carla", "carla.parent@naya.local"),
        ("david", "david.parent@naya.local"),
    ]:
        u, _ = _get_or_create(
            session,
            UserModel,
            email=email,
            defaults={
                "name": name,
                "password": pwd_hash,
                "is_verified": True,
                "user_kind": UserRoles.PARENT,
            },
        )
        parents.append(u)

    return {"therapists": therapists, "patients": patients, "parents": parents}


def seed_relationships(session: Session, data: dict):
    """connections terapeuta↔niño y parent_child tutor↔niño."""
    therapists = data["therapists"]
    patients = data["patients"]
    parents = data["parents"]

    # Terapeuta 0 atiende a niños 0,1,2; terapeuta 1 atiende a 2,3
    pairs = [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)]
    for ti, pi in pairs:
        _, t = therapists[ti]
        _, p = patients[pi]
        existing = session.exec(
            select(ConnectionModel).where(
                ConnectionModel.therapist_id == t.id,
                ConnectionModel.patient_id == p.id,
            )
        ).first()
        if not existing:
            session.add(ConnectionModel(therapist_id=t.id, patient_id=p.id))
    session.commit()

    # Tutor 0 -> niños 0,1; tutor 1 -> niños 2,3
    parent_pairs = [(0, 0), (0, 1), (1, 2), (1, 3)]
    for pi, ci in parent_pairs:
        parent_user = parents[pi]
        _, child = patients[ci]
        existing = session.exec(
            select(ParentChildModel).where(
                ParentChildModel.parent_user_id == parent_user.id,
                ParentChildModel.patient_id == child.id,
            )
        ).first()
        if not existing:
            session.add(
                ParentChildModel(parent_user_id=parent_user.id, patient_id=child.id)
            )
    session.commit()


def seed_specialty_therapist(session: Session, therapists, specialties):
    for (_, t), s in zip(therapists, specialties[: len(therapists)]):
        existing = session.exec(
            select(SpecialtyTherapistModel).where(
                SpecialtyTherapistModel.id_therapist == t.id,
                SpecialtyTherapistModel.id_specialty == s.id,
            )
        ).first()
        if not existing:
            session.add(
                SpecialtyTherapistModel(id_therapist=t.id, id_specialty=s.id)
            )
    session.commit()


def seed_professional_experience(session: Session, therapists):
    for i, (_, t) in enumerate(therapists):
        existing = session.exec(
            select(ProfessionalExperienceModel).where(
                ProfessionalExperienceModel.id_therapist == t.id
            )
        ).first()
        if existing:
            continue
        session.add(
            ProfessionalExperienceModel(
                id_therapist=t.id,
                institute=f"Clínica Naya {i + 1}",
                position="Terapeuta infantil",
                period="2020 - Presente",
                activity="Atención a niños y adolescentes en regulación emocional.",
            )
        )
    session.commit()


def seed_energies(session: Session, patients):
    for u, _ in patients:
        existing = session.exec(
            select(EnergyModel).where(EnergyModel.user_id == u.id)
        ).first()
        if not existing:
            session.add(EnergyModel(user_id=u.id, current_energy=3, max_energy=3))
    session.commit()


def seed_user_badges(session: Session, patients, badges):
    for (u, _), b in zip(patients, badges):
        existing = session.exec(
            select(UserBadgeModel).where(
                UserBadgeModel.user_id == u.id, UserBadgeModel.badge_id == b.id
            )
        ).first()
        if not existing:
            session.add(UserBadgeModel(user_id=u.id, badge_id=b.id))
    session.commit()


def seed_game_history(session: Session, patients, games):
    for u, _ in patients:
        for g in games[:2]:
            session.add(
                GameHistoryAchievementsModel(
                    user_id=u.id,
                    game_id=g.id,
                    played_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                )
            )
    session.commit()


def seed_tests_and_answers(
    session: Session,
    patients,
    activities,
    catalog,
):
    """
    Para cada niño crea 8 tests distribuidos en los últimos 90 días con
    respuestas variadas. Las respuestas tienen sesgos por niño para producir
    perfiles emocionales distintos:
      - sofia: alto miedo
      - mateo: alta tristeza
      - valentina: feliz
      - emiliano: enojo + vergüenza
    """
    profile = {
        "sofia": {"Miedo": 0.55, "Tristeza": 0.2, "Felicidad": 0.1, "Enojo": 0.1, "Vergüenza": 0.05},
        "mateo": {"Miedo": 0.15, "Tristeza": 0.55, "Felicidad": 0.15, "Enojo": 0.1, "Vergüenza": 0.05},
        "valentina": {"Miedo": 0.1, "Tristeza": 0.1, "Felicidad": 0.6, "Enojo": 0.1, "Vergüenza": 0.1},
        "emiliano": {"Miedo": 0.1, "Tristeza": 0.1, "Felicidad": 0.1, "Enojo": 0.45, "Vergüenza": 0.25},
    }

    coping_pool = list(CopingCategories)

    answers_by_emotion: Dict[str, List[AnswerModel]] = {}
    for _, qs in catalog:
        for q in qs:
            ans_list = session.exec(
                select(AnswerModel).where(AnswerModel.question_id == q.id)
            ).all()
            for a in ans_list:
                emo = session.get(EmotionModel, a.emotion_id)
                answers_by_emotion.setdefault(emo.name, []).append(a)

    now = datetime.now(timezone.utc)
    test_count = 0
    answer_count = 0

    for u, p in patients:
        weights = profile.get(u.name, profile["sofia"])
        for i in range(8):
            days_ago = random.randint(0, 90)
            ts = now - timedelta(days=days_ago, hours=random.randint(0, 23))
            test = TestModel(
                user_id=u.id,
                activity_id=random.choice(activities).id,
                score=random.randint(40, 95),
                duration_seconds=random.randint(60, 600),
                completed_at=ts,
                created_at=ts,
                updated_at=ts,
            )
            session.add(test)
            session.commit()
            session.refresh(test)
            test_count += 1

            # 5 respuestas por test, ponderadas por el perfil del niño
            emotion_names = list(weights.keys())
            emotion_probs = list(weights.values())
            for _ in range(5):
                emo_name = random.choices(emotion_names, weights=emotion_probs, k=1)[0]
                pool = answers_by_emotion.get(emo_name, [])
                if not pool:
                    continue
                ans = random.choice(pool)
                session.add(
                    TestAnswerModel(
                        test_id=test.id,
                        answer_id=ans.id,
                        emotion_intensity=random.randint(40, 95),
                        coping_category=random.choice(coping_pool).value,
                    )
                )
                answer_count += 1
            session.commit()

    return test_count, answer_count


# ----------------------------------------------------------------------
# Entrada
# ----------------------------------------------------------------------


def run() -> dict:
    summary = {}
    with Session(engine) as session:
        emotions = seed_emotions(session)
        animals = seed_animals(session)
        seed_pictures_and_emotion_pictures(session, animals, emotions)
        activities = seed_activities(session)
        games = seed_games(session)
        advices = seed_advices(session)
        badges = seed_badges(session)
        specialties = seed_specialties(session)
        catalog = seed_stories_and_questions(session, emotions)
        situations_created = seed_situations(session, emotions)
        sounds_created = seed_sounds(session, emotions)
        users = seed_users_and_roles(session)
        seed_relationships(session, users)
        seed_specialty_therapist(session, users["therapists"], specialties)
        seed_professional_experience(session, users["therapists"])
        seed_energies(session, users["patients"])
        seed_user_badges(session, users["patients"], badges)
        seed_game_history(session, users["patients"], games)
        tests, answers = seed_tests_and_answers(
            session, users["patients"], activities, catalog
        )

        summary = {
            "emotions": len(emotions),
            "animals": len(animals),
            "activities": len(activities),
            "games": len(games),
            "advices": len(advices),
            "badges": len(badges),
            "specialties": len(specialties),
            "stories": len(catalog),
            "situations": situations_created,
            "sounds": sounds_created,
            "therapists": len(users["therapists"]),
            "patients": len(users["patients"]),
            "parents": len(users["parents"]),
            "tests": tests,
            "test_answers": answers,
        }

    logger.info("seed.completed", extra={"event": "seed.completed", "summary": summary})
    print("=== seed completado ===")
    for k, v in summary.items():
        print(f"  {k:18}: {v}")
    print("\nUsuarios de prueba (password: Password123):")
    print("  - ana.therapist@naya.local (THERAPIST)")
    print("  - luis.therapist@naya.local (THERAPIST)")
    print("  - sofia.child@naya.local (PATIENT)")
    print("  - mateo.child@naya.local (PATIENT)")
    print("  - valentina.child@naya.local (PATIENT)")
    print("  - emiliano.child@naya.local (PATIENT)")
    print("  - carla.parent@naya.local (PARENT)")
    print("  - david.parent@naya.local (PARENT)")
    return summary


if __name__ == "__main__":
    run()

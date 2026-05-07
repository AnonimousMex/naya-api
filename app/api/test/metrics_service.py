"""
Servicio de cálculo de métricas a partir de TestModel + TestAnswerModel.

Todas las funciones son puras (no escriben en DB): leen y devuelven dicts/dataclasses.
La fuente de verdad son las tablas tests/test_answer/answers/questions/emotions.

Para mantener separación: este módulo NO conoce HTTP ni autorización; eso vive
en el controller/router.
"""
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlmodel import Session, select

from app.api.emotions.emotion_model import (
    AnswerModel,
    EmotionModel,
    StoryModel,
    TestAnswerModel,
)
from app.api.patients.patient_model import PatientModel
from app.api.test.questions_model import QuestionModel
from app.api.test.test_model import TestModel

# Mapa de slug interno → label visible. Mantiene contrato estable aunque el
# usuario administre nombres de emociones en español en la DB.
EMOTION_SLUGS = {
    "Miedo": "fear",
    "Enojo": "anger",
    "Tristeza": "sadness",
    "Felicidad": "happiness",
    "Vergüenza": "shame",
    "Verguenza": "shame",
}

ALL_EMOTION_KEYS = ["fear", "anger", "sadness", "happiness", "shame"]
ALL_COPING_KEYS = ["avoidance", "frustration", "abandonment"]
ALL_TRIGGER_KEYS = ["self", "siblings", "friends", "father", "mother", "teachers"]

CLINICAL_DISCLAIMER = (
    "Estos resultados son indicadores generados a partir del uso de la "
    "aplicación y no representan un diagnóstico clínico."
)


def _emotion_slug(name: str) -> Optional[str]:
    if not name:
        return None
    return EMOTION_SLUGS.get(name.strip(), name.strip().lower())


def _to_pct(part: int, total: int) -> int:
    if total <= 0:
        return 0
    return round((part / total) * 100)


def _resolve_window(
    start: Optional[date], end: Optional[date]
) -> Tuple[datetime, datetime]:
    """Default: últimos 30 días (UTC)."""
    if end is None:
        end = datetime.now(timezone.utc).date()
    if start is None:
        start = end - timedelta(days=30)
    start_dt = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)
    end_dt = datetime.combine(end, datetime.max.time(), tzinfo=timezone.utc)
    return start_dt, end_dt


class MetricsService:
    @staticmethod
    def _get_user_id_from_patient(session: Session, patient_id: UUID) -> Optional[UUID]:
        patient = session.get(PatientModel, patient_id)
        return patient.user_id if patient else None

    @staticmethod
    def _load_answers(
        session: Session,
        *,
        user_id: UUID,
        start: datetime,
        end: datetime,
    ):
        """Devuelve filas (TestAnswer, Answer, Question, Emotion, Test) en la ventana."""
        stmt = (
            select(TestAnswerModel, AnswerModel, QuestionModel, EmotionModel, TestModel)
            .join(TestModel, TestModel.id == TestAnswerModel.test_id)
            .join(AnswerModel, AnswerModel.id == TestAnswerModel.answer_id)
            .join(QuestionModel, QuestionModel.id == AnswerModel.question_id)
            .join(EmotionModel, EmotionModel.id == AnswerModel.emotion_id)
            .where(TestModel.user_id == user_id)
            .where(TestModel.created_at >= start)
            .where(TestModel.created_at <= end)
        )
        return list(session.exec(stmt))

    # --- cálculos puros (públicos para reutilizar en tests/seed) ----------

    @staticmethod
    def emotion_percentages(answers_rows) -> Dict[str, int]:
        counter: Counter = Counter()
        total = 0
        for _, _, _, emotion, _ in answers_rows:
            slug = _emotion_slug(emotion.name) if emotion else None
            if slug:
                counter[slug] += 1
                total += 1
        out = {k: 0 for k in ALL_EMOTION_KEYS}
        for k in counter:
            out.setdefault(k, 0)
            out[k] = _to_pct(counter[k], total)
        return out

    @staticmethod
    def coping_percentages(answers_rows) -> Dict[str, int]:
        counter: Counter = Counter()
        total = 0
        for ta, _, _, _, _ in answers_rows:
            cat = (ta.coping_category or "").strip().lower()
            if cat in ALL_COPING_KEYS:
                counter[cat] += 1
                total += 1
        out = {k: 0 for k in ALL_COPING_KEYS}
        for k in counter:
            out[k] = _to_pct(counter[k], total)
        return out

    @staticmethod
    def trigger_percentages(answers_rows) -> Dict[str, int]:
        counter: Counter = Counter()
        total = 0
        for _, _, q, _, _ in answers_rows:
            cat = (q.trigger_category or "").strip().lower()
            if cat in ALL_TRIGGER_KEYS:
                counter[cat] += 1
                total += 1
        out = {k: 0 for k in ALL_TRIGGER_KEYS}
        for k in counter:
            out[k] = _to_pct(counter[k], total)
        return out

    @staticmethod
    def frequent_answers(answers_rows, limit: int = 5) -> List[str]:
        counter: Counter = Counter()
        for _, ans, _, _, _ in answers_rows:
            if ans and ans.answer_text:
                counter[ans.answer_text] += 1
        return [text for text, _ in counter.most_common(limit)]

    @staticmethod
    def weekly_evolution(answers_rows) -> List[Dict]:
        """Agrupa por ISO-week y devuelve % por emoción + total respuestas."""
        buckets: Dict[Tuple[int, int], List] = defaultdict(list)
        for ta, ans, q, emotion, test in answers_rows:
            iso_year, iso_week, _ = test.created_at.isocalendar()
            buckets[(iso_year, iso_week)].append((ta, ans, q, emotion, test))
        out = []
        for (year, week), rows in sorted(buckets.items()):
            out.append(
                {
                    "year": year,
                    "week": week,
                    "answers_count": len(rows),
                    "emotions": MetricsService.emotion_percentages(rows),
                }
            )
        return out

    @staticmethod
    def trend(emotions_pct: Dict[str, int], previous_pct: Optional[Dict[str, int]] = None) -> Dict:
        """
        Reglas de tendencia textual:
        - miedo > 50% → inseguridad / alerta
        - tristeza > 50% → aislamiento / baja motivación
        - enojo > 50% → frustración / desregulación
        - felicidad sube respecto al periodo anterior → mejora
        - default → estado emocional variado
        """
        title = "Estado emocional variado"
        description = (
            "El niño muestra una distribución equilibrada o variable de "
            "emociones durante el periodo analizado."
        )

        if emotions_pct.get("fear", 0) > 50:
            title = "Tendencia a la inseguridad y alerta constante"
            description = (
                "El niño muestra una mayor frecuencia de respuestas asociadas "
                "al miedo, la inseguridad y la necesidad de acompañamiento."
            )
        elif emotions_pct.get("sadness", 0) > 50:
            title = "Tendencia a aislamiento o baja motivación"
            description = (
                "Las respuestas se concentran en estados de tristeza, lo que "
                "puede sugerir baja motivación o dificultad para conectar."
            )
        elif emotions_pct.get("anger", 0) > 50:
            title = "Tendencia a frustración o dificultad para regular emociones"
            description = (
                "Predominan respuestas asociadas al enojo, sugiriendo retos en "
                "la regulación emocional."
            )
        elif (
            previous_pct
            and emotions_pct.get("happiness", 0) > previous_pct.get("happiness", 0)
        ):
            title = "Mejora en el estado emocional reportado"
            description = (
                "Comparado con el periodo anterior, el niño reporta más "
                "respuestas asociadas a la felicidad."
            )

        return {
            "title": title,
            "description": description,
            "clinical_note": CLINICAL_DISCLAIMER,
        }

    # --- vistas agregadas para terapeuta y tutor ---------------------------

    @staticmethod
    def therapist_metrics(
        session: Session,
        *,
        child_id: UUID,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> Dict:
        user_id = MetricsService._get_user_id_from_patient(session, child_id)
        if not user_id:
            return {}
        start_dt, end_dt = _resolve_window(start, end)
        rows = MetricsService._load_answers(
            session, user_id=user_id, start=start_dt, end=end_dt
        )

        # Periodo previo (mismo tamaño) para detectar mejora
        prev_start = start_dt - (end_dt - start_dt)
        prev_rows = MetricsService._load_answers(
            session, user_id=user_id, start=prev_start, end=start_dt
        )

        emotions = MetricsService.emotion_percentages(rows)
        coping = MetricsService.coping_percentages(rows)
        triggers = MetricsService.trigger_percentages(rows)
        frequent = MetricsService.frequent_answers(rows)
        evolution = MetricsService.weekly_evolution(rows)
        trend = MetricsService.trend(
            emotions, MetricsService.emotion_percentages(prev_rows)
        )

        return {
            "child_id": str(child_id),
            "period": {
                "start": start_dt.date().isoformat(),
                "end": end_dt.date().isoformat(),
            },
            "answers_count": len(rows),
            "emotional_statistics": emotions,
            "coping_statistics": coping,
            "emotional_triggers": triggers,
            "frequent_answers": frequent,
            "weekly_evolution": evolution,
            "trend": trend,
            "disclaimer": CLINICAL_DISCLAIMER,
        }

    @staticmethod
    def tutor_progress(
        session: Session,
        *,
        child_id: UUID,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> Dict:
        user_id = MetricsService._get_user_id_from_patient(session, child_id)
        if not user_id:
            return {}
        start_dt, end_dt = _resolve_window(start, end)
        rows = MetricsService._load_answers(
            session, user_id=user_id, start=start_dt, end=end_dt
        )

        emotions = MetricsService.emotion_percentages(rows)
        if emotions:
            main_key = max(emotions, key=lambda k: emotions[k]) if emotions else "happiness"
            main_pct = emotions.get(main_key, 0)
        else:
            main_key, main_pct = "happiness", 0

        completed = (
            session.exec(
                select(TestModel)
                .where(TestModel.user_id == user_id)
                .where(TestModel.created_at >= start_dt)
                .where(TestModel.created_at <= end_dt)
            )
        )
        completed_count = sum(1 for _ in completed)

        # Mensaje amigable derivado de la tendencia técnica
        technical_trend = MetricsService.trend(emotions)
        friendly = _friendly_trend(emotions, technical_trend)

        return {
            "child_id": str(child_id),
            "period": {
                "start": start_dt.date().isoformat(),
                "end": end_dt.date().isoformat(),
            },
            "summary": {
                "main_emotion": _emotion_label_es(main_key),
                "main_emotion_percentage": main_pct,
                "completed_activities": completed_count,
                "progress_status": _progress_status(emotions, completed_count),
            },
            "emotional_progress": emotions,
            "child_trend": friendly,
            "recommendation": _recommendation(emotions),
            "frequent_phrases": MetricsService.frequent_answers(rows, limit=3),
            "disclaimer": CLINICAL_DISCLAIMER,
        }

    @staticmethod
    def activity_history(session: Session, *, child_id: UUID) -> List[Dict]:
        user_id = MetricsService._get_user_id_from_patient(session, child_id)
        if not user_id:
            return []
        stmt = (
            select(TestModel)
            .where(TestModel.user_id == user_id)
            .order_by(TestModel.created_at.desc())
        )
        tests = list(session.exec(stmt))
        out = []
        for t in tests:
            # Emoción dominante de este test
            stmt_emo = (
                select(EmotionModel.name)
                .join(AnswerModel, AnswerModel.emotion_id == EmotionModel.id)
                .join(TestAnswerModel, TestAnswerModel.answer_id == AnswerModel.id)
                .where(TestAnswerModel.test_id == t.id)
            )
            names = list(session.exec(stmt_emo))
            main_emotion = Counter(names).most_common(1)
            out.append(
                {
                    "test_id": str(t.id),
                    "activity_id": str(t.activity_id) if t.activity_id else None,
                    "date": (t.completed_at or t.created_at).isoformat(),
                    "score": t.score,
                    "duration_seconds": t.duration_seconds,
                    "main_emotion": main_emotion[0][0] if main_emotion else None,
                }
            )
        return out


def _emotion_label_es(slug: str) -> str:
    return {
        "fear": "Miedo",
        "anger": "Enojo",
        "sadness": "Tristeza",
        "happiness": "Felicidad",
        "shame": "Vergüenza",
    }.get(slug, slug.title())


def _progress_status(emotions: Dict[str, int], completed: int) -> str:
    if completed == 0:
        return "Sin actividad reciente"
    if emotions.get("fear", 0) > 50 or emotions.get("sadness", 0) > 50:
        return "En seguimiento"
    if emotions.get("happiness", 0) > 50:
        return "Avance positivo"
    return "En observación"


def _friendly_trend(emotions: Dict[str, int], technical: Dict) -> Dict:
    if emotions.get("fear", 0) > 50:
        return {
            "title": "El niño presenta señales de alerta e inseguridad",
            "description": (
                "Sus respuestas muestran que algunas situaciones le generan miedo "
                "o preocupación. Esta información puede ayudar al tutor a "
                "acompañarlo mejor."
            ),
        }
    if emotions.get("sadness", 0) > 50:
        return {
            "title": "El niño muestra momentos de tristeza",
            "description": (
                "Es importante ofrecerle espacios de escucha y actividades que "
                "le animen sin presionarlo."
            ),
        }
    if emotions.get("anger", 0) > 50:
        return {
            "title": "El niño está atravesando momentos de enojo",
            "description": (
                "Acompañarlo con calma y validar sus emociones le ayudará a "
                "regularse poco a poco."
            ),
        }
    if emotions.get("happiness", 0) > 50:
        return {
            "title": "El niño se ha sentido bien la mayor parte del tiempo",
            "description": (
                "Sus respuestas muestran un estado emocional positivo. "
                "¡Sigue acompañándolo así!"
            ),
        }
    return {
        "title": "El niño está atravesando una etapa con emociones variadas",
        "description": (
            "Sus respuestas muestran distintas emociones. Acompañarlo con "
            "rutinas estables y conversaciones cortas puede ayudarle."
        ),
    }


def _recommendation(emotions: Dict[str, int]) -> str:
    if emotions.get("fear", 0) > 50:
        return (
            "Crear un objeto de seguridad (un \"amuleto de valentía\") que el "
            "niño pueda llevar consigo cuando se sienta inseguro."
        )
    if emotions.get("sadness", 0) > 50:
        return (
            "Dedica un rato del día a una actividad compartida que le guste, "
            "sin pantallas, para abrir espacio a la conversación."
        )
    if emotions.get("anger", 0) > 50:
        return (
            "Practica con él una técnica de respiración corta cuando notes "
            "que se siente abrumado."
        )
    if emotions.get("happiness", 0) > 50:
        return (
            "Refuerza positivamente con palabras lo que el niño está haciendo "
            "bien — el reconocimiento ayuda a sostener el avance."
        )
    return (
        "Mantén rutinas estables y abre conversaciones cortas sobre cómo se "
        "siente al final del día."
    )

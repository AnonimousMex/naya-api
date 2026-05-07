"""
Tests para la lógica pura de MetricsService.

Estos tests NO tocan la BD: usamos `SimpleNamespace` para fabricar las filas
joineadas que normalmente vienen del SELECT, así validamos los cálculos
puros (porcentajes, tendencias, evolución semanal) sin sesión de SQLAlchemy.
"""
from datetime import datetime, timezone

from app.api.test.metrics_service import (
    ALL_COPING_KEYS,
    ALL_EMOTION_KEYS,
    ALL_TRIGGER_KEYS,
    CLINICAL_DISCLAIMER,
    MetricsService,
    _emotion_label_es,
    _emotion_slug,
    _friendly_trend,
    _progress_status,
    _recommendation,
    _to_pct,
)


# --- helpers puros -----------------------------------------------------


class TestPureHelpers:
    def test_to_pct_zero_total_returns_zero(self):
        assert _to_pct(5, 0) == 0

    def test_to_pct_rounds_correctly(self):
        assert _to_pct(1, 3) == 33  # 33.33 → 33

    def test_to_pct_full_match(self):
        assert _to_pct(10, 10) == 100

    def test_emotion_slug_known_names(self):
        assert _emotion_slug("Miedo") == "fear"
        assert _emotion_slug("Tristeza") == "sadness"
        assert _emotion_slug("Felicidad") == "happiness"
        assert _emotion_slug("Enojo") == "anger"
        assert _emotion_slug("Vergüenza") == "shame"
        # Variante sin tilde también debe mapear
        assert _emotion_slug("Verguenza") == "shame"

    def test_emotion_slug_unknown_returns_lowercased(self):
        assert _emotion_slug("Custom") == "custom"

    def test_emotion_slug_empty_returns_none(self):
        assert _emotion_slug("") is None
        assert _emotion_slug(None) is None

    def test_emotion_label_es(self):
        assert _emotion_label_es("fear") == "Miedo"
        assert _emotion_label_es("happiness") == "Felicidad"

    def test_emotion_label_es_unknown_titlecases(self):
        assert _emotion_label_es("custom") == "Custom"


# --- emotion_percentages ----------------------------------------------


class TestEmotionPercentages:
    def test_empty_rows_returns_all_zero(self):
        result = MetricsService.emotion_percentages([])
        assert result == {k: 0 for k in ALL_EMOTION_KEYS}

    def test_single_emotion_100_percent(self, make_row):
        rows = [make_row("Miedo")] * 4
        result = MetricsService.emotion_percentages(rows)
        assert result["fear"] == 100
        assert result["sadness"] == 0

    def test_distributed_emotions(self, make_row):
        rows = [
            make_row("Miedo"),
            make_row("Miedo"),
            make_row("Tristeza"),
            make_row("Felicidad"),
        ]
        result = MetricsService.emotion_percentages(rows)
        assert result["fear"] == 50
        assert result["sadness"] == 25
        assert result["happiness"] == 25
        assert result["anger"] == 0

    def test_keys_always_present(self, make_row):
        rows = [make_row("Miedo")]
        result = MetricsService.emotion_percentages(rows)
        # Aún si solo aparece miedo, los otros keys deben existir en 0
        for k in ALL_EMOTION_KEYS:
            assert k in result


# --- coping_percentages ------------------------------------------------


class TestCopingPercentages:
    def test_empty(self):
        assert MetricsService.coping_percentages([]) == {k: 0 for k in ALL_COPING_KEYS}

    def test_balanced_distribution(self, make_row):
        rows = [
            make_row("Miedo", coping="avoidance"),
            make_row("Miedo", coping="frustration"),
            make_row("Miedo", coping="abandonment"),
            make_row("Miedo", coping="abandonment"),
        ]
        result = MetricsService.coping_percentages(rows)
        assert result["avoidance"] == 25
        assert result["frustration"] == 25
        assert result["abandonment"] == 50

    def test_invalid_coping_is_ignored(self, make_row):
        rows = [
            make_row("Miedo", coping="avoidance"),
            make_row("Miedo", coping="fake_category"),  # ignorado
            make_row("Miedo", coping=None),
        ]
        result = MetricsService.coping_percentages(rows)
        # Solo 1 de 1 categoría válida cuenta
        assert result["avoidance"] == 100


# --- trigger_percentages -----------------------------------------------


class TestTriggerPercentages:
    def test_empty(self):
        assert MetricsService.trigger_percentages([]) == {k: 0 for k in ALL_TRIGGER_KEYS}

    def test_distribution(self, make_row):
        rows = [
            make_row("Miedo", trigger="self"),
            make_row("Miedo", trigger="father"),
            make_row("Miedo", trigger="father"),
            make_row("Miedo", trigger="mother"),
        ]
        result = MetricsService.trigger_percentages(rows)
        assert result["father"] == 50
        assert result["self"] == 25
        assert result["mother"] == 25
        assert result["siblings"] == 0


# --- frequent_answers --------------------------------------------------


class TestFrequentAnswers:
    def test_empty(self):
        assert MetricsService.frequent_answers([]) == []

    def test_returns_top_n(self, make_row):
        rows = (
            [make_row("Miedo", answer_text="A")] * 3
            + [make_row("Miedo", answer_text="B")] * 2
            + [make_row("Miedo", answer_text="C")]
        )
        assert MetricsService.frequent_answers(rows, limit=2) == ["A", "B"]

    def test_default_limit_is_5(self, make_row):
        rows = [make_row("Miedo", answer_text=f"A{i}") for i in range(10)]
        assert len(MetricsService.frequent_answers(rows)) == 5


# --- weekly_evolution --------------------------------------------------


class TestWeeklyEvolution:
    def test_empty(self):
        assert MetricsService.weekly_evolution([]) == []

    def test_groups_by_iso_week(self, make_row):
        wk1 = datetime(2026, 1, 5, tzinfo=timezone.utc)  # ISO week 2
        wk2 = datetime(2026, 1, 12, tzinfo=timezone.utc)  # ISO week 3
        rows = [
            make_row("Miedo", created_at=wk1),
            make_row("Tristeza", created_at=wk1),
            make_row("Felicidad", created_at=wk2),
        ]
        result = MetricsService.weekly_evolution(rows)
        assert len(result) == 2
        # Ordenado por (year, week) ascendente
        assert result[0]["week"] == 2
        assert result[0]["answers_count"] == 2
        assert result[1]["week"] == 3
        assert result[1]["answers_count"] == 1


# --- trend (reglas textuales) ------------------------------------------


class TestTrend:
    def test_fear_dominant_returns_inseguridad(self):
        result = MetricsService.trend({"fear": 60, "sadness": 10, "anger": 10, "happiness": 10, "shame": 10})
        assert "inseguridad" in result["title"].lower()
        assert result["clinical_note"] == CLINICAL_DISCLAIMER

    def test_sadness_dominant_returns_aislamiento(self):
        result = MetricsService.trend({"fear": 10, "sadness": 60, "anger": 10, "happiness": 10, "shame": 10})
        assert "aislamiento" in result["title"].lower()

    def test_anger_dominant_returns_frustracion(self):
        result = MetricsService.trend({"fear": 10, "sadness": 10, "anger": 60, "happiness": 10, "shame": 10})
        assert "frustración" in result["title"].lower()

    def test_happiness_increase_returns_mejora(self):
        result = MetricsService.trend(
            {"fear": 20, "sadness": 20, "anger": 20, "happiness": 25, "shame": 15},
            previous_pct={"happiness": 10},
        )
        assert "mejora" in result["title"].lower()

    def test_balanced_returns_default(self):
        result = MetricsService.trend({"fear": 20, "sadness": 20, "anger": 20, "happiness": 20, "shame": 20})
        # Ninguna emoción >50, sin previous_pct → default
        assert "variado" in result["title"].lower() or "variado" in result["description"].lower()

    def test_clinical_note_always_present(self):
        # Todas las ramas deben incluir el disclaimer obligatorio
        for emotions in [
            {"fear": 60, "sadness": 0, "anger": 0, "happiness": 0, "shame": 0},
            {"fear": 0, "sadness": 60, "anger": 0, "happiness": 0, "shame": 0},
            {"fear": 0, "sadness": 0, "anger": 60, "happiness": 0, "shame": 0},
            {"fear": 0, "sadness": 0, "anger": 0, "happiness": 0, "shame": 0},
        ]:
            result = MetricsService.trend(emotions)
            assert result["clinical_note"] == CLINICAL_DISCLAIMER


# --- helpers de la vista tutor ----------------------------------------


class TestTutorHelpers:
    def test_progress_status_no_activity(self):
        assert _progress_status({"fear": 0}, completed=0) == "Sin actividad reciente"

    def test_progress_status_high_fear_or_sadness(self):
        assert _progress_status({"fear": 60, "sadness": 0, "anger": 0, "happiness": 0, "shame": 0}, completed=5) == "En seguimiento"
        assert _progress_status({"fear": 0, "sadness": 60, "anger": 0, "happiness": 0, "shame": 0}, completed=5) == "En seguimiento"

    def test_progress_status_high_happiness(self):
        assert _progress_status({"fear": 0, "sadness": 0, "anger": 0, "happiness": 60, "shame": 0}, completed=5) == "Avance positivo"

    def test_progress_status_default(self):
        assert _progress_status({"fear": 20, "sadness": 20, "anger": 20, "happiness": 20, "shame": 20}, completed=5) == "En observación"

    def test_friendly_trend_fear(self):
        result = _friendly_trend({"fear": 60, "sadness": 0, "anger": 0, "happiness": 0, "shame": 0}, technical={})
        assert "alerta" in result["title"].lower() or "inseguridad" in result["title"].lower()

    def test_recommendation_fear_mentions_amuleto(self):
        rec = _recommendation({"fear": 60, "sadness": 0, "anger": 0, "happiness": 0, "shame": 0})
        assert "amuleto" in rec.lower() or "valent" in rec.lower()

    def test_recommendation_default_non_empty(self):
        rec = _recommendation({"fear": 20, "sadness": 20, "anger": 20, "happiness": 20, "shame": 20})
        assert len(rec) > 0

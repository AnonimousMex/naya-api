"""
Tests para las métricas de dominio nuevas (citas, energía, conexiones).

Garantizan que:
- Las métricas existen y son del tipo correcto (Counter).
- Aceptan los labels documentados.
- inc() funciona y se refleja en el valor _value.

No probamos que aparezcan en Prometheus — eso es responsabilidad del
instrumentator de FastAPI, ya cubierto por tests de integración HTTP.
"""
from prometheus_client import Counter

from app.core import metrics


class TestAppointmentMetrics:
    def test_appointments_created_is_counter(self):
        assert isinstance(metrics.APPOINTMENTS_CREATED, Counter)

    def test_appointments_lifecycle_counters_exist(self):
        for m in (
            metrics.APPOINTMENTS_CREATED,
            metrics.APPOINTMENTS_CANCELLED,
            metrics.APPOINTMENTS_RESCHEDULED,
            metrics.APPOINTMENTS_COMPLETED,
        ):
            assert isinstance(m, Counter)

    def test_appointment_conflicts_accepts_operation_label(self):
        before = metrics.APPOINTMENT_CONFLICTS.labels(operation="create")._value.get()
        metrics.APPOINTMENT_CONFLICTS.labels(operation="create").inc()
        after = metrics.APPOINTMENT_CONFLICTS.labels(operation="create")._value.get()
        assert after == before + 1

    def test_appointment_conflicts_supports_reschedule_label(self):
        # Solo confirmamos que el label "reschedule" no truena.
        metrics.APPOINTMENT_CONFLICTS.labels(operation="reschedule").inc()


class TestEnergyMetrics:
    def test_energy_metrics_are_counters(self):
        for m in (
            metrics.ENERGY_CONSUMED,
            metrics.ENERGY_DEPLETED,
            metrics.ENERGY_RECHARGED_UNITS,
        ):
            assert isinstance(m, Counter)

    def test_energy_consumed_inc(self):
        before = metrics.ENERGY_CONSUMED._value.get()
        metrics.ENERGY_CONSUMED.inc()
        assert metrics.ENERGY_CONSUMED._value.get() == before + 1

    def test_energy_depleted_tracks_independently(self):
        # ENERGY_DEPLETED no debe moverse cuando incrementamos ENERGY_CONSUMED.
        depleted_before = metrics.ENERGY_DEPLETED._value.get()
        metrics.ENERGY_CONSUMED.inc()
        assert metrics.ENERGY_DEPLETED._value.get() == depleted_before


class TestTherapistConnectionRejection:
    def test_metric_exists(self):
        assert isinstance(metrics.THERAPIST_CONNECTION_REJECTED, Counter)

    def test_supports_documented_reasons(self):
        # No debe explotar con ninguno de los 3 valores documentados.
        for reason in ("unknown_code", "unknown_patient", "already_linked"):
            metrics.THERAPIST_CONNECTION_REJECTED.labels(reason=reason).inc()

"""
Generador de tráfico realista contra la API local.

Útil para:
- Nutrir las gráficas de Grafana en vivo durante una demo de tesis.
- Producir métricas custom de Prometheus (logins, activities, emociones).
- Mantener Sentry "vivo" con eventos esporádicos.

Uso:
    docker compose exec fastapi python -m app.scripts.generate_traffic
    # O con duración limitada:
    docker compose exec fastapi python -m app.scripts.generate_traffic --duration 300
    # Más intensidad:
    docker compose exec fastapi python -m app.scripts.generate_traffic --rps 5

Configuración:
- Hace login con cada uno de los 4 niños del seed.
- Simula sesiones de actividad: pega a /pairs, /sounds, /detective/game,
  /api/v1/animals, /games, /energy/current_energies, /badges, etc.
- Cada cierto tiempo registra activity-results con score y duration aleatorios.
- Con probabilidad baja inyecta un error para que Sentry tenga eventos.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

BASE_URL = "http://localhost:8000"

CHILDREN = [
    "sofia.child@naya.local",
    "mateo.child@naya.local",
    "valentina.child@naya.local",
    "emiliano.child@naya.local",
]
PASSWORD = "Password123"

# Endpoints a hitar con un PATIENT logueado (ponderados)
PATIENT_ENDPOINTS = [
    ("GET", "/api/v1/animals", 3),
    ("GET", "/api/v1/games", 3),
    ("GET", "/api/v1/pairs", 4),
    ("GET", "/api/v1/sounds", 4),
    ("GET", "/api/v1/detective/game", 4),
    ("GET", "/api/v1/specialties", 1),
    ("GET", "/api/v1/badges", 2),
    ("GET", "/api/v1/auth/daily", 2),
    ("GET", "/api/v1/parent/list-therapists", 1),
]


def _post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _request(method: str, path: str, token: Optional[str] = None) -> int:
    url = BASE_URL + path
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def _login(email: str) -> Optional[str]:
    try:
        data = _post_form(
            f"{BASE_URL}/api/v1/auth/login", {"username": email, "password": PASSWORD}
        )
        return data.get("access_token")
    except Exception as e:
        print(f"  ! login {email} failed: {e}")
        return None


def _post_activity_result(token: str, child_id: str) -> int:
    """Registra una actividad simulada con score y duración aleatorios."""
    body = json.dumps(
        {
            "child_id": child_id,
            "score": random.randint(50, 95),
            "duration_seconds": random.randint(60, 480),
            "answers": [],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/activity-results",
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def _trigger_random_error() -> int:
    """Provoca esporádicamente un error en /sentry-debug para que Sentry vea actividad."""
    endpoint = random.choice(
        [
            "/sentry-debug/attribute-error",
            "/sentry-debug/key-error",
            "/sentry-debug/index-error",
            "/sentry-debug/captured-message",
        ]
    )
    return _request("POST", endpoint)


def _get_child_id(token: str, email: str) -> Optional[str]:
    """Obtiene el patient_id del niño desde el JWT decodificado."""
    # Sin librería JWT — parseamos el payload base64.
    try:
        import base64
        payload_b64 = token.split(".")[1]
        # Padding base64
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("user", {}).get("patient_id")
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Genera tráfico contra la API")
    parser.add_argument("--rps", type=float, default=2.0, help="Requests por segundo (aprox)")
    parser.add_argument("--duration", type=int, default=0, help="Duración en segundos (0 = infinito)")
    parser.add_argument("--error-rate", type=float, default=0.02, help="% de requests que disparan error en Sentry")
    args = parser.parse_args()

    print(f"[traffic-gen] base={BASE_URL} rps={args.rps} duration={args.duration or 'infinite'}")
    print(f"[traffic-gen] children: {CHILDREN}")

    # Login inicial — cachear tokens
    tokens: dict[str, str] = {}
    for email in CHILDREN:
        tok = _login(email)
        if tok:
            tokens[email] = tok
            print(f"  ✓ login {email}")
    if not tokens:
        print("[traffic-gen] no se pudo loguear ningún niño. Aborta.")
        sys.exit(1)

    # Pesos para sampleo
    weighted_endpoints = []
    for method, path, weight in PATIENT_ENDPOINTS:
        weighted_endpoints.extend([(method, path)] * weight)

    interval = 1.0 / max(args.rps, 0.1)
    started = time.time()
    iterations = 0
    counters = {"2xx": 0, "4xx": 0, "5xx": 0, "errors": 0, "activities": 0}

    try:
        while True:
            if args.duration and time.time() - started > args.duration:
                break

            email = random.choice(list(tokens.keys()))
            token = tokens[email]

            # Cada ~20 iteraciones registramos un activity-result
            if iterations % 20 == 19:
                child_id = _get_child_id(token, email)
                if child_id:
                    code = _post_activity_result(token, child_id)
                    counters["activities"] += 1
                    print(f"  [{email[:10]}] activity-result → {code}")
            # Cada cierto tiempo dispara error sintético para Sentry
            elif random.random() < args.error_rate:
                code = _trigger_random_error()
                counters["errors"] += 1
                print(f"  [error] /sentry-debug/* → {code}")
            else:
                method, path = random.choice(weighted_endpoints)
                code = _request(method, path, token)
                bucket = "2xx" if 200 <= code < 300 else ("4xx" if 400 <= code < 500 else "5xx" if code >= 500 else "0")
                counters[bucket if bucket in counters else "5xx"] += 1
                if iterations % 10 == 0:
                    elapsed = int(time.time() - started)
                    print(
                        f"  [{elapsed:>4}s] [{email[:10]}] {method} {path} → {code} "
                        f"| ok={counters['2xx']} 4xx={counters['4xx']} 5xx={counters['5xx']} "
                        f"acts={counters['activities']} errs={counters['errors']}"
                    )

            iterations += 1
            time.sleep(interval + random.uniform(-0.2, 0.2) * interval)
    except KeyboardInterrupt:
        print("\n[traffic-gen] interrumpido por usuario")

    elapsed = int(time.time() - started)
    print(f"\n=== Resumen ({elapsed}s, {iterations} iteraciones) ===")
    for k, v in counters.items():
        print(f"  {k:10}: {v}")


if __name__ == "__main__":
    main()

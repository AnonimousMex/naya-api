# Naya API — comandos comunes de desarrollo.
# Uso: `make help`

.PHONY: help up down restart logs ps build seed migrate test test-cov shell psql metrics

DC := docker compose
CONTAINER := fastapi

help:  ## Mostrar este mensaje
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up:  ## Levantar todos los servicios (fastapi, postgres, redis, prometheus, grafana, pgadmin)
	$(DC) up -d

down:  ## Bajar todos los servicios
	$(DC) down

restart:  ## Reiniciar fastapi (recarga código sin tocar BD)
	$(DC) restart $(CONTAINER)

logs:  ## Ver logs en vivo de fastapi
	$(DC) logs -f $(CONTAINER)

ps:  ## Estado de los servicios
	$(DC) ps

build:  ## Reconstruir la imagen de fastapi
	$(DC) build $(CONTAINER)

seed:  ## Sembrar la BD con datos de prueba (8 usuarios, 32 tests, etc)
	$(DC) exec $(CONTAINER) python -m app.scripts.seed_database

migrate:  ## Aplicar migraciones de Alembic
	$(DC) exec $(CONTAINER) alembic upgrade head

test:  ## Correr los 87 unit tests
	$(DC) exec $(CONTAINER) pytest tests/ -v

test-cov:  ## Correr tests con reporte de cobertura
	$(DC) exec $(CONTAINER) pytest tests/ --cov=app --cov-report=term

shell:  ## Abrir shell dentro del contenedor de fastapi
	$(DC) exec $(CONTAINER) bash

psql:  ## Abrir psql dentro del contenedor de postgres
	$(DC) exec postgres psql -U postgres -d naya

metrics:  ## Ver métricas custom expuestas por la app
	@curl -s http://localhost:8000/metrics | grep "^naya_" | head -20

recharge:  ## Recargar energía de los 4 niños del seed
	@$(DC) exec -T postgres psql -U postgres -d naya -c \
		"UPDATE energies SET current_energy = max_energy, last_charge = NOW() \
		 WHERE user_id IN (SELECT id FROM users WHERE user_kind = 'PATIENT')"

.PHONY: dev prod down logs rebuild clean

# Dev mode: hot reload on code change, auto rebuild on deps change
dev:
	docker compose -f compose.yaml -f compose.dev.yaml up --build --watch

# Production mode: fastapi run, no reload
prod:
	docker compose up -d --build

# Stop everything (data preserved)
down:
	docker compose down

# Tail api logs
logs:
	docker compose logs -f api

# Force rebuild api image (ignore cache)
rebuild:
	docker compose build --no-cache api

# Nuke everything including data volume
clean:
	docker compose down -v

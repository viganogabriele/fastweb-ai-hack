# Tessera dev commands. Run from the repo root. Requires uv and Node >= 22.
BACKEND := backend
WEB := web
PY := $(BACKEND)/.venv/bin/python

.PHONY: setup dev backend web mocks check fmt test

setup:  ## install backend and web dependencies from the lockfiles
	cd $(BACKEND) && uv sync --frozen
	cd $(WEB) && npm ci

dev:  ## backend :8000 + web :5173 + dataset mock systems :8088 (Ctrl-C stops all)
	@trap 'kill 0' INT TERM; \
	$(MAKE) --no-print-directory mocks & \
	$(MAKE) --no-print-directory backend & \
	$(MAKE) --no-print-directory web & \
	wait

backend:
	cd $(BACKEND) && uv run uvicorn tessera.api.main:app --reload --port 8000

web:
	cd $(WEB) && npm run dev

mocks:  ## dataset mock agents server: run it, never import or read its code
	$(PY) generator/systems/mock_agents/server.py --port 8088

check:  ## must pass before every PR
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check . && uv run pytest -q
	cd $(WEB) && npm run lint && npm run typecheck

fmt:
	cd $(BACKEND) && uv run ruff check --fix . && uv run ruff format .

test:
	cd $(BACKEND) && uv run pytest -q

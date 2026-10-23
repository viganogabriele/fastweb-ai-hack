# Tessera dev commands. Run from the repo root. Requires uv and Node >= 22.
BACKEND := backend
WEB := web
PY := $(BACKEND)/.venv/bin/python

.PHONY: setup dev backend web mocks check fmt test types

setup:  ## install backend, web and type-generator dependencies from the lockfiles
	cd $(BACKEND) && uv sync --frozen
	cd $(WEB) && npm ci
	cd scripts/openapi && npm ci

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
	cd $(BACKEND) && uv run ruff check . ../eval ../scripts/export_openapi.py ../scripts/replay_demo.py && uv run ruff format --check . ../eval ../scripts/export_openapi.py ../scripts/replay_demo.py && uv run pytest -q
	cd $(WEB) && npm run lint && npm run typecheck && npm test
	$(MAKE) --no-print-directory types && git diff --exit-code -- web/src/api/schema.d.ts

fmt:
	cd $(BACKEND) && uv run ruff check --fix . ../eval ../scripts/export_openapi.py ../scripts/replay_demo.py && uv run ruff format . ../eval ../scripts/export_openapi.py ../scripts/replay_demo.py

test:
	cd $(BACKEND) && uv run pytest -q

types:  ## regenerate TypeScript contracts from FastAPI OpenAPI (no running server needed)
	@schema_dir=$$(mktemp -d) || exit 1; schema="$$schema_dir/openapi.json"; \
	trap 'rm -f "$$schema"; rmdir "$$schema_dir"' EXIT; \
	$(PY) scripts/export_openapi.py > "$$schema" && \
	scripts/openapi/node_modules/.bin/openapi-typescript "$$schema" -o web/src/api/schema.d.ts

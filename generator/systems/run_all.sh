#!/usr/bin/env bash
# Regenerates every `systems` source in dependency order. Run from repo root.
set -euo pipefail
export PYTHONHASHSEED=0
PY=.venv/bin/python
D=generator/systems
$PY $D/ecommerce/ecommerce.py
$PY $D/warehouse/warehouse.py
$PY $D/warehouse/warehouse_export.py
$PY $D/warehouse/warehouse_api_samples.py
$PY $D/logistics/logistics.py
$PY $D/logistics/ibt_incidents.py
$PY $D/planning/planning.py
$PY $D/planning/planning_docs.py
$PY $D/marketing/marketing_calendar_media.py
$PY $D/marketing/marketing_crm.py
$PY $D/customer_care/customer_care.py
$PY $D/reference/reference.py
$PY $D/agents/agents.py
$PY $D/build_notes.py 2>/dev/null || true

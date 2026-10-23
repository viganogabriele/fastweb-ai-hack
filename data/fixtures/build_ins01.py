"""Build the INS-01 fixture: the `ProductInsight`s of the fixture run.

Run from the repo root after DATA-01b (rewrites `data/fixtures/insights/`):

    backend/.venv/bin/python data/fixtures/build_ins01.py

`ins.product` itself runs on the DATA-01a/b observations, links and relations plus the real ERP
daily sales and POS returns of MIL01 and NYC01 in the `src.erp` window, at the fixture run's
`as_of` (the DATA-01b report's). The test checks the module still returns these records.
"""

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

from tesseract.core.config import REPO_ROOT
from tesseract.core.contracts import ProductInsight, Report, RunSpec
from tesseract.core.db import connect
from tesseract.core.fixtures import read_fixtures
from tesseract.core.repo import Repo, create_run
from tesseract.modules.intelligence import insights
from tesseract.modules.sources import erp

FIXTURES = REPO_ROOT / "data" / "fixtures"
TARGET = FIXTURES / "insights" / "insights.json"
INPUTS = ("Observation", "EntityLink", "EvidenceRelation")


def fixture_as_of():
    (rec,) = json.loads((FIXTURES / "reports" / "report-by-office-20261009T0835.json").read_text())
    return Report.model_validate(rec["payload"]).as_of


def build(db: Path) -> list[ProductInsight]:
    as_of = fixture_as_of()
    spec = RunSpec(
        run_id="fixture", scenario_id="historical", as_of=as_of, stores=("MIL01", "NYC01"),
        source_manifest_hash="s", config_hash="c", code_version="0", mode="fixture", modules=(),
        prompt_versions={}, model_versions={}, authorized_fixture_refs=(),
    )  # fmt: skip
    engine = connect(f"sqlite:///{db}")
    erp.load_window(engine, spec, {}, sources_dir=REPO_ROOT / "generated" / "sources")
    create_run(engine, spec)
    repo = Repo(engine, spec)
    _, records = read_fixtures(FIXTURES)
    repo.put(*(
        r for r in records
        if type(r).__name__ in INPUTS and r.available_at is not None and r.available_at <= as_of
    ))  # fmt: skip
    insights.run(SimpleNamespace(spec=spec, repo=repo, params={}))
    return repo.list(ProductInsight)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        built = build(Path(tmp) / "ins01.db")
    TARGET.parent.mkdir(exist_ok=True)
    records = [{"kind": "ProductInsight", "payload": i.model_dump(mode="json")} for i in built]
    TARGET.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(records)} ProductInsight to {TARGET.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

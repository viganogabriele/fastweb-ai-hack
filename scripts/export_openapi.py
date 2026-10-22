"""Write the API schema without opening a database or contacting any service."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from tessera.api.main import app

if __name__ == "__main__":
    print(json.dumps(app.openapi(), indent=2, sort_keys=True))

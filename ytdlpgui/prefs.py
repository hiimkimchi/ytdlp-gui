import json
from pathlib import Path


def load_prefs(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def save_prefs(path: Path, data: dict) -> None:
    try:
        path.write_text(json.dumps(data))
    except Exception:
        pass

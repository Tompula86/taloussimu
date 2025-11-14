from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Lataa YAML-konfiguraation sanakirjaksi.

    Polku annetaan projektin juuresta, esim. "config/base.yaml".
    """

    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Config file not found: {p}")

    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Config root must be a mapping (dict)")

    return data

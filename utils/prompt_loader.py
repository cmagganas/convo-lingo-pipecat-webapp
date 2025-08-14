from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any


class PromptLoader:
    def __init__(self, base_dir: Path) -> None:
        self._base = base_dir

    def load(self, language: str, version: str, name: str) -> List[Dict[str, Any]]:
        path = self._base / language / version / f"{name}.json"
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
            if not isinstance(data, list):
                raise ValueError(f"Prompt file must be a list of messages: {path}")
            return data



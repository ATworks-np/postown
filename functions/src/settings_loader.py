import json
import os
from typing import Any, Dict


def load_settings() -> Dict[str, Any]:
  base_dir = os.path.dirname(__file__)
  path = os.path.join(base_dir, "settings.json")
  with open(path, "r", encoding="utf-8") as f:
    return json.load(f)

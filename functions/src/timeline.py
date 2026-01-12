from typing import Any, Dict, List


def timeline_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
  # Expected structure similar to functions/tmp/tweets.json
  if not isinstance(payload, dict):
    return []
  items = payload.get("timeline")
  if isinstance(items, list):
    return [i for i in items if isinstance(i, dict)]
  return []

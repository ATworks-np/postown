from typing import Any, Dict, Optional

import requests

from src.config import get_rapidapi_key, RAPIDAPI_HOST, RAPIDAPI_URL


def fetch_list_timeline(list_id: str, cursor: Optional[str] = None) -> Dict[str, Any]:
  headers = {
    "x-rapidapi-key": get_rapidapi_key(),
    "x-rapidapi-host": RAPIDAPI_HOST,
  }
  params: Dict[str, Any] = {"list_id": list_id}
  if cursor:
    params["cursor"] = cursor

  resp = requests.get(RAPIDAPI_URL, headers=headers, params=params, timeout=30)
  resp.raise_for_status()
  return resp.json()

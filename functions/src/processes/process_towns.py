from src.utils import logger
from typing import Any, Dict

from src.config import get_db
from src.clients.rapidapi_client import fetch_list_timeline
from src.timeline import timeline_items
from src.repositories.posts_repo import store_posts_for_town


def process_all_towns() -> Dict[str, Any]:
  db = get_db()
  results: Dict[str, Any] = {"towns": {}, "total_saved": 0, "total_skipped": 0}
  towns = db.collection("towns").stream()
  for doc in towns:
    town_id = doc.id
    data = doc.to_dict() or {}
    list_id = data.get("post_group_id")
    if not list_id:
      logger.warning("town %s missing post_group_id; skipping", town_id)
      continue
    try:
      payload = fetch_list_timeline(str(list_id))
      items = timeline_items(payload)
      res = store_posts_for_town(town_id, items)
      results["towns"][town_id] = {"saved": res["saved"], "skipped": res["skipped"], "count": len(items)}
      results["total_saved"] += res["saved"]
      results["total_skipped"] += res["skipped"]
    except Exception as e:
      logger.error("Failed processing town %s: %s", town_id, e)
      results["towns"][town_id] = {"error": str(e)}
  return results

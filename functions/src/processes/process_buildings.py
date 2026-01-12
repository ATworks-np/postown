from src.utils import logger
import math
import random
from typing import Any, Dict, List, Tuple

from firebase_admin import firestore

from src.config import get_db
from src.settings_loader import load_settings
from src.clients.ai_client import AIClient
from src.repositories.buildings_repo import (
  get_posts_missing_category,
  update_post_category_and_exp,
  get_buildings_by_category,
  get_center_building_level,
  pick_closest_to_center,
  update_building_exp_and_level,
  create_building,
  all_buildings,
  add_post_to_building,
  set_post_remaining_exp_zero,
)
from src.utils.grid_utils import build_grid_from_buildings
from src.utils.storage_utils import upload_building_image_png
from src.utils.image_utils import remove_bg_and_trim


def _obtainable_exp_from_post(data: Dict[str, Any]) -> int:
  category = data.get("category", "") if isinstance(data, dict) else ""
  if category == "non_category":
      return 0
  base = 10
  fav = 0
  rt = 0
  # try common keys inside row_data
  row = data.get("row_data", {}) if isinstance(data, dict) else {}
  if isinstance(row, dict):
    fav = int(row.get("favorite_count") or row.get("favorites") or row.get("likes") or 0)
    rt = int(row.get("retweet_count") or row.get("retweets") or 0)
  add = max(fav - 10, 0) + max(rt - 5, 0)
  return base + add


def _choose_build_action(town_data: Dict[str, Any], settings: Dict[str, Any]) -> str:
  # returns "new" or "renovate"
  plan = str(town_data.get("urban_planning", "balance"))
  prob_map = settings.get("urban_planning", {})
  new_prob = int(prob_map.get(plan, prob_map.get("balance", 30)))
  r = random.randint(1, 100)
  return "new" if r <= new_prob else "renovate"


def _generate_and_upload_image(ai: AIClient, town_id: str, building_id: str, category: str, building_name: str, level: int, grid_size: int) -> None:
  img = ai.generate_building_image(category=category, building_name=building_name, level=level, grid_size=grid_size)
  if img:
    # Post-process: remove background and trim to tight bbox
    try:
      processed = remove_bg_and_trim(img)
    except Exception:
      processed = img
    url = upload_building_image_png(processed, f"{building_id}.png")
    if url:
      # update doc
      db = get_db()
      db.collection("towns").document(town_id).collection("buildings").document(building_id).update({"image_url": url})


def process_buildings_for_all_towns() -> Dict[str, Any]:
  db = get_db()
  settings = load_settings()
  category_to_id: Dict[str, int] = settings.get("category", {})
  level_progression = settings.get("level_progression", [])
  ai = AIClient()

  result: Dict[str, Any] = {"towns": {}}
  towns = db.collection("towns").stream()
  for doc in towns:
    town_id = doc.id
    town_data = doc.to_dict() or {}
    town_res: Dict[str, Any] = {"analyzed": 0, "renovated": 0, "built": 0, "image_updated": 0, "linked_posts": 0}
    try:
      # 1) Analyze posts without category
      pending_posts = get_posts_missing_category(town_id, limit=100)
      batches: List[List[Tuple[str, Dict[str, Any]]]] = []
      # split in chunks of 10
      for i in range(0, len(pending_posts), 10):
        batches.append(pending_posts[i : i + 10])

      analyzed_results: List[Tuple[str, Dict[str, Any], Dict[str, str]]] = []
      for batch in batches:
        payload = [{"post_id": pid, "text": (data.get("row_data", {}) or {}).get("text", "")} for pid, data in batch]
        ai_out = ai.analyze_posts(payload)
        # index by post_id
        by_id = {d.get("post_id"): d for d in ai_out if isinstance(d, dict)}
        for pid, data in batch:
          res = by_id.get(pid)
          if res:
            analyzed_results.append((pid, data, res))

      # update posts with category and obtainable_exp
      for pid, data, res in analyzed_results:
        cat = str(res.get("category", "life"))
        bname = res.get("building_name")
        obtainable = _obtainable_exp_from_post(data)
        update_post_category_and_exp(town_id, pid, cat, obtainable, bname)
        town_res["analyzed"] += 1

      # 2) Building construction per analyzed item
      center_level = get_center_building_level(town_id)
      for pid, data, res in analyzed_results:
        cat = str(res.get("category", "life"))
        bname = res.get("building_name")

        if cat == "non_category":
            continue

        obtainable = _obtainable_exp_from_post(data)
        action = _choose_build_action(town_data, settings)

        if action == "renovate":
          candidates = get_buildings_by_category(town_id, cat)
          # try from closest to center
          candidates_sorted = sorted(candidates, key=lambda it: abs(int(it[1].get("row", 0))) + abs(int(it[1].get("col", 0))))
          selected_id = None
          for bid, b in candidates_sorted:
            gained = int(b.get("gained_exp", 0)) + obtainable
            new_level = 0
            for step in level_progression:
              if gained >= int(step.get("required_total_exp", 0)):
                new_level = int(step.get("level", 0))
            if new_level <= center_level:
              selected_id = bid
              break
          if selected_id:
            old_level, new_level = update_building_exp_and_level(town_id, selected_id, obtainable, level_progression)
            town_res["renovated"] += 1
            if new_level > old_level:
              # image update
              _generate_and_upload_image(ai, town_id, selected_id, cat, bname or "", new_level, grid_size=1)
              town_res["image_updated"] += 1
            # Link the source post to the renovated building (dedupe inside repo)
            if add_post_to_building(town_id, selected_id, pid):
              town_res["linked_posts"] += 1
            # After consuming obtainable_exp, set remaining_exp to 0
            set_post_remaining_exp_zero(town_id, pid)
            continue
          # fallback to new build

        # New construction path
        blds = all_buildings(town_id)
        grid = build_grid_from_buildings(blds, category_to_id)
        target_id = int(category_to_id.get(cat, 0))
        placement = ai.choose_placement(grid, target_id)
        plc = placement.get("placement", {}) if isinstance(placement, dict) else {}
        r = int(plc.get("row", (len(grid)//2)))
        c = int(plc.get("col", (len(grid[0])//2)))
        h = len(grid)
        w = len(grid[0]) if h else 0
        cy, cx = h // 2, w // 2
        # convert to world coordinates relative to center (0,0)
        world_row = r - cy
        world_col = c - cx
        new_id = create_building(town_id, cat, world_row, world_col, obtainable)
        town_res["built"] += 1
        _generate_and_upload_image(ai, town_id, new_id, cat, bname or "", level=1, grid_size=1)
        town_res["image_updated"] += 1
        # Link the source post to the newly built building
        if add_post_to_building(town_id, new_id, pid):
          town_res["linked_posts"] += 1
        # After consuming obtainable_exp, set remaining_exp to 0
        set_post_remaining_exp_zero(town_id, pid)

    except Exception as e:
      logger.error(f"Failed processing town {town_id}: {e}")
      town_res["error"] = str(e)
    result["towns"][town_id] = town_res

  return result

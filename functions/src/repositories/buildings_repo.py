import math

from google.protobuf.internal.well_known_types import Timestamp
from src.utils import logger
from typing import Any, Dict, List, Optional, Tuple

from firebase_admin import firestore
from google.cloud.firestore import FieldFilter

from src.config import get_db


Building = Dict[str, Any]


def buildings_collection(town_id: str) -> firestore.CollectionReference:
  db = get_db()
  return db.collection("towns").document(town_id).collection("buildings")


def posts_collection(town_id: str) -> firestore.CollectionReference:
  db = get_db()
  return db.collection("towns").document(town_id).collection("posts")


def building_posts_collection(town_id: str, building_id: str) -> firestore.CollectionReference:
  db = get_db()
  return (
    db.collection("towns")
    .document(town_id)
    .collection("buildings")
    .document(building_id)
    .collection("posts")
  )


def get_center_building_level(town_id: str) -> int:
  ref = buildings_collection(town_id)
  q = ref.where(filter=FieldFilter("category", "==", "center")).limit(1).stream()
  for d in q:
    data = d.to_dict() or {}
    return int(data.get("level", 0))
  return 0


def get_buildings_by_category(town_id: str, category: str) -> List[Tuple[str, Building]]:
  ref = buildings_collection(town_id)
  docs = ref.where(filter=FieldFilter("category", "==", category)).stream()
  res: List[Tuple[str, Building]] = []
  for d in docs:
    res.append((d.id, d.to_dict() or {}))
  return res


def all_buildings(town_id: str) -> List[Tuple[str, Building]]:
  ref = buildings_collection(town_id)
  docs = ref.stream()
  res: List[Tuple[str, Building]] = []
  for d in docs:
    res.append((d.id, d.to_dict() or {}))
  return res


def manhattan_dist_to_center(row: int, col: int) -> int:
  # (0,0) is center in our coordinate system
  return abs(row) + abs(col)


def pick_closest_to_center(buildings: List[Tuple[str, Building]]) -> Optional[Tuple[str, Building]]:
  if not buildings:
    return None
  return min(
    buildings,
    key=lambda item: manhattan_dist_to_center(int(item[1].get("row", 0)), int(item[1].get("col", 0))),
  )


def compute_level_from_exp(level_progression: List[Dict[str, Any]], total_exp: int) -> int:
  lvl = 0
  for step in level_progression:
    if total_exp >= int(step.get("required_total_exp", 0)):
      lvl = int(step.get("level", 0))
  return lvl


def update_building_exp_and_level(
  town_id: str,
  building_id: str,
  add_exp: int,
  level_progression: List[Dict[str, Any]],
) -> Tuple[int, int]:
  """Returns (old_level, new_level)."""
  ref = buildings_collection(town_id).document(building_id)
  snap = ref.get()
  data = snap.to_dict() or {}
  gained = int(data.get("gained_exp", 0)) + int(add_exp)
  new_level = compute_level_from_exp(level_progression, gained)
  ref.update({"gained_exp": gained, "level": new_level})
  return int(data.get("level", 0)), new_level


def create_building(
  town_id: str,
  category: str,
  row: int,
  col: int,
  gained_exp: int,
) -> str:
  ref = buildings_collection(town_id).document()
  ref.set(
    {
      "_created_at": firestore.SERVER_TIMESTAMP,
      "category": category,
      "col": int(col),
      "row": int(row),
      "level": 1,
      "gained_exp": gained_exp,
      "grid_size": 1,
    }
  )
  return ref.id


def get_posts_missing_category(town_id: str, limit: int = 100):
  """Firestore does not support 'field does not exist' queries; fetch a page and filter client-side."""
  res: List[Tuple[str, Dict[str, Any]]] = []
  res2: List[Tuple[str, Dict[str, Any]], Dict[str, Any]] = []
  for d in posts_collection(town_id).order_by("_created_at", direction=firestore.Query.DESCENDING).limit(limit).stream():
    data = d.to_dict() or {}
    if "category" not in data:
      res.append((d.id, data))
    if data.get("remaining_exp", 0) > 0:
      res2.append((d.id, data, {'category': data.get('category'), 'building_name': data.get('building_name')}))
  return res, res2


def update_post_category_and_exp(
  town_id: str,
  post_id: str,
  category: str,
  obtainable_exp: int,
  building_name: Optional[str],
) -> None:
  # Initialize remaining_exp with obtainable_exp at the same time
  posts_collection(town_id).document(post_id).update(
    {
      "category": category,
      "obtainable_exp": int(obtainable_exp),
      "remaining_exp": int(obtainable_exp),
      "building_name": building_name,
    }
  )


def batch_update_posts_category_and_exp(
  town_id: str,
  items: List[Tuple[str, str, int, Optional[str]]],
) -> int:
  """Batch update posts' category and obtainable/remaining exp.

  Args:
    town_id: Town identifier.
    items: List of tuples (post_id, category, obtainable_exp, building_name).

  Returns:
    Number of posts scheduled for update (length of items).
  """
  if not items:
    return 0
  db = get_db()
  batch = db.batch()
  col = posts_collection(town_id)
  for post_id, category, obtainable_exp, building_name in items:
    ref = col.document(post_id)
    batch.update(
      ref,
      {
        "category": category,
        "obtainable_exp": int(obtainable_exp),
        "remaining_exp": int(obtainable_exp),
        "building_name": building_name,
      },
    )
  batch.commit()
  return len(items)


def set_post_remaining_exp_zero(town_id: str, post_id: str) -> None:
  """Set remaining_exp to 0 after the post's exp has been consumed for build/renovate."""
  posts_collection(town_id).document(post_id).update({"remaining_exp": 0})


def add_post_to_building(_created_at: Timestamp, town_id: str, building_id: str, post_id: str, original_post_id: str) -> bool:
  """Link a post to a building by creating a doc under buildings/{id}/posts.

  Returns True if created, False if a duplicate was detected and nothing was created.
  """
  col = building_posts_collection(town_id, building_id)
  # duplicate check
  dup = col.where(filter=FieldFilter("post_id", "==", post_id)).limit(1).stream()
  for _ in dup:
    logger.info(f"Duplicate building-post link skipped: town={town_id} building={building_id} post_id={post_id}")
    return False

  ref = col.document()
  ref.set({"post_id": post_id, "original_post_id": original_post_id, "_created_at": _created_at})
  return True

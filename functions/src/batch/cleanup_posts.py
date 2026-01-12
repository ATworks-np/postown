from typing import Any, Dict, List

from firebase_admin import firestore

from src.config import get_db


def delete_posts_except(town_id: str, keep_doc_ids: List[str]) -> Dict[str, Any]:
  """Delete all docs in towns/{town_id}/posts except those in keep_doc_ids.

  Returns statistics: { scanned, kept, deleted, batches_committed }
  """
  db = get_db()
  posts_ref = db.collection("towns").document(town_id).collection("posts")

  keep_set = set(keep_doc_ids)

  scanned = 0
  kept = 0
  deleted = 0
  batches = 0

  batch = db.batch()
  ops_in_batch = 0

  # Stream through all docs in posts
  for snap in posts_ref.stream():
    scanned += 1
    if snap.id in keep_set:
      kept += 1
      continue
    batch.delete(snap.reference)
    deleted += 1
    ops_in_batch += 1
    # Firestore has a hard limit of 500 writes per batch; keep margin
    if ops_in_batch >= 400:
      batch.commit()
      batches += 1
      batch = db.batch()
      ops_in_batch = 0

  if ops_in_batch:
    batch.commit()
    batches += 1

  return {
    "town_id": town_id,
    "scanned": scanned,
    "kept": kept,
    "deleted": deleted,
    "batches_committed": batches,
  }

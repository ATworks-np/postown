from typing import Any, Dict, List

from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from src.config import get_db


def _post_exists(posts_ref: firestore.CollectionReference, tweet_id: str) -> bool:
  q = posts_ref.where(filter=FieldFilter("row_data.tweet_id", "==", tweet_id)).limit(1).stream()
  return any(True for _ in q)


def store_posts_for_town(town_id: str, timeline: List[Dict[str, Any]]) -> Dict[str, int]:
  db = get_db()
  posts_ref = db.collection("towns").document(town_id).collection("posts")
  saved = 0
  skipped = 0
  batch = db.batch()
  ops_in_batch = 0

  for item in timeline:
    # Skip retweets
    if item.get("retweeted_tweet"):
      skipped += 1
      continue
    tweet_id = str(item.get("tweet_id", ""))
    if not tweet_id:
      skipped += 1
      continue
    if _post_exists(posts_ref, tweet_id):
      skipped += 1
      continue



    doc_ref = posts_ref.document()  # auto id
    data = {
      "row_data": item,
      "_created_at": firestore.SERVER_TIMESTAMP,
    }
    batch.set(doc_ref, data)
    saved += 1
    ops_in_batch += 1

    if ops_in_batch >= 400:
      batch.commit()
      batch = db.batch()
      ops_in_batch = 0

  if ops_in_batch:
    batch.commit()

  return {"saved": saved, "skipped": skipped}

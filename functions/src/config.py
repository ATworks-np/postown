import os
from typing import Optional

from firebase_admin import initialize_app, firestore

try:
  # Support local development using a .env file
  from dotenv import load_dotenv  # type: ignore
  load_dotenv()
except Exception:
  # .env is optional in production
  pass


# Initialize Admin SDK exactly once at import time
_app = initialize_app()


def get_db() -> firestore.Client:
  return firestore.client()


def get_rapidapi_key() -> str:
  key = (
    os.environ.get("X_RAPID_API_KEY")
  )
  if not key:
    raise RuntimeError(
      "RapidAPI key is not set. Please set env var X_RAPIDAPI_KEY (or RAPIDAPI_KEY)."
    )
  return key


RAPIDAPI_HOST = "twitter-api45.p.rapidapi.com"
RAPIDAPI_URL = f"https://{RAPIDAPI_HOST}/listtimeline.php"

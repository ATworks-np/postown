from typing import Optional

from firebase_admin import storage


def upload_building_image_png(content: bytes, filename: str) -> Optional[str]:
  """Uploads PNG to default bucket under buildings/{filename}. Returns public URL if available."""
  try:
    bucket = storage.bucket()
    blob = bucket.blob(f"buildings/{filename}")
    blob.upload_from_string(content, content_type="image/png")
    try:
      blob.make_public()
      return blob.public_url
    except Exception:
      # If public ACL not allowed, return signed URL could be implemented; for now None
      return None
  except Exception:
    return None

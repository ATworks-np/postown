import io

from src.utils import logger
import os

os.environ["U2NET_HOME"] = "./models"

def remove_bg_and_trim(img) -> bytes:
  """Remove background using rembg and trim to non-transparent tight bbox.

  Returns processed PNG bytes. If processing fails, returns the original bytes.
  """
  try:
    logger.info('start remove background and trim')

    from rembg import remove, new_session  # type: ignore
    from PIL import Image  # type: ignore

    my_session = new_session("u2netp")
    output_image = remove(img, session=my_session)
    bbox = output_image.getbbox()
    cropped = output_image.crop(bbox)

    logger.info('finish remove background and trim')

    # 4) Encode back to PNG bytes
    out = io.BytesIO()
    cropped.save(out, format="PNG")
    return out.getvalue()
  except Exception as e:
    logger.error('remove background and trim failed:', exc_info=e)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()

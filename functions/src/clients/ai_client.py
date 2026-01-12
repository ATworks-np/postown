import json
import os
import random
from src.utils import logger
import re
from typing import Any, Dict, List, Optional, Tuple, Literal
from pydantic import BaseModel, Field
from PIL import Image

class PlacementLocation(BaseModel):
  row: str
  col: str

class Placement(BaseModel):
  placement: PlacementLocation
  updated_grid: List[List[int]]
  reasoning: str

def _load_prompt(path: str) -> str:
  with open(path, "r", encoding="utf-8") as f:
    return f.read()


class AIClient:
  def __init__(self) -> None:
    base_dir = os.path.dirname(__file__)
    # Prompts are located at functions/src/prompts, while this file is functions/src/clients/ai_client.py
    prompts_dir = os.path.abspath(os.path.join(base_dir, "..", "prompts"))

    self.prompt_post_analyzer = _load_prompt(os.path.join(prompts_dir, "post_analyzer.md"))
    self.prompt_town_planner = _load_prompt(os.path.join(prompts_dir, "town_planner.md"))
    self.prompt_building_image = _load_prompt(os.path.join(prompts_dir, "building_image_generator.md"))

    # Google AI Python SDK (google-genai) initialization (lazy/optional)
    self._genai_client = None
    try:
        from google import genai  # type: ignore
        from google.genai.types import HttpOptions

        api_key = os.environ.get("GOOGLE_GEMINI_API_KEY")

        self._genai_client = genai.Client()
        logger.info("google-genai client initialized")
    except Exception as e:
      # SDK not installed or environment not set. We'll fall back to heuristics.
      logger.warning(f"google-genai SDK not available or failed to init: {e}")

  # ---------- Helpers ----------
  def _extract_json_snippet(self, text: Optional[str]) -> Optional[str]:
    """Extract a JSON object or array from a model response.

    Handles common patterns like Markdown code fences (```json ... ```),
    extra prose before/after JSON, and returns the first JSON block found.
    """
    if not text:
      return None
    s = text.strip()
    # Remove surrounding Markdown code fences if present
    fence = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL | re.IGNORECASE)
    m = fence.match(s)
    if m:
      s = m.group(1).strip()

    # If the whole string looks like JSON already
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
      return s

    # Otherwise, find the first JSON object/array in the text
    # Search for array first
    m = re.search(r"\[.*?\]", s, re.DOTALL)
    if m:
      return m.group(0)
    # Then object
    m = re.search(r"\{.*?\}", s, re.DOTALL)
    if m:
      return m.group(0)
    return None

  # ---------- Post Analyzer ----------
  def analyze_posts(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
    # return [{"post_id":"VbXqZtbHomOQlokFgBKW", "category":"entertainment", "building_name":"test"}]
    """items: [{post_id, text}] -> [{post_id, category, building_name}]"""
    if not items:
      return []
    if self._genai_client is not None:
      try:
        CategoryType = Literal[
            "technology",
            "economy",
            "entertainment",
            "life",
            "culture",
            "food",
            "non_category"
        ]

        class AnalyzedPost(BaseModel):
            post_id: str = Field(..., description="firebase の document ID")
            category: CategoryType = Field(..., description="カテゴリ分類")
            building_name: str = Field(..., description="具体的な建物名 (日本語)")

        class PostAnalysisResult(BaseModel):
            items: List[AnalyzedPost]

        # Use Gemini via google-genai
        prompt = self.prompt_post_analyzer + "\n\n" + json.dumps(items, ensure_ascii=False)
        resp = self._genai_client.models.generate_content(
          model="gemini-2.5-flash",
          contents=prompt,
          config={
              "response_mime_type": "application/json",
              "response_json_schema": PostAnalysisResult.model_json_schema(),
          },
        )
        result = PostAnalysisResult.model_validate_json(resp.text)
        data = result.model_dump()['items']
        if isinstance(data, list):
          return data
      except Exception as e:
        logger.warning(f"google-genai analyze_posts failed, falling back: {e}")

    return None

  # ---------- Town Planner (placement) ----------
  def choose_placement(self, grid: List[List[int]], target_id: int) -> Dict[str, Any]:
    # return {'placement': {'row': '1', 'col': '2'}, 'updated_grid': [[0, 0, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, -1, 1, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], 'reasoning':''}
    payload = {"grid": grid, "target_id": target_id}
    if self._genai_client is not None:
      try:
        prompt = self.prompt_town_planner + "\n\n" + json.dumps(payload, ensure_ascii=False)
        logger.info('start placement by ai')
        schema = Placement.model_json_schema()
        resp = self._genai_client.models.generate_content(
          model="gemini-2.5-flash",
          contents=prompt,
          config={
              "response_mime_type": "application/json",
              "response_json_schema": schema,
          },
        )
        result = Placement.model_validate_json(resp.text)
        data = result.model_dump()
        print(data)
        if isinstance(data, dict) and "placement" in data:
          return data
      except Exception as e:
        logger.warning(f"google-genai choose_placement failed, falling back: {e}")
    return None

  # ---------- Image Generation ----------
  def generate_building_image(self, category: str, building_name: str, level: int, grid_size: int):
    """Generate pil image for a building using Imagen 3.0 only.
    """
    # return  Image.open('generated_image.png')
    try:
      prompt_text = self.prompt_building_image.format(
        category=str(category), building_name=str(building_name), level=int(level), grid_size=int(grid_size)
      )
    except Exception:
      prompt_text = f"Category: {category}, Level: {level}, Grid: {grid_size}"

    if self._genai_client is None:
      return None

    try:
      logger.info('start generate image')
      resp = self._genai_client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt_text],
      )
      logger.info('finish generate image')
      for part in resp.parts:
        if part.text is not None:
          print(part.text)
        elif part.inline_data is not None:
          # Try to materialize PIL Image from raw bytes first (more robust across SDK versions)
          try:
            from io import BytesIO
            raw_bytes = None
            if hasattr(part, "as_bytes"):
              raw_bytes = part.as_bytes()  # type: ignore[attr-defined]
            elif hasattr(part, "inline_data") and hasattr(part.inline_data, "data"):
              raw_bytes = part.inline_data.data  # type: ignore[attr-defined]

            if raw_bytes:
              img = Image.open(BytesIO(raw_bytes))
              img.load()  # fully read
              try:
                img = img.convert("RGBA")
              except Exception:
                pass
              return img

            # Fallback to as_image if bytes path not available
            img2 = part.as_image()
            try:
              # Not all returned objects expose load(); guard it.
              if hasattr(img2, "load"):
                img2.load()
            except Exception:
              pass
            try:
              img2 = img2.convert("RGBA")
            except Exception:
              pass
            # Ensure detached copy if possible
            try:
              return img2.copy()
            except Exception:
              return img2
          except Exception as inner_e:
            logger.warning(f"image part handling failed, continue: {inner_e}")

      return None
    except Exception  as e:
      logger.warning(f"google-genai generate iamge failed, falling back: {e}")
      return None

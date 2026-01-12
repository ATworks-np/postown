"""
Firebase Functions entrypoints.

This file only wires HTTP/scheduled triggers to the internal implementation
under functions/src to keep the code modular and reusable.
"""

from src.utils import logger
from firebase_functions import https_fn, scheduler_fn
from firebase_functions.options import set_global_options
from firebase_functions import options

from src.processes.process_towns import process_all_towns
from src.processes.process_buildings import process_buildings_for_all_towns
from src.batch.cleanup_posts import delete_posts_except


# Cost control: set max instances per function (can be overridden per decorator)
set_global_options(max_instances=10)


# HTTP function to run on-demand (manual trigger)
@https_fn.on_request()
def fetch_x_lists_now(req: https_fn.Request) -> https_fn.Response:
  try:
    result = process_all_towns()
    return https_fn.Response(result, status=200)
  except Exception as e:
    logger.error(f"fetch_x_lists_now failed: {e}")
    return https_fn.Response({"error": str(e)}, status=500)


# Scheduled function: run daily
@scheduler_fn.on_schedule(schedule="every day 05:00")
def fetch_x_lists_daily(event: scheduler_fn.ScheduledEvent) -> None:
  try:
    result = process_all_towns()
    logger.info(f"Daily fetch completed: {result}")
  except Exception as e:
    logger.error(f"Daily fetch failed: {e}")


# =============== Buildings processing (analysis + build) ===============


@https_fn.on_request(timeout_sec=600, memory=options.MemoryOption.GB_2)
def build_towns_now(req: https_fn.Request) -> https_fn.Response:
  """Manual trigger to analyze posts, construct/renovate buildings, and generate images."""
  try:
    result = process_buildings_for_all_towns()
    return https_fn.Response(result, status=200)
  except Exception as e:
    logger.error(f"build_towns_now failed: {e}")
    return https_fn.Response({"error": str(e)}, status=500)


@scheduler_fn.on_schedule(schedule="every day 07:00")
def build_towns_daily(event: scheduler_fn.ScheduledEvent) -> None:
  """Scheduled daily trigger at 07:00."""
  try:
    result = process_buildings_for_all_towns()
    logger.info(f"Daily buildings processing completed: {result}")
  except Exception as e:
    logger.error(f"Daily buildings processing failed: {e}")


# =============== Batch utilities ===============


@https_fn.on_request()
def cleanup_town_posts_now(req: https_fn.Request) -> https_fn.Response:
  """Delete posts in a specific town except a given whitelist (manual HTTP trigger).

  This endpoint is hardcoded per maintenance request to operate on town id
  3PJ0B7ZqINXYirzCvVEt and keep only the following post doc ids:
  ["1zbiDopSzk77U7dev5Zv", "VbXqZtbHomOQlokFgBKW", "XpMhDNkxJY8foCCIhZYn", "q9jw6rtW6jFQap8mA51A", "09ebUiHVI72KVCjKWla5"].
  """
  try:
    town_id = "3PJ0B7ZqINXYirzCvVEt"
    keep_ids = [
      "1zbiDopSzk77U7dev5Zv",
      "VbXqZtbHomOQlokFgBKW",
      "XpMhDNkxJY8foCCIhZYn",
      "q9jw6rtW6jFQap8mA51A",
      "09ebUiHVI72KVCjKWla5",
    ]
    result = delete_posts_except(town_id, keep_ids)
    return https_fn.Response(result, status=200)
  except Exception as e:
    logger.error(f"cleanup_town_posts_now failed: {e}")
    return https_fn.Response({"error": str(e)}, status=500)
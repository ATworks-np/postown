import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# Cloud Logging compatible JSON logger (simple, dependency-free)
# - Prints a single JSON object per line to stdout
# - Required fields: message, severity
# - Optional fields: time (RFC3339 UTC), labels, context, data (any extra payload)


def _now_rfc3339() -> str:
  return datetime.now(timezone.utc).isoformat()


def log(
  message: str,
  severity: str = "DEFAULT",
  *,
  labels: Optional[Dict[str, Any]] = None,
  context: Optional[Dict[str, Any]] = None,
  data: Optional[Dict[str, Any]] = None,
  time: Optional[str] = None,
) -> None:
  """Emit one JSON log line to stdout.

  severity: one of Google levels (DEFAULT, DEBUG, INFO, NOTICE, WARNING, ERROR,
            CRITICAL, ALERT, EMERGENCY) or any custom string (e.g., MYSEVERITY).
  """
  payload: Dict[str, Any] = {
    "message": message,
    "severity": str(severity),
    "time": time or _now_rfc3339(),
  }

  if labels:
    payload["labels"] = labels
  if context:
    payload["context"] = context
  if data:
    payload["data"] = data

  try:
    line = json.dumps(payload, ensure_ascii=False)
  except Exception:
    # Fallback: best-effort serialization
    payload["message"] = f"{message} (json-encoding-fallback)"
    line = json.dumps({"message": payload["message"], "severity": payload["severity"], "time": payload["time"]}, ensure_ascii=False)

  print(line)
  sys.stdout.flush()


# Convenience helpers
def debug(message: str, **kwargs: Any) -> None:
  log(message, "DEBUG", **kwargs)


def info(message: str, **kwargs: Any) -> None:
  log(message, "INFO", **kwargs)


def notice(message: str, **kwargs: Any) -> None:
  log(message, "NOTICE", **kwargs)


def warning(message: str, **kwargs: Any) -> None:
  log(message, "WARNING", **kwargs)


def error(message: str, **kwargs: Any) -> None:
  log(message, "ERROR", **kwargs)


def critical(message: str, **kwargs: Any) -> None:
  log(message, "CRITICAL", **kwargs)


def alert(message: str, **kwargs: Any) -> None:
  log(message, "ALERT", **kwargs)


def emergency(message: str, **kwargs: Any) -> None:
  log(message, "EMERGENCY", **kwargs)


def custom(message: str, severity: str, **kwargs: Any) -> None:
  """Custom severity convenience wrapper (e.g., "MYSEVERITY")."""
  log(message, severity, **kwargs)


def example_all_severities() -> None:
  """Example based on the provided snippet (検証6)."""
  message = "exp 6: This is a message"
  severities = [
    "DEFAULT",
    "DEBUG",
    "INFO",
    "NOTICE",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "ALERT",
    "EMERGENCY",
    "MYSEVERITY",
  ]
  for s in severities:
    log(f"{message} with severity: {s}", s)

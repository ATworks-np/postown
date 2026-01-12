Logger ライブラリ（functions 用）

背景 / 目的
Firebase Functions (Python) で Cloud Logging 互換の JSON 形式ログを安定して出力するため、軽量な自作ロガーを用意する。標準の logging 依存を避け、message と severity を必須として 1 行 1 JSON を標準出力へ出す。

- 必須フィールド: message, severity
- 任意フィールド: time (RFC3339 UTC), labels, context, data
- 既定の Severity: DEFAULT, DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL, ALERT, EMERGENCY
- カスタム Severity も許容（例: MYSEVERITY）

仕様
- 位置: functions/src/utils/logger.py
- API:
  - log(message: str, severity: str = "DEFAULT", *, labels=None, context=None, data=None, time=None) -> None
  - ショートカット: debug / info / notice / warning / error / critical / alert / emergency
  - カスタム用: custom(message: str, severity: str, **kwargs)
- 出力例（一例）:
  {"message":"exp 6: This is a message with severity: INFO","severity":"INFO","time":"2026-01-12T01:23:45.678901+00:00"}

使い方
既存の logging 呼び出しを段階的に置換可能。

from src.utils import logger
logger.info("Daily fetch completed: ok")
logger.error("build_towns_now failed", labels={"fn":"build_towns_now"})
logger.custom("custom level sample", "MYSEVERITY", data={"foo":1})

検証6（様々な Severity）
提示スニペットに対応する出力を自作ロガーで再現可能。

from src.utils import logger
message = "exp 6: This is a message"
severities = ["DEFAULT","DEBUG","INFO","NOTICE","WARNING","ERROR","CRITICAL","ALERT","EMERGENCY","MYSEVERITY"]
for s in severities:
  logger.log(f"{message} with severity: {s}", s)

導入箇所
- functions/main.py の例外時/完了時ログを src.utils.logger に置換。

今後の拡張
- Trace/Span ID の自動付与（labels/context での取り扱い）
- 構造化 StackTrace の整備（data に格納）

実装時の感想・気持ち
- シンプルに 1 行 1 JSON で出すと、取り回しが楽で可搬性が高いと感じました。
- カスタム Severity も許容にして、運用上の柔軟性を残せたのが嬉しいです。
- 段階的に logging から置換しやすい API 形にできてよかったです。
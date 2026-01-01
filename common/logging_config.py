import logging
import json
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Custom
from typing import NotRequired, TypedDict


class EngineLogRecord(TypedDict):
    timestamp: str
    level: str
    logger: str
    message: str
    exception: NotRequired[str]


# Custom formatter that outputs JSON
class EngineJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_object = EngineLogRecord(
            timestamp=self.formatTime(
                record=record, datefmt="%Y-%m-%dT%H:%M:%SZ"
            ),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
        )

        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_object, ensure_ascii=False)

def setup_engine_logging(
    level: int = logging.INFO,
    log_dir: str = "logs",
) -> None:
    Path(log_dir).mkdir(exist_ok=True)

    handler = TimedRotatingFileHandler(
        filename=f"{log_dir}/engine.jsonl",
        when="midnight",
        interval=1,
        backupCount=14,
        encoding="utf-8",
    )

    handler.setFormatter(EngineJSONFormatter())

    logger = logging.getLogger("engine")
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

import logging
import json
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import NotRequired, TypedDict

# Custom


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
    level: int = logging.INFO, dir_name: str = "logs", file_name: str = "engine"
) -> None:
    dir_path = Path.cwd() / dir_name
    dir_path.mkdir(exist_ok=True)

    handler = TimedRotatingFileHandler(
        filename=f"{dir_name}/{file_name}.jsonl",
        when="midnight",
        interval=10,
        backupCount=14,
        encoding="utf-8",
    )

    handler.setFormatter(EngineJSONFormatter())

    logger = logging.getLogger(file_name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False

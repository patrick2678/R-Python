import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=True)


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler("app.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger("blog_app")
    for handler in logging.getLogger().handlers:
        handler.setFormatter(JsonFormatter())

    return logger


logger = setup_logger()

import logging
import colorlog
from datetime import datetime
import pytz
from logging import StreamHandler

class ColoredFormatterWithTimeZone(colorlog.ColoredFormatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        tz = pytz.timezone("Asia/Tokyo")
        return dt.astimezone(tz)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()



def setup_logger(context):
    logger = logging.getLogger(context)
    logger.setLevel(logging.DEBUG)
    # colorful format
    formatter = ColoredFormatterWithTimeZone(
            "%(log_color)s%(asctime)s - %(levelname)s - %(reset)s %(blue)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )
    # console handler
    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
import logging
import sys

logger = logging.getLogger("applogger")
logger.setLevel(level=logging.DEBUG)

_console_handler = logging.StreamHandler(sys.stdout)

_formatter = logging.Formatter("%(name)s:%(levelname)s\t%(message)s")

_console_handler.setFormatter(_formatter)

logger.addHandler(_console_handler)
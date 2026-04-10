import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("logs/api.log", maxBytes=10_000_000, backupCount=5)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
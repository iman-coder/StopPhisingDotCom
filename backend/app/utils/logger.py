import logging
import logging.handlers
import os
from dotenv import load_dotenv

try:
	# optional structured logger
	from pythonjsonlogger import jsonlogger
except Exception:
	jsonlogger = None

load_dotenv()


def _get_json_formatter():
	if not jsonlogger:
		return None
	try:
		fmt = jsonlogger.JsonFormatter(
			"%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
			rename_fields={"message": "msg"},
		)
		return fmt
	except Exception:
		return None


def configure_logging():
	# read current environment variables at call time so tests can monkeypatch
	LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
	LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() in ("1", "true", "yes")
	LOG_FILE = os.getenv("LOG_FILE", "backend.log")
	LOG_JSON = os.getenv("LOG_JSON", "false").lower() in ("1", "true", "yes")

	level = getattr(logging, LOG_LEVEL, logging.INFO)
	root = logging.getLogger()
	root.setLevel(level)

	# remove default handlers
	for h in list(root.handlers):
		root.removeHandler(h)

	# console handler
	ch = logging.StreamHandler()
	if LOG_JSON:
		jf = _get_json_formatter()
		if jf:
			ch.setFormatter(jf)
		else:
			ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
	else:
		ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
	root.addHandler(ch)

	if LOG_TO_FILE:
		# ensure directory exists
		try:
			log_dir = os.path.dirname(LOG_FILE)
			if log_dir and not os.path.exists(log_dir):
				os.makedirs(log_dir, exist_ok=True)
		except Exception:
			pass

		# Rotating file handler
		fh = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)
		if LOG_JSON:
			jf = _get_json_formatter()
			if jf:
				fh.setFormatter(jf)
			else:
				fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
		else:
			fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
		root.addHandler(fh)


def get_logger(name: str | None = None) -> logging.Logger:
	if not logging.getLogger().handlers:
		configure_logging()
	return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]

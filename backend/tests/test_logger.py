import os
from app.utils.logger import get_logger, configure_logging


def test_get_logger_and_configure(tmp_path, monkeypatch):
    # set env to write to a temp file
    logfile = tmp_path / "test_backend.log"
    monkeypatch.setenv("LOG_TO_FILE", "true")
    monkeypatch.setenv("LOG_FILE", str(logfile))
    monkeypatch.setenv("LOG_JSON", "false")

    # configure explicitly
    configure_logging()
    logger = get_logger("test")
    logger.info("hello from test")

    # ensure file was created and contains the message
    with open(logfile, "r", encoding="utf-8") as f:
        content = f.read()
    assert "hello from test" in content

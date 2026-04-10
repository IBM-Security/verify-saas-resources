from __future__ import annotations
import logging
from typing import Dict, Any

from util.config_loader import Config


class Logger:
    """Sets up structured logging based on config."""

    def __init__(self, config: 'Config'):
        self._setup_logging(config.logging_cfg)

    def _setup_logging(self, cfg: Dict[str, Any]):
        level_name = cfg.get("level", "INFO").upper()
        log_level = getattr(logging, level_name, logging.INFO)

        fmt = cfg.get("format", "%(asctime)s  %(levelname)-8s  %(message)s")
        datefmt = cfg.get("datefmt", "%Y-%m-%d %H:%M:%S")

        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

        # Root logger
        root = logging.getLogger()
        root.setLevel(log_level)

        # Console handler
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

        # Optional file handler
        if cfg.get("to_file", False):
            file_path = cfg.get("file_path", "bulk_import.log")
            file_mode = cfg.get("file_mode", "a")
            file_handler = logging.FileHandler(file_path, mode=file_mode, encoding="utf-8")
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)

        logging.info(f"Logging initialized: level={level_name}, console=yes, file={'yes' if cfg.get('to_file') else 'no'}")
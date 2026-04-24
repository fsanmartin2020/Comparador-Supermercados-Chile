"""Configuración de logging estructurado.

Provee un logger con salida a consola y archivo rotativo por día. Evita
reconfigurar handlers si el logger ya fue inicializado.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import LOGS_DIR

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-18s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger configurado con handlers de consola y archivo.

    Args:
        name: Nombre del logger (usualmente ``__name__`` del módulo).

    Returns:
        Instancia de ``logging.Logger`` lista para usar.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file: Path = LOGS_DIR / f"scraper_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

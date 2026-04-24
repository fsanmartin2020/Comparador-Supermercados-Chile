"""Registro y factory de scrapers disponibles.

Importar ``SCRAPERS_DISPONIBLES`` devuelve la lista de clases listas para
ejecutar. Nuevos supermercados se registran aquí y quedan inmediatamente
incluidos en la orquestación concurrente de ``main.py``.
"""

from __future__ import annotations

from scrapers.acuenta import AcuentaScraper
from scrapers.alvi import AlviScraper
from scrapers.base import BaseScraper
from scrapers.jumbo import JumboScraper
from scrapers.lider import LiderScraper
from scrapers.santa_isabel import SantaIsabelScraper
from scrapers.unimarc import UnimarcScraper

SCRAPERS_DISPONIBLES: tuple[type[BaseScraper], ...] = (
    JumboScraper,
    SantaIsabelScraper,
    UnimarcScraper,
    AlviScraper,
    LiderScraper,
    AcuentaScraper,
)

__all__ = [
    "BaseScraper",
    "SCRAPERS_DISPONIBLES",
    "JumboScraper",
    "SantaIsabelScraper",
    "UnimarcScraper",
    "AlviScraper",
    "LiderScraper",
    "AcuentaScraper",
]

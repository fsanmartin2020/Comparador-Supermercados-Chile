"""Scraper para Alvi.cl — front SMU (mismo grupo que Unimarc).

Alvi reutiliza la infraestructura de SMU, así que hereda toda la lógica
de parseo del :class:`SMUScraper`. Si en el futuro divergen los selectores,
sobreescribir ``parsear`` aquí.
"""

from __future__ import annotations

from scrapers.smu import SMUScraper


class AlviScraper(SMUScraper):
    SUPERMERCADO = "Alvi"
    BASE_URL = "https://www.alvi.cl"

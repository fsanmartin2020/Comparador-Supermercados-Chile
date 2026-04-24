"""Scraper para Acuenta.cl — Walmart Chile (marca de descuento).

Acuenta comparte la infraestructura de Lider (ambos Walmart), por eso
hereda de :class:`WalmartScraper`. Si los selectores divergen, se puede
sobrescribir ``parsear`` sin afectar a Lider.
"""

from __future__ import annotations

from scrapers.walmart import WalmartScraper


class AcuentaScraper(WalmartScraper):
    SUPERMERCADO = "Acuenta"
    BASE_URL = "https://www.acuenta.cl"
    # Acuenta expone /search en la raíz, no /supermercado/search.
    RUTA_BUSQUEDA = "/search"

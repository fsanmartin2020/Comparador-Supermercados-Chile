"""Scraper para Lider.cl — Walmart Chile (requiere undetected_chromedriver)."""

from __future__ import annotations

from scrapers.walmart import WalmartScraper


class LiderScraper(WalmartScraper):
    SUPERMERCADO = "Lider"
    BASE_URL = "https://www.lider.cl"
    RUTA_BUSQUEDA = "/supermercado/search"

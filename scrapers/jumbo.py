"""Scraper para Jumbo.cl — front VTEX."""

from __future__ import annotations

from scrapers.vtex import VTEXScraper


class JumboScraper(VTEXScraper):
    SUPERMERCADO = "Jumbo"
    BASE_URL = "https://www.jumbo.cl"

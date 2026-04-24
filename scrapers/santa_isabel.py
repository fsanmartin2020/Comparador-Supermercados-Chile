"""Scraper para SantaIsabel.cl — front VTEX."""

from __future__ import annotations

from scrapers.vtex import VTEXScraper


class SantaIsabelScraper(VTEXScraper):
    SUPERMERCADO = "Santa Isabel"
    BASE_URL = "https://www.santaisabel.cl"

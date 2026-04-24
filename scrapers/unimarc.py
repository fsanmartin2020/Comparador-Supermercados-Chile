"""Scraper para Unimarc.cl — front SMU."""

from __future__ import annotations

from scrapers.smu import SMUScraper


class UnimarcScraper(SMUScraper):
    SUPERMERCADO = "Unimarc"
    BASE_URL = "https://www.unimarc.cl"

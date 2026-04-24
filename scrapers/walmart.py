"""Scraper genérico para tiendas Walmart Chile (Lider, Acuenta).

Walmart Chile usa Akamai Bot Manager, por lo que ambos scrapers fuerzan
``undetected_chromedriver``. El HTML comparte el componente Algolia
``ais-Hits-item`` y las clases ``product-card__*``.
"""

from __future__ import annotations

import urllib.parse
from typing import Iterator

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from utils.cleaning import construir_enlace, limpiar_precio, limpiar_texto


class WalmartScraper(BaseScraper):
    """Scraper compartido para Lider y Acuenta (infraestructura Walmart)."""

    REQUIERE_UNDETECTED = True

    # Ruta de búsqueda relativa al ``BASE_URL``. Cada subclase la sobrescribe
    # si Acuenta/Lider usan rutas distintas en el futuro.
    RUTA_BUSQUEDA: str = "/supermercado/search"

    def construir_url(self, busqueda: str) -> str:
        termino = urllib.parse.quote(busqueda)
        return f"{self.BASE_URL}{self.RUTA_BUSQUEDA}?query={termino}"

    def parsear(self, soup: BeautifulSoup, busqueda: str) -> Iterator[dict]:
        items = soup.find_all("li", class_="ais-Hits-item")
        if not items:
            self.logger.warning(
                "%s — 'ais-Hits-item' no produjo resultados para %r",
                self.SUPERMERCADO,
                busqueda,
            )

        for item in items:
            try:
                descripcion = item.find("h2", class_="product-description")
                if descripcion:
                    marca_span = descripcion.find(
                        "span", style="font-weight: bold; color: rgb(0, 0, 0);"
                    )
                    marca_text = (
                        marca_span.get_text(strip=True) if marca_span else None
                    )
                    nombre_span = (
                        marca_span.find_next_sibling("span") if marca_span else None
                    )
                    nombre_text = (
                        nombre_span.get_text(strip=True) if nombre_span else None
                    )
                else:
                    marca_text = nombre_text = None

                precio = item.find("div", class_="product-card__sale-price")
                precio_valor, por_mayor = limpiar_precio(
                    precio.get_text(strip=True) if precio else None
                )

                link = item.find("a", {"data-testid": "product-card-nav-test-id"})
                href = link.get("href") if link else None

                yield self._fila(
                    marca=limpiar_texto(marca_text, fallback="Sin marca"),
                    producto=limpiar_texto(nombre_text, fallback="Sin nombre"),
                    precio=precio_valor,
                    categoria=busqueda,
                    enlace=construir_enlace(self.BASE_URL, href),
                    por_mayor=por_mayor,
                )
            except Exception as err:  # noqa: BLE001
                self.logger.warning(
                    "%s — item ignorado: %s", self.SUPERMERCADO, err
                )
                continue

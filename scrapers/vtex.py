"""Scraper genérico para tiendas basadas en VTEX (Jumbo, Santa Isabel).

Ambas tiendas comparten estructura HTML prácticamente idéntica porque
usan el mismo front-end de VTEX: tarjetas ``product-card``, nombres en
``.product-card-name`` y precios en ``.prices-main-price``. Este módulo
centraliza esa lógica para que las subclases solo definan el dominio.
"""

from __future__ import annotations

import urllib.parse
from typing import Iterator

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from utils.cleaning import construir_enlace, limpiar_precio, limpiar_texto


class VTEXScraper(BaseScraper):
    """Implementación compartida para front-ends VTEX."""

    def construir_url(self, busqueda: str) -> str:
        termino = urllib.parse.quote(busqueda)
        return f"{self.BASE_URL}/busqueda?ft={termino}"

    def parsear(self, soup: BeautifulSoup, busqueda: str) -> Iterator[dict]:
        tarjetas = soup.find_all("div", class_="product-card")
        if not tarjetas:
            self.logger.warning(
                "%s — selector 'product-card' no produjo resultados para %r",
                self.SUPERMERCADO,
                busqueda,
            )

        for tarjeta in tarjetas:
            try:
                marca = tarjeta.find("a", class_="product-card-brand")
                nombre = tarjeta.find("a", class_="product-card-name")
                precio = tarjeta.find("span", class_="prices-main-price")
                link = tarjeta.find("a", class_="product-card-image-link")

                precio_valor, por_mayor = limpiar_precio(
                    precio.get_text(strip=True) if precio else None
                )
                href = link.get("href") if link else None

                yield self._fila(
                    marca=limpiar_texto(
                        marca.get_text(strip=True) if marca else None,
                        fallback="Sin marca",
                    ),
                    producto=limpiar_texto(
                        nombre.get_text(strip=True) if nombre else None,
                        fallback="Sin nombre",
                    ),
                    precio=precio_valor,
                    categoria=busqueda,
                    enlace=construir_enlace(self.BASE_URL, href),
                    por_mayor=por_mayor,
                )
            except Exception as err:  # noqa: BLE001 — una tarjeta rota no debe matar todo
                self.logger.warning(
                    "%s — tarjeta ignorada por error de parseo: %s",
                    self.SUPERMERCADO,
                    err,
                )
                continue

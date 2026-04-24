"""Scraper genérico para tiendas del grupo SMU (Unimarc, Alvi).

SMU usa un front propio con clases CSS bastante específicas (``Shelf_...``,
``Text_...``). Los selectores se parametrizan como atributos de clase para
que, si cambian en el futuro, la modificación sea puntual.
"""

from __future__ import annotations

from typing import Iterator

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper
from utils.cleaning import construir_enlace, limpiar_precio, limpiar_texto

# Los nombres de clase de SMU son hashes CSS-in-JS y cambian ocasionalmente.
# Si falla el parseo, lo primero a revisar son estos tres selectores.
_SELECTOR_CONTENEDOR = (
    "div",
    {"class": "baseContainer_container__TSgMX ab__shelves abc__shelves "
              "baseContainer_justify-start___sjrG "
              "baseContainer_align-start__6PKCY "
              "baseContainer_absolute-default--topLeft__lN1In"},
)
_SELECTOR_CARD = (
    "div",
    {"class": "baseContainer_container__TSgMX "
              "baseContainer_justify-start___sjrG "
              "baseContainer_align-start__6PKCY "
              "baseContainer_flex-direction--column__iiccg "
              "baseContainer_absolute-default--topLeft__lN1In"},
)
_CLASE_PRECIO = (
    "Text_text__cB7NM Text_text--left__1v2Xw Text_text--flex__F7yuI "
    "Text_text--medium__rIScp Text_text--lg__GZWsa "
    "Text_text--primary__OoK0C Text_text__cursor--auto__cMaN1 "
    "Text_text--none__zez2n"
)


class SMUScraper(BaseScraper):
    """Implementación compartida para tiendas SMU (Unimarc, Alvi)."""

    def construir_url(self, busqueda: str) -> str:
        termino = busqueda.strip().replace(" ", "-")
        return f"{self.BASE_URL}/search?q={termino}"

    def parsear(self, soup: BeautifulSoup, busqueda: str) -> Iterator[dict]:
        contenedor_tag, contenedor_attrs = _SELECTOR_CONTENEDOR
        card_tag, card_attrs = _SELECTOR_CARD

        contenedores = soup.find_all(contenedor_tag, attrs=contenedor_attrs)
        if not contenedores:
            self.logger.warning(
                "%s — contenedores SMU no encontrados para %r",
                self.SUPERMERCADO,
                busqueda,
            )

        for contenedor in contenedores:
            try:
                card = contenedor.find(card_tag, attrs=card_attrs)
                if card is None:
                    continue

                marca = card.find("p", class_="Shelf_brandText__sGfsS")
                nombre = card.find("p", class_="Shelf_nameProduct__CXI5M")
                precio = card.find("p", class_=_CLASE_PRECIO)
                link = card.find("a", class_="Link_link___5dmQ")

                precio_valor, por_mayor = limpiar_precio(
                    precio.get_text(strip=True) if precio else None
                )

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
                    enlace=construir_enlace(
                        self.BASE_URL, link.get("href") if link else None
                    ),
                    por_mayor=por_mayor,
                )
            except Exception as err:  # noqa: BLE001
                self.logger.warning(
                    "%s — card ignorada: %s", self.SUPERMERCADO, err
                )
                continue

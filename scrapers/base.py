"""Clase base abstracta para todos los scrapers de supermercados.

Implementa el ciclo de vida común:
    1. Construir opciones de Chrome (headless, UA aleatorio, proxy opcional).
    2. Abrir el driver (regular o undetected).
    3. Navegar a la URL de búsqueda.
    4. Pasar el HTML a :meth:`parsear` (implementado por cada subclase).
    5. Cerrar el driver siempre, incluso ante excepciones.

Las subclases solo deben:
    * Declarar ``SUPERMERCADO``, ``BASE_URL`` y ``REQUIERE_UNDETECTED``.
    * Implementar :meth:`construir_url` y :meth:`parsear`.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import datetime
from random import randrange
from typing import Iterator

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential

from config import (
    MAX_RETRIES,
    PAGE_LOAD_TIMEOUT_S,
    WAIT_AFTER_LOAD_MAX_S,
    WAIT_AFTER_LOAD_MIN_S,
    WAIT_HARDENED_MAX_S,
    WAIT_HARDENED_MIN_S,
)
from utils.logger import get_logger
from utils.user_agents import random_proxy, random_user_agent


class BaseScraper(ABC):
    """Plantilla común para scrapear un supermercado por categoría.

    Attributes:
        SUPERMERCADO: Nombre que aparecerá en la columna ``Supermercado``.
        BASE_URL: Dominio base para armar enlaces absolutos.
        REQUIERE_UNDETECTED: Si la tienda detecta Selenium standard y hay
            que usar ``undetected_chromedriver``.
    """

    SUPERMERCADO: str = ""
    BASE_URL: str = ""
    REQUIERE_UNDETECTED: bool = False

    def __init__(self) -> None:
        if not self.SUPERMERCADO or not self.BASE_URL:
            raise ValueError(
                f"{type(self).__name__} debe definir SUPERMERCADO y BASE_URL"
            )
        self.logger = get_logger(f"scraper.{self.SUPERMERCADO.lower().replace(' ', '_')}")

    # ------------------------------------------------------------------
    # Hooks que las subclases deben implementar.
    # ------------------------------------------------------------------
    @abstractmethod
    def construir_url(self, busqueda: str) -> str:
        """Devuelve la URL de búsqueda para ``busqueda`` en esta tienda."""

    @abstractmethod
    def parsear(self, soup: BeautifulSoup, busqueda: str) -> Iterator[dict]:
        """Itera sobre tarjetas de producto y yield-ea filas ya limpias."""

    # ------------------------------------------------------------------
    # Flujo público.
    # ------------------------------------------------------------------
    def scrap(self, busqueda: str) -> list[dict]:
        """Ejecuta el scraping para una categoría con reintentos.

        Args:
            busqueda: Término de búsqueda (p. ej. ``"Leche Entera"``).

        Returns:
            Lista de filas (diccionarios) listas para agregar al DataFrame.
            Lista vacía si todos los intentos fallan.
        """
        try:
            return self._scrap_con_reintentos(busqueda)
        except RetryError as err:
            self.logger.error(
                "Todos los reintentos fallaron para %r: %s", busqueda, err
            )
            return []

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        reraise=True,
    )
    def _scrap_con_reintentos(self, busqueda: str) -> list[dict]:
        driver = self._crear_driver()
        try:
            url = self.construir_url(busqueda)
            self.logger.info("GET %s", url)
            driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_S)
            driver.get(url)
            self._esperar_render(driver)
            # Truco estándar: ocultar la propiedad que delata a Selenium.
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', "
                "{get: () => undefined})"
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            filas = list(self.parsear(soup, busqueda))
            self.logger.info(
                "%s — %d productos encontrados para %r",
                self.SUPERMERCADO,
                len(filas),
                busqueda,
            )
            return filas
        except WebDriverException as err:
            self.logger.warning(
                "WebDriverException en %s / %s: %s",
                self.SUPERMERCADO,
                busqueda,
                err,
            )
            raise
        finally:
            self._cerrar_driver(driver)

    # ------------------------------------------------------------------
    # Helpers internos.
    # ------------------------------------------------------------------
    def _crear_driver(self) -> WebDriver:
        """Crea y devuelve un ``WebDriver`` configurado para headless."""
        user_agent = random_user_agent()
        proxy = random_proxy()

        if self.REQUIERE_UNDETECTED:
            opciones = uc.ChromeOptions()
        else:
            opciones = webdriver.ChromeOptions()
            opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
            opciones.add_experimental_option("useAutomationExtension", False)

        opciones.add_argument("--headless=new")
        opciones.add_argument("--disable-blink-features=AutomationControlled")
        opciones.add_argument("--disable-gpu")
        opciones.add_argument("--no-sandbox")
        opciones.add_argument("--window-size=1920,1080")
        opciones.add_argument(f"user-agent={user_agent}")
        if proxy:
            opciones.add_argument(f"--proxy-server={proxy}")
            self.logger.info("Usando proxy %s", proxy)

        if self.REQUIERE_UNDETECTED:
            return uc.Chrome(options=opciones)
        return webdriver.Chrome(options=opciones)

    def _esperar_render(self, driver: WebDriver) -> None:
        """Duerme un rango aleatorio ajustado al nivel de bloqueo del sitio."""
        if self.REQUIERE_UNDETECTED:
            dormir = randrange(WAIT_HARDENED_MIN_S, WAIT_HARDENED_MAX_S)
        else:
            dormir = randrange(WAIT_AFTER_LOAD_MIN_S, WAIT_AFTER_LOAD_MAX_S)
        time.sleep(dormir)

    def _cerrar_driver(self, driver: WebDriver) -> None:
        try:
            driver.quit()
        except Exception as err:  # noqa: BLE001 — cierre best-effort
            self.logger.debug("Error al cerrar driver (ignorado): %s", err)

    def _fila(
        self,
        *,
        marca: str,
        producto: str,
        precio: int,
        categoria: str,
        enlace: str,
        por_mayor: str,
    ) -> dict:
        """Construye una fila con el esquema estándar del DataFrame."""
        return {
            "Supermercado": self.SUPERMERCADO,
            "Marca": marca,
            "Producto": producto,
            "Precio": precio,
            "Categoria": categoria,
            "Enlace": enlace,
            "Fecha": datetime.now().date().isoformat(),
            "porMayor": por_mayor,
        }

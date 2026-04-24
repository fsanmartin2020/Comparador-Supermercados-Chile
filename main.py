"""Orquestador principal del pipeline de scraping.

Flujo:
    1. Cargar el CSV histórico (desde GitHub o desde disco si ya se bajó).
    2. Ejecutar todos los scrapers en paralelo, uno por combinación
       (scraper, categoría). Los scrapers de Walmart (Lider, Acuenta) se
       limitan a un único worker para no gatillar el anti-bot de Akamai.
    3. Consolidar filas nuevas, descartar precios ``0`` (sin stock),
       ordenar por precio y reindexar.
    4. Agregar columna ``ProductoNormalizado`` para matching cross-store.
    5. Subir el resultado a GitHub vía la API REST.

Uso:
    $ python main.py                    # modo completo: scraping + subida
    $ python main.py --dry-run          # scraping + guarda local, no sube
    $ python main.py --solo Jumbo Lider # ejecuta un subconjunto
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

import pandas as pd

from config import (
    CATEGORIAS_BUSQUEDA,
    COLUMNAS,
    LOCAL_CSV_PATH,
    MAX_WORKERS,
    REMOTE_CSV_URL,
)
from scrapers import SCRAPERS_DISPONIBLES, BaseScraper
from utils.github_uploader import GitHubUploadError, subir_csv
from utils.logger import get_logger
from utils.normalization import normalizar_nombre

_LOGGER = get_logger("main")

# Tiendas que comparten infraestructura Walmart/Akamai no deben correr en
# paralelo entre sí: levantar dos Chrome detectados a la vez aumenta el
# riesgo de bloqueo. Se ejecutan secuencialmente.
_TIENDAS_SENSIBLES = {"Lider", "Acuenta"}


def cargar_historico() -> pd.DataFrame:
    """Lee el CSV histórico remoto; si falla, intenta el archivo local."""
    try:
        df = pd.read_csv(REMOTE_CSV_URL, index_col="Id")
        _LOGGER.info("Histórico cargado desde GitHub (%d filas)", len(df))
        return df
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning(
            "No se pudo cargar el histórico remoto (%s). Intentando local.", err
        )
    if LOCAL_CSV_PATH.exists():
        df = pd.read_csv(LOCAL_CSV_PATH, index_col="Id")
        _LOGGER.info("Histórico cargado desde disco (%d filas)", len(df))
        return df
    _LOGGER.info("Sin histórico: se parte con DataFrame vacío")
    return pd.DataFrame(columns=COLUMNAS)


def ejecutar_scraper(scraper: BaseScraper, categoria: str) -> list[dict]:
    """Wrapper para ejecutar un scraper y capturar cualquier error."""
    try:
        return scraper.scrap(categoria)
    except Exception as err:  # noqa: BLE001 — nada debe parar el pool
        _LOGGER.exception(
            "Fallo inesperado en %s / %s: %s", scraper.SUPERMERCADO, categoria, err
        )
        return []


def recolectar_filas(
    scrapers: Iterable[BaseScraper], categorias: Iterable[str]
) -> list[dict]:
    """Ejecuta todos los ``(scraper, categoría)`` y devuelve las filas.

    Separa las tiendas sensibles (Walmart) para correrlas en serie y deja
    el resto corriendo en paralelo con ``MAX_WORKERS`` hilos.
    """
    scrapers = list(scrapers)
    categorias = list(categorias)
    filas: list[dict] = []

    sensibles = [s for s in scrapers if s.SUPERMERCADO in _TIENDAS_SENSIBLES]
    paralelos = [s for s in scrapers if s.SUPERMERCADO not in _TIENDAS_SENSIBLES]

    if paralelos:
        _LOGGER.info(
            "Ejecutando en paralelo %d scraper(s) × %d categoría(s) con %d workers",
            len(paralelos),
            len(categorias),
            MAX_WORKERS,
        )
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futuros = {
                pool.submit(ejecutar_scraper, scraper, categoria): (
                    scraper.SUPERMERCADO,
                    categoria,
                )
                for scraper in paralelos
                for categoria in categorias
            }
            for futuro in as_completed(futuros):
                nombre, categoria = futuros[futuro]
                resultado = futuro.result()
                _LOGGER.info(
                    "[%s / %s] %d filas recolectadas", nombre, categoria, len(resultado)
                )
                filas.extend(resultado)

    for scraper in sensibles:
        _LOGGER.info(
            "Ejecutando en serie tienda sensible: %s", scraper.SUPERMERCADO
        )
        for categoria in categorias:
            resultado = ejecutar_scraper(scraper, categoria)
            _LOGGER.info(
                "[%s / %s] %d filas recolectadas",
                scraper.SUPERMERCADO,
                categoria,
                len(resultado),
            )
            filas.extend(resultado)

    return filas


def consolidar(historico: pd.DataFrame, nuevas: list[dict]) -> pd.DataFrame:
    """Une histórico + filas nuevas, filtra precios 0, normaliza y ordena."""
    if not nuevas:
        _LOGGER.warning("No se obtuvieron filas nuevas; se conserva el histórico")
        df = historico.copy()
    else:
        df_nuevas = pd.DataFrame(nuevas, columns=COLUMNAS)
        df = pd.concat([historico, df_nuevas], ignore_index=True)

    antes = len(df)
    df = df[df["Precio"] > 0].copy()
    _LOGGER.info("Filas con precio > 0: %d / %d", len(df), antes)

    df["ProductoNormalizado"] = df.apply(
        lambda fila: normalizar_nombre(
            str(fila.get("Producto", "")), str(fila.get("Marca", ""))
        ),
        axis=1,
    )

    df = df.sort_values(by=["Precio"], ascending=True).reset_index(drop=True)
    df.index.name = "Id"
    return df


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scraping y consolidación de precios de supermercados chilenos."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No sube el CSV a GitHub; solo guarda localmente.",
    )
    parser.add_argument(
        "--solo",
        nargs="+",
        metavar="SUPERMERCADO",
        help="Ejecuta únicamente los supermercados indicados (por nombre).",
    )
    parser.add_argument(
        "--categorias",
        nargs="+",
        metavar="TERMINO",
        help="Sobrescribe la lista de categorías configurada.",
    )
    return parser.parse_args()


def seleccionar_scrapers(filtro: list[str] | None) -> list[BaseScraper]:
    if not filtro:
        return [cls() for cls in SCRAPERS_DISPONIBLES]
    filtro_normalizado = {nombre.strip().lower() for nombre in filtro}
    seleccionados: list[BaseScraper] = []
    for cls in SCRAPERS_DISPONIBLES:
        if cls.SUPERMERCADO.lower() in filtro_normalizado:
            seleccionados.append(cls())
    if not seleccionados:
        raise SystemExit(
            f"Ningún scraper coincide con {filtro!r}. "
            f"Opciones: {[c.SUPERMERCADO for c in SCRAPERS_DISPONIBLES]}"
        )
    return seleccionados


def main() -> int:
    args = parsear_argumentos()
    scrapers = seleccionar_scrapers(args.solo)
    categorias = args.categorias or CATEGORIAS_BUSQUEDA

    _LOGGER.info(
        "Iniciando pipeline — scrapers=%s categorias=%s",
        [s.SUPERMERCADO for s in scrapers],
        categorias,
    )

    historico = cargar_historico()
    nuevas = recolectar_filas(scrapers, categorias)
    df_final = consolidar(historico, nuevas)

    df_final.to_csv(LOCAL_CSV_PATH, index=True, index_label="Id")
    _LOGGER.info("CSV guardado localmente en %s (%d filas)", LOCAL_CSV_PATH, len(df_final))

    if args.dry_run:
        _LOGGER.info("--dry-run activo: se omite la subida a GitHub")
        return 0

    try:
        subir_csv(df_final)
    except GitHubUploadError as err:
        _LOGGER.error("Error subiendo a GitHub: %s", err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

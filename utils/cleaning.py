"""Funciones puras de limpieza de texto y precios.

Estas utilidades no tocan el DOM: reciben strings ya extraídos por los
scrapers y los convierten a los tipos que espera el DataFrame final.
"""

from __future__ import annotations

import re

# Patrón para precios "al por mayor": "3 x $1.990", "2x$3500", etc.
_PATRON_POR_MAYOR = re.compile(r"(\d+)\s*x\s*\$\s*([\d.,]+)", re.IGNORECASE)


def limpiar_precio(texto: str | None) -> tuple[int, str]:
    """Convierte un string de precio a entero en pesos chilenos.

    Maneja tanto precios simples (``"$1.990"``) como promociones al por
    mayor (``"3 x $4.500"``), donde se calcula el precio unitario.

    Args:
        texto: Texto bruto del precio extraído del HTML.

    Returns:
        Tupla ``(precio_unitario_int, etiqueta_por_mayor)``. Si no hay
        promoción, la etiqueta es ``""``. Si el texto es inválido o vacío,
        retorna ``(0, "")``.
    """
    if not texto:
        return 0, ""

    texto = texto.strip()

    match = _PATRON_POR_MAYOR.match(texto)
    if match:
        cantidad = int(match.group(1))
        total = int(match.group(2).replace(".", "").replace(",", ""))
        if cantidad <= 0:
            return 0, ""
        return total // cantidad, texto

    solo_digitos = re.sub(r"[^\d]", "", texto)
    if not solo_digitos:
        return 0, ""
    return int(solo_digitos), ""


def limpiar_texto(texto: str | None, fallback: str = "Sin dato") -> str:
    """Normaliza un string: strip, title-case y fallback si está vacío."""
    if not texto:
        return fallback
    limpio = " ".join(texto.split())
    return limpio.title() if limpio else fallback


def construir_enlace(base_url: str, href: str | None) -> str:
    """Prepende el dominio al href relativo; retorna 'Sin enlace' si falta."""
    if not href:
        return "Sin enlace"
    if href.startswith("http"):
        return href
    return f"{base_url.rstrip('/')}{href}"

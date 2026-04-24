"""Normalización de nombres de producto para matching cruzado entre tiendas.

El objetivo es que ``"Leche Soprole 1L"`` y ``"Soprole Leche Entera 1lt"``
produzcan la misma clave normalizada, para que Power BI pueda agruparlos.

Estrategia:
1. Minúsculas y eliminación de acentos.
2. Extracción de tamaño estándar (``1 l``, ``500 g``, ``12 un``).
3. Tokenización y remoción de stop-words de retail.
4. Ordenamiento alfabético de tokens → clave estable.
5. Fuzzy matching opcional con :func:`encontrar_similar` para consolidar
   variantes que quedaron con 1-2 tokens de diferencia.
"""

from __future__ import annotations

import re

from unidecode import unidecode

# Palabras irrelevantes que inflan el texto sin aportar al matching.
_STOP_WORDS: frozenset[str] = frozenset(
    {
        "de",
        "del",
        "la",
        "el",
        "los",
        "las",
        "con",
        "sin",
        "pack",
        "un",
        "unidades",
        "unidad",
        "natural",
        "tradicional",
    }
)

# Tamaños estándar: cantidad + unidad (l/lt/ml/g/kg/cc/un).
_PATRON_TAMANIO = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(kg|g|gr|ml|cc|l|lt|un)\b", re.IGNORECASE
)

# Unidades homologadas para que "lt" y "l" colapsen.
_UNIDAD_CANONICA: dict[str, str] = {
    "l": "l",
    "lt": "l",
    "ml": "ml",
    "cc": "ml",
    "g": "g",
    "gr": "g",
    "kg": "kg",
    "un": "un",
}


def _extraer_tamanio(texto: str) -> str:
    """Extrae el primer tamaño con unidad canónica; '' si no hay."""
    match = _PATRON_TAMANIO.search(texto)
    if not match:
        return ""
    cantidad = match.group(1).replace(",", ".")
    unidad = _UNIDAD_CANONICA.get(match.group(2).lower(), match.group(2).lower())
    try:
        numero = float(cantidad)
        # Formato entero si corresponde, evita "1.0 l".
        cantidad_str = str(int(numero)) if numero.is_integer() else f"{numero:g}"
    except ValueError:
        cantidad_str = cantidad
    return f"{cantidad_str}{unidad}"


def normalizar_nombre(producto: str, marca: str = "") -> str:
    """Devuelve una clave canónica para comparar productos entre tiendas.

    Args:
        producto: Nombre del producto tal como aparece en la tienda.
        marca: Marca asociada (se antepone para robustecer el match).

    Returns:
        String en minúsculas con tokens ordenados, p. ej. ``"1l entera
        leche soprole"``.
    """
    crudo = f"{marca} {producto}".strip()
    sin_acentos = unidecode(crudo).lower()
    tamanio = _extraer_tamanio(sin_acentos)
    sin_tamanio = _PATRON_TAMANIO.sub(" ", sin_acentos)
    # Solo letras/números, colapsa separadores.
    tokens = re.findall(r"[a-z0-9]+", sin_tamanio)
    tokens = [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]
    if tamanio:
        tokens.append(tamanio)
    return " ".join(sorted(tokens))



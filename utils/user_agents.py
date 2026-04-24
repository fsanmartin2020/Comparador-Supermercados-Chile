"""Rotación de User-Agents y proxies para reducir bloqueos anti-bot.

Mantiene una lista curada de UAs recientes y entrega uno por invocación
de forma aleatoria. La rotación por sí sola no basta frente a WAFs serios
(Akamai, DataDome): para esos casos el scraper correspondiente debe usar
``undetected_chromedriver`` además de rotar UA.
"""

from __future__ import annotations

import random

from config import PROXIES

# Pool de UAs actualizados (Chrome y Firefox en Windows/macOS).
_USER_AGENTS: tuple[str, ...] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
    "Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
)


def random_user_agent() -> str:
    """Devuelve un User-Agent aleatorio del pool."""
    return random.choice(_USER_AGENTS)


def random_proxy() -> str | None:
    """Devuelve un proxy aleatorio configurado en ``.env`` o ``None``."""
    return random.choice(PROXIES) if PROXIES else None

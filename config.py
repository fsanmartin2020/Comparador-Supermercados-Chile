"""Configuración central del proyecto.

Contiene constantes compartidas por todos los scrapers y la orquestación:
categorías a buscar, timeouts, rutas de salida y credenciales.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga variables desde .env (silencioso si no existe, útil en CI).
load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
LOGS_DIR = ROOT_DIR / "logs"
LOCAL_CSV_PATH = ROOT_DIR / "Listado-Supermercado.csv"

# URL pública del CSV usado como fuente de verdad histórica.
REMOTE_CSV_URL = (
    "https://raw.githubusercontent.com/fsanmartin2020/"
    "Comparador-Supermercados-Chile/refs/heads/main/Listado-Supermercado.csv"
)

# Categorías a buscar en cada supermercado.
# Alimentos básicos no perecibles + productos de limpieza del hogar.
CATEGORIAS_BUSQUEDA: list[str] = [
    # --- Alimentos originales ---
    "Tallarín",
    "Jurel",
    "Leche Entera",
    "Frac",
    "Porotos",
    # --- Alimentos no perecibles ---
    "Arroz",
    "Aceite",
    "Azúcar",
    "Harina",
    "Atún",
    "Café",
    "Té",
    "Salsa de Tomate",
    # --- Productos de limpieza ---
    "Detergente",
    "Suavizante",
    "Cloro",
    "Lavaloza",
    "Papel Higiénico",
    "Toalla de Papel",
    "Jabón de Mano",
]

# Columnas del DataFrame final.
COLUMNAS = [
    "Supermercado",
    "Marca",
    "Producto",
    "Precio",
    "Categoria",
    "Enlace",
    "Fecha",
    "porMayor",
]

# Timeouts y reintentos de scraping.
PAGE_LOAD_TIMEOUT_S = 45
WAIT_AFTER_LOAD_MIN_S = 5
WAIT_AFTER_LOAD_MAX_S = 10
WAIT_HARDENED_MIN_S = 12
WAIT_HARDENED_MAX_S = 24
MAX_RETRIES = 3

# Concurrencia: cada scraper abre un Chrome, cuidar RAM en runners de CI.
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "3"))

# Credenciales y destino de subida.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "fsanmartin2020/Comparador-Supermercados-Chile")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_CSV_PATH = os.getenv("GITHUB_CSV_PATH", "Listado-Supermercado.csv")

# Proxies opcionales (lista separada por coma).
PROXIES: list[str] = [p.strip() for p in os.getenv("PROXIES", "").split(",") if p.strip()]

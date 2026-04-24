"""Subida del CSV resultante a un repositorio de GitHub vía API REST.

Usa un token personal cargado desde variables de entorno (nunca se
hardcodea) y ejecuta un commit-then-update: obtiene el SHA actual del
archivo y lo reemplaza, o lo crea si no existe.
"""

from __future__ import annotations

import base64
from io import StringIO

import pandas as pd
import requests

from config import GITHUB_BRANCH, GITHUB_CSV_PATH, GITHUB_REPO, GITHUB_TOKEN
from utils.logger import get_logger

_LOGGER = get_logger(__name__)
_API_BASE = "https://api.github.com"


class GitHubUploadError(RuntimeError):
    """Error de red o de autorización al subir el CSV."""


def _headers() -> dict[str, str]:
    if not GITHUB_TOKEN:
        raise GitHubUploadError(
            "GITHUB_TOKEN no está configurado. Copia .env.example como .env."
        )
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def _obtener_sha_remoto(url: str) -> str | None:
    """Devuelve el SHA del archivo remoto si existe, o None."""
    respuesta = requests.get(url, headers=_headers(), timeout=30)
    if respuesta.status_code == 200:
        return respuesta.json().get("sha")
    if respuesta.status_code == 404:
        return None
    raise GitHubUploadError(
        f"No se pudo consultar el archivo remoto ({respuesta.status_code}): "
        f"{respuesta.text}"
    )


def subir_csv(df: pd.DataFrame, mensaje_commit: str = "Actualización semanal CSV") -> None:
    """Sube ``df`` como CSV al repositorio configurado en ``config.py``.

    Args:
        df: DataFrame con la información ya limpia.
        mensaje_commit: Mensaje asociado al commit en GitHub.

    Raises:
        GitHubUploadError: Si no hay token o la API devuelve un error.
    """
    url = f"{_API_BASE}/repos/{GITHUB_REPO}/contents/{GITHUB_CSV_PATH}"

    buffer = StringIO()
    df.to_csv(buffer, index=True, index_label="Id")
    contenido_b64 = base64.b64encode(buffer.getvalue().encode()).decode()

    sha = _obtener_sha_remoto(url)
    payload: dict[str, object] = {
        "message": mensaje_commit,
        "content": contenido_b64,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    respuesta = requests.put(url, json=payload, headers=_headers(), timeout=60)
    if respuesta.status_code not in (200, 201):
        raise GitHubUploadError(
            f"Fallo al subir CSV ({respuesta.status_code}): {respuesta.text}"
        )
    _LOGGER.info("CSV subido correctamente a %s@%s", GITHUB_REPO, GITHUB_BRANCH)

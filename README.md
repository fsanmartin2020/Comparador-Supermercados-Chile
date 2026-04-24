# Comparador de Supermercados Chile

Pipeline de scraping semanal que compara precios entre **Jumbo, Santa Isabel, Lider, Unimarc, Acuenta y Alvi**, consolida los datos en un CSV y los publica en GitHub para ser consumidos por Power BI.

![Dashboard principal](https://github.com/user-attachments/assets/8e35f0cc-f6dd-4661-b194-6744cac4b52c)
![Dashboard secundario](https://github.com/user-attachments/assets/cf40aba5-75aa-4dd6-b960-0a48047a66f3)

---

## Arquitectura

```
Comparador-Supermercados-Chile-main/
├── main.py                  # Orquestador (paralelismo + consolidación + subida)
├── config.py                # Constantes y carga de .env
├── requirements.txt
├── .env.example             # Plantilla de variables de entorno (nunca commitear .env)
├── scrapers/
│   ├── base.py              # Clase abstracta BaseScraper
│   ├── vtex.py              # Lógica común Jumbo / Santa Isabel
│   ├── smu.py               # Lógica común Unimarc / Alvi
│   ├── walmart.py           # Lógica común Lider / Acuenta (undetected)
│   ├── jumbo.py · santa_isabel.py · unimarc.py · alvi.py · lider.py · acuenta.py
│   └── __init__.py          # Factory: SCRAPERS_DISPONIBLES
├── utils/
│   ├── logger.py            # logging con archivo rotativo
│   ├── cleaning.py          # limpieza de precios y texto
│   ├── normalization.py     # normalización y fuzzy matching de productos
│   ├── user_agents.py       # rotación de UA y proxies opcionales
│   └── github_uploader.py   # subida a GitHub vía API REST
├── .github/workflows/
│   └── weekly_scrape.yml    # Ejecución programada semanal en CI
├── logs/                    # Logs de ejecuciones (no se commitean)
└── Listado-Supermercado.csv # CSV resultante consumido por Power BI
```

### Patrón de diseño

- **Template Method** en `BaseScraper`: define el ciclo de vida (crear driver → navegar → parsear → cerrar) y delega en subclases los detalles específicos (`construir_url`, `parsear`).
- **Factory** en `scrapers/__init__.py`: `SCRAPERS_DISPONIBLES` lista las clases concretas. Agregar un nuevo supermercado solo requiere crear la subclase y registrarla aquí.
- **Reutilización por familia**: tiendas que comparten infraestructura comparten clase intermedia:
  - `VTEXScraper` → Jumbo, Santa Isabel
  - `SMUScraper` → Unimarc, Alvi
  - `WalmartScraper` → Lider, Acuenta (fuerza `undetected_chromedriver`)

---

## Setup local

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Editar .env y colocar el GITHUB_TOKEN real.
```

### Variables de entorno

| Variable          | Descripción                                                       |
|-------------------|-------------------------------------------------------------------|
| `GITHUB_TOKEN`    | PAT de GitHub con permisos de `contents:write`. **Nunca commitear.** |
| `GITHUB_REPO`     | `usuario/repo` destino del CSV.                                   |
| `GITHUB_BRANCH`   | Rama destino (default: `main`).                                   |
| `GITHUB_CSV_PATH` | Path del CSV dentro del repo.                                     |
| `PROXIES`         | (Opcional) Lista de proxies HTTP separados por coma.              |
| `MAX_WORKERS`     | (Opcional) Hilos concurrentes; default `3`.                       |

---

## Ejecución

```bash
# Pipeline completo: scraping + consolidación + subida a GitHub
python main.py

# Solo scraping + guardar localmente, sin tocar GitHub
python main.py --dry-run

# Ejecutar un subconjunto de tiendas
python main.py --solo Jumbo Unimarc

# Sobrescribir categorías
python main.py --categorias "Arroz" "Atún" "Harina"
```

---

## Automatización con GitHub Actions

El workflow `.github/workflows/weekly_scrape.yml` corre cada **lunes 09:00 UTC** y también se puede disparar manualmente desde la pestaña _Actions_ del repo.

1. En el repo, ir a **Settings → Secrets and variables → Actions**.
2. Crear un secret llamado `SCRAPER_PAT` con un _fine-grained personal access token_ que tenga permiso `Contents: Read/Write` sobre el repo destino.
3. (Opcional) Editar el cron en el workflow si se prefiere otra frecuencia.

Power BI queda apuntando al CSV público y se refresca automáticamente.

---

## Recomendación: Script vs. Web App

**Opción A (recomendada): script automatizado + dashboard**

- Pro: GitHub Actions es gratis para repos públicos, corre Chrome sin problema, y el CSV resultante se sirve estático (rápido, sin costos).
- Pro: Power BI / Streamlit leen el CSV ya procesado; la UI carga en <1s sin depender de Selenium.
- Contra: los datos se actualizan semanalmente, no en tiempo real.

**Opción B: Web App con scraping on-demand (Streamlit/Dash)**

- Contra: ejecutar Selenium/undetected-chromedriver en servidores gratuitos (Streamlit Cloud, Render free) suele **fallar** por límites de RAM y ausencia de Chrome en la imagen.
- Contra: cada visita gatilla scraping de 6 tiendas → UX lento (~30-60s) y riesgo de bloqueos (cada sesión nueva es un IP sospechoso).
- Contra: costo real en cualquier opción paga (Fly.io, Railway con Chrome) es alto para un caso de uso personal.

**Veredicto**: mantener **Opción A** y, si se quiere una UI web además de Power BI, hacer una Streamlit app _separada_ que solo lea el CSV público (cero Selenium en runtime). Mejor de ambos mundos.

---

## Mejoras implementadas sobre el notebook original

1. **Arquitectura**: funciones sueltas → clase base + subclases (Factory Pattern).
2. **Concurrencia**: `concurrent.futures.ThreadPoolExecutor` para paralelizar tiendas no-Walmart (evita bloqueos Akamai).
3. **Robustez**: reintentos con backoff exponencial (`tenacity`), `try/except` por tarjeta de producto para que un cambio de DOM no mate la corrida.
4. **Anti-bloqueo**: rotación de User-Agent, soporte opcional de proxies, `undetected_chromedriver` para Lider y Acuenta.
5. **Nuevas tiendas**: Acuenta (Walmart) y Alvi (SMU).
6. **Limpieza de datos**: filtrado de precios `0` antes de subir, columna `ProductoNormalizado` para matching cross-store en Power BI.
7. **Logging**: módulo `logging` con archivo rotativo en `logs/` + artefacto en GitHub Actions.
8. **Seguridad**: eliminación de tokens hardcodeados; `python-dotenv` + secretos de GitHub Actions.
9. **Automatización**: workflow semanal con `workflow_dispatch` manual.

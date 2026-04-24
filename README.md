# Comparador de Supermercados Chile

> 🌐 **Web en vivo:** [comparador-super-chile.netlify.app](https://comparador-super-chile.netlify.app)

Pipeline de scraping semanal que compara precios entre **Jumbo, Santa Isabel, Lider, Unimarc, Acuenta y Alvi**, consolida los datos en un CSV público y los visualiza en una web app interactiva desplegada en Netlify.

---

## ¿Cómo funciona?

```
Cada lunes (GitHub Actions)
  └─► python main.py          # scraping de 6 supermercados × 20 categorías
        └─► Listado-Supermercado.csv  # CSV público en este repo
              └─► Web App (Netlify)   # lee el CSV, calcula gaps, muestra la UI
```

La web no tiene backend ni base de datos: consume directamente el CSV crudo de GitHub vía `fetch`, lo parsea en el browser con PapaParse y calcula en tiempo real qué productos tienen mayor diferencia de precio entre supermercados.

---

## Web App

Stack: **Vite + React**, CSS custom (dark mode, glassmorphism), sin dependencias de UI pesadas.

Secciones principales:
- **Mayores oportunidades de ahorro** — productos ordenados por gap de precio (más caro vs más barato), con filtros por categoría y link directo a cada tienda.
- **Todos los precios** — tabla completa con búsqueda, ordenamiento por columna y paginación. Verde = más barato, Rojo = más caro.
- **Por categoría** — resumen de cuál supermercado es más barato en promedio por grupo de productos.

Para correr localmente:
```bash
cd web
npm install
npm run dev
```

---

## Arquitectura del scraper

```
├── main.py                  # Orquestador (paralelismo + consolidación + subida)
├── config.py                # Constantes y carga de .env — 20 categorías configuradas
├── requirements.txt
├── .env.example             # Plantilla de variables de entorno
├── scrapers/
│   ├── base.py              # Clase abstracta BaseScraper (Template Method)
│   ├── vtex.py              # Lógica común Jumbo / Santa Isabel
│   ├── smu.py               # Lógica común Unimarc / Alvi
│   ├── walmart.py           # Lógica común Lider / Acuenta (undetected-chromedriver)
│   ├── jumbo.py · santa_isabel.py · unimarc.py · alvi.py · lider.py · acuenta.py
│   └── __init__.py          # Factory: SCRAPERS_DISPONIBLES
├── utils/
│   ├── logger.py            # Logging con archivo rotativo
│   ├── cleaning.py          # Limpieza de precios y texto
│   ├── normalization.py     # Normalización y fuzzy matching de productos
│   ├── user_agents.py       # Rotación de UA y proxies opcionales
│   └── github_uploader.py   # Subida a GitHub vía API REST
├── .github/workflows/
│   └── weekly_scrape.yml    # Ejecución programada — cada lunes 09:00 UTC
├── web/                     # Web App (Vite + React)
│   ├── src/
│   │   ├── components/      # Header, Hero, StatsBar, GapCards, ProductTable, CategoryCards, Footer
│   │   ├── data/csvLoader.js
│   │   ├── hooks/useProducts.js
│   │   └── utils/           # formatters.js, priceAnalysis.js
│   └── netlify.toml
└── Listado-Supermercado.csv # CSV fuente de verdad (actualizado semanalmente)
```

### Patrones de diseño

- **Template Method** en `BaseScraper`: define el ciclo de vida (crear driver → navegar → parsear → cerrar) y delega en subclases los detalles específicos.
- **Factory** en `scrapers/__init__.py`: `SCRAPERS_DISPONIBLES` lista las clases concretas. Agregar un nuevo supermercado solo requiere crear la subclase y registrarla aquí.
- **Reutilización por familia**:
  - `VTEXScraper` → Jumbo, Santa Isabel
  - `SMUScraper` → Unimarc, Alvi
  - `WalmartScraper` → Lider, Acuenta (fuerza `undetected_chromedriver`)

---

## Categorías (20)

| Grupo | Productos |
|-------|-----------|
| Alimentos originales | Tallarín, Jurel, Leche Entera, Frac, Porotos |
| Alimentos no perecibles | Arroz, Aceite, Azúcar, Harina, Atún, Café, Té, Salsa de Tomate |
| Limpieza del hogar | Detergente, Suavizante, Cloro, Lavaloza, Papel Higiénico, Toalla de Papel, Jabón de Mano |

---

## Setup local (scraper)

```bash
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Editar .env con tu GITHUB_TOKEN
```

### Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `GITHUB_TOKEN` | PAT con permiso `contents:write`. **Nunca commitear.** |
| `GITHUB_REPO` | `usuario/repo` destino del CSV |
| `GITHUB_BRANCH` | Rama destino (default: `main`) |
| `GITHUB_CSV_PATH` | Path del CSV dentro del repo |
| `PROXIES` | (Opcional) Lista de proxies HTTP separados por coma |
| `MAX_WORKERS` | (Opcional) Hilos concurrentes; default `3` |

---

## Ejecución del scraper

```bash
# Pipeline completo: scraping + consolidación + subida a GitHub
python main.py

# Solo scraping local, sin subir a GitHub
python main.py --dry-run

# Ejecutar un subconjunto de tiendas
python main.py --solo Jumbo Unimarc

# Sobrescribir categorías
python main.py --categorias "Arroz" "Atún" "Harina"
```

---

## Automatización con GitHub Actions

El workflow corre cada **lunes 09:00 UTC** (~06:00 Chile) y también se puede disparar manualmente desde la pestaña _Actions_.

**Configuración requerida:**
1. Ir a **Settings → Secrets and variables → Actions**
2. Crear el secret `SCRAPER_PAT` con un PAT que tenga permiso `Contents: Read/Write`
3. El workflow actualiza el CSV → Netlify sirve los datos frescos automáticamente

---

## Mejoras implementadas sobre el notebook original

1. **Arquitectura**: funciones sueltas → clase base + subclases (Factory + Template Method).
2. **Concurrencia**: `ThreadPoolExecutor` para scrapers no-Walmart; serie para Lider/Acuenta.
3. **Robustez**: reintentos con backoff exponencial (`tenacity`), `try/except` por tarjeta.
4. **Anti-bloqueo**: rotación de User-Agent, proxies opcionales, `undetected_chromedriver`.
5. **20 categorías**: alimentos + limpieza (vs. 5 originales).
6. **Web App**: Vite + React con comparador interactivo, filtros y links directos.
7. **Limpieza de datos**: filtrado de precios `0`, columna `ProductoNormalizado`.
8. **Logging**: archivo rotativo en `logs/` + artefacto en GitHub Actions.
9. **Seguridad**: `python-dotenv` + secretos de GitHub Actions.

/**
 * Lógica central de análisis de precios.
 * Deduplicación, cálculo de gaps y rankings.
 */

export const SUPERMERCADOS = ['Jumbo', 'Santa Isabel', 'Unimarc', 'Lider', 'Alvi', 'Acuenta'];

/** Normaliza un nombre de producto para comparación cruzada */
function normalizar(nombre) {
  return nombre
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // quitar tildes
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Deduplica filas: para cada par (Producto + Supermercado),
 * conserva solo el registro con la fecha más reciente.
 */
export function deduplicar(rows) {
  const map = new Map();
  for (const row of rows) {
    if (!row.Producto || !row.Supermercado || row.Precio <= 0) continue;
    const key = `${row.Supermercado}||${normalizar(row.Producto)}`;
    const existing = map.get(key);
    if (!existing || row.Fecha > existing.Fecha) {
      map.set(key, row);
    }
  }
  return Array.from(map.values());
}

/**
 * Agrupa productos por categoría y nombre normalizado,
 * devuelve un mapa { nombreNorm → [rows...] } para una categoría dada.
 */
export function agruparPorProducto(rows) {
  const map = new Map();
  for (const row of rows) {
    const key = normalizar(row.Producto);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(row);
  }
  return map;
}

/**
 * Calcula el gap para un grupo de filas del mismo producto (distintas tiendas).
 *
 * Métricas:
 *  - gapPesos / gapPct : más barato vs precio PROMEDIO (métrica principal)
 *    → detecta si un precio es realmente barato o si otro supermercado
 *      tiene un sobreprecio puntual que infla la brecha.
 *  - gapVsSegundo      : más barato vs 2do más barato
 *    → permite ver si el precio más bajo es una oferta real o
 *      simplemente el precio normal de mercado.
 *  - gapVsMaximo       : más barato vs más caro (referencia)
 *
 * Retorna null si el producto aparece en menos de 2 tiendas.
 */
export function calcularGap(filas) {
  if (filas.length < 2) return null;

  const sorted = [...filas].sort((a, b) => a.Precio - b.Precio);
  const masBarato       = sorted[0];
  const segundoMasBarato = sorted[1];
  const masCaro         = sorted[sorted.length - 1];

  // Promedio de todos los precios
  const promedio = sorted.reduce((acc, f) => acc + f.Precio, 0) / sorted.length;

  // Métrica principal: más barato vs promedio
  const gapPesos = promedio - masBarato.Precio;
  const gapPct   = promedio > 0 ? (gapPesos / promedio) * 100 : 0;

  // Métrica secundaria: 1ro vs 2do más barato (¿es una oferta real?)
  const gapVsSegundo    = segundoMasBarato.Precio - masBarato.Precio;
  const gapVsSegundoPct = segundoMasBarato.Precio > 0
    ? (gapVsSegundo / segundoMasBarato.Precio) * 100
    : 0;

  // Métrica de referencia: más barato vs más caro
  const gapVsMaximo    = masCaro.Precio - masBarato.Precio;
  const gapVsMaximoPct = masCaro.Precio > 0
    ? (gapVsMaximo / masCaro.Precio) * 100
    : 0;

  if (gapPesos <= 0) return null;

  return {
    producto: masBarato.Producto,
    marca: masBarato.Marca || masCaro.Marca || '',
    categoria: masBarato.Categoria,
    masBarato,
    segundoMasBarato,
    masCaro,
    promedio,
    gapPesos,         // más barato vs promedio (principal)
    gapPct,
    gapVsSegundo,     // más barato vs 2do más barato
    gapVsSegundoPct,
    gapVsMaximo,      // más barato vs más caro (referencia)
    gapVsMaximoPct,
    todasLasTiendas: sorted, // de más barato a más caro
  };
}

/**
 * Pipeline completo de análisis:
 * 1. Deduplica
 * 2. Agrupa por producto dentro de cada categoría
 * 3. Calcula gap para cada grupo
 * 4. Ordena por mayor gap en pesos
 */
export function analizarPrecios(rows) {
  const dedup = deduplicar(rows);

  // Agrupar por categoría primero
  const porCategoria = new Map();
  for (const row of dedup) {
    const cat = row.Categoria || 'Sin categoría';
    if (!porCategoria.has(cat)) porCategoria.set(cat, []);
    porCategoria.get(cat).push(row);
  }

  const gaps = [];
  for (const [, filasCat] of porCategoria) {
    const grupos = agruparPorProducto(filasCat);
    for (const [, filas] of grupos) {
      const gap = calcularGap(filas);
      if (gap) gaps.push(gap);
    }
  }

  // Ordenar por mayor gap vs promedio (métrica principal)
  gaps.sort((a, b) => b.gapPesos - a.gapPesos);
  return gaps;
}

/**
 * Stats globales del dataset para mostrar en el header.
 */
export function calcularStats(rows, gaps) {
  const dedup = deduplicar(rows);
  const supermercados = [...new Set(dedup.map((r) => r.Supermercado))];
  const categorias = [...new Set(dedup.map((r) => r.Categoria))].filter(Boolean);
  const fechas = dedup.map((r) => r.Fecha).filter(Boolean).sort();
  const ultimaFecha = fechas[fechas.length - 1] || '';

  // Supermercado más barato: el que gana más gaps como masBarato
  const wins = {};
  for (const g of gaps) {
    const s = g.masBarato.Supermercado;
    wins[s] = (wins[s] || 0) + 1;
  }
  const supMasBarato = Object.entries(wins).sort((a, b) => b[1] - a[1])[0]?.[0] || '';

  return {
    totalProductos: dedup.length,
    totalCategorias: categorias.length,
    totalSupermercados: supermercados.length,
    ultimaFecha,
    supMasBarato,
    totalGaps: gaps.length,
    mayorAhorro: gaps[0] || null,
  };
}

/**
 * Devuelve la tabla pivot: lista de productos únicos con precio por supermercado.
 * Útil para la tabla comparativa completa.
 */
export function construirTabla(rows) {
  const dedup = deduplicar(rows);

  // Agrupar por producto normalizado
  const grupos = agruparPorProducto(dedup);

  const tabla = [];
  for (const [, filas] of grupos) {
    if (filas.length < 1) continue;

    const base = filas[0];
    const precios = {};
    for (const f of filas) {
      precios[f.Supermercado] = f.Precio;
    }

    const preciosArr = Object.values(precios).filter((p) => p > 0);
    const minPrecio = preciosArr.length ? Math.min(...preciosArr) : 0;
    const maxPrecio = preciosArr.length ? Math.max(...preciosArr) : 0;
    const gap = maxPrecio - minPrecio;
    const gapPct = maxPrecio > 0 ? (gap / maxPrecio) * 100 : 0;

    tabla.push({
      producto: base.Producto,
      marca: base.Marca || '',
      categoria: base.Categoria || '',
      precios,
      minPrecio,
      maxPrecio,
      gap,
      gapPct,
      enlaceBarato: filas.find((f) => f.Precio === minPrecio)?.Enlace || '',
    });
  }

  return tabla.sort((a, b) => b.gap - a.gap);
}

/**
 * Formatea un número como precio en pesos chilenos.
 * Ej: 1990 → "$1.990"
 */
export function formatPrecio(precio) {
  if (!precio || isNaN(precio)) return '—';
  return '$' + Math.round(precio).toLocaleString('es-CL');
}

/**
 * Formatea una diferencia de precio con signo y color.
 */
export function formatGap(gap) {
  return '$' + Math.round(Math.abs(gap)).toLocaleString('es-CL');
}

/**
 * Formatea un porcentaje de ahorro.
 * Ej: 12.5 → "12.5%"
 */
export function formatPct(pct) {
  if (isNaN(pct)) return '—';
  return Math.round(pct) + '%';
}

/**
 * Formatea una fecha ISO a "DD/MM/AAAA".
 */
export function formatFecha(fechaStr) {
  if (!fechaStr) return '—';
  const [y, m, d] = fechaStr.split('-');
  return `${d}/${m}/${y}`;
}

/**
 * Formatea una fecha ISO a string legible tipo "1 oct 2024".
 */
export function formatFechaLegible(fechaStr) {
  if (!fechaStr) return '—';
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  const [y, m, d] = fechaStr.split('-');
  return `${parseInt(d)} ${meses[parseInt(m) - 1]} ${y}`;
}

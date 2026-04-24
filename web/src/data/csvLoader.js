import Papa from 'papaparse';

// URL pública del CSV — mismo que en config.py
const CSV_URL =
  'https://raw.githubusercontent.com/1bryanvalenzuela/Comparador-Supermercados-Chile/refs/heads/main/Listado-Supermercado.csv';

/**
 * Descarga y parsea el CSV público de GitHub.
 * Retorna un array de objetos con las filas del CSV.
 */
export async function fetchProductos() {
  const res = await fetch(CSV_URL);
  if (!res.ok) throw new Error(`No se pudo obtener el CSV: ${res.status}`);
  const text = await res.text();

  const { data, errors } = Papa.parse(text, {
    header: true,
    skipEmptyLines: true,
    dynamicTyping: false,
    transformHeader: (h) => h.trim(),
    transform: (v) => v.trim(),
  });

  if (errors.length > 0) {
    console.warn('PapaParse warnings:', errors);
  }

  // Normalizar tipos
  return data.map((row) => ({
    ...row,
    Precio: parseFloat(row.Precio) || 0,
    porMayor: row.porMayor === 'True' || row.porMayor === 'true' || row.porMayor === '1',
  }));
}

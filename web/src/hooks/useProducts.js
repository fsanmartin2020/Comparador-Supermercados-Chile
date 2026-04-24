import { useState, useEffect, useMemo } from 'react';
import { fetchProductos } from '../data/csvLoader';
import { analizarPrecios, calcularStats, construirTabla } from '../utils/priceAnalysis';

/**
 * Hook central: carga el CSV, deduplica, calcula gaps y estadísticas.
 * Expone estado de loading, error y datos procesados.
 */
export function useProducts() {
  const [rawRows, setRawRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProductos()
      .then((rows) => {
        setRawRows(rows);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Error al cargar datos');
        setLoading(false);
      });
  }, []);

  const gaps = useMemo(() => analizarPrecios(rawRows), [rawRows]);
  const tabla = useMemo(() => construirTabla(rawRows), [rawRows]);
  const stats = useMemo(() => calcularStats(rawRows, gaps), [rawRows, gaps]);
  const categorias = useMemo(
    () => [...new Set(rawRows.map((r) => r.Categoria).filter(Boolean))].sort(),
    [rawRows]
  );

  return { loading, error, gaps, tabla, stats, categorias, rawRows };
}

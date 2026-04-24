import { useState, useMemo, useEffect, useRef } from 'react';
import { Search, ArrowUpDown, ExternalLink, ChevronUp, ChevronDown } from 'lucide-react';
import { formatPrecio } from '../utils/formatters';
import { SUPERMERCADOS } from '../utils/priceAnalysis';
import './ProductTable.css';

function PrecioCell({ precio, isMin, isMax }) {
  if (!precio) return <td className="pt-cell pt-cell--empty">—</td>;
  return (
    <td className={`pt-cell ${isMin ? 'pt-cell--best' : isMax ? 'pt-cell--worst' : ''}`}>
      <span className="price-num">{formatPrecio(precio)}</span>
    </td>
  );
}

function SortIcon({ field, sortField, sortDir }) {
  if (sortField !== field) return <ArrowUpDown size={13} className="pt-sort-icon" />;
  return sortDir === 'asc' ? <ChevronUp size={13} className="pt-sort-icon active" /> : <ChevronDown size={13} className="pt-sort-icon active" />;
}

export default function ProductTable({ tabla, categorias, loading }) {
  const [query, setQuery]           = useState('');
  const [filtroCateg, setFiltroCateg] = useState('Todos');
  const [sortField, setSortField]   = useState('gap');
  const [sortDir, setSortDir]       = useState('desc');
  const [pagina, setPagina]         = useState(0);
  const PER_PAGE = 20;

  // Supermercados con datos reales
  const supersConDatos = useMemo(() => {
    const set = new Set();
    for (const row of tabla) Object.keys(row.precios).forEach(s => set.add(s));
    return SUPERMERCADOS.filter(s => set.has(s));
  }, [tabla]);

  const filtrada = useMemo(() => {
    let rows = tabla;
    if (query.trim()) {
      const q = query.toLowerCase();
      rows = rows.filter(r =>
        r.producto.toLowerCase().includes(q) ||
        r.marca.toLowerCase().includes(q) ||
        r.categoria.toLowerCase().includes(q)
      );
    }
    if (filtroCateg !== 'Todos') rows = rows.filter(r => r.categoria === filtroCateg);

    return [...rows].sort((a, b) => {
      let va, vb;
      if (sortField === 'gap')       { va = a.gap; vb = b.gap; }
      else if (sortField === 'min')  { va = a.minPrecio; vb = b.minPrecio; }
      else if (sortField === 'pct')  { va = a.gapPct; vb = b.gapPct; }
      else { va = a.producto; vb = b.producto; }
      if (typeof va === 'string') return sortDir === 'asc' ? va.localeCompare(vb, 'es') : vb.localeCompare(va, 'es');
      return sortDir === 'asc' ? va - vb : vb - va;
    });
  }, [tabla, query, filtroCateg, sortField, sortDir]);

  const paginas = Math.ceil(filtrada.length / PER_PAGE);
  const visible = filtrada.slice(pagina * PER_PAGE, (pagina + 1) * PER_PAGE);

  function toggleSort(field) {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortField(field); setSortDir('desc'); }
    setPagina(0);
  }

  // Reset page on filter change
  useEffect(() => setPagina(0), [query, filtroCateg]);

  return (
    <section id="tabla" className="pt-section">
      <div className="container">
        <div className="pt-header">
          <div>
            <p className="section-label">Comparador completo</p>
            <h2 className="pt-title">Todos los precios</h2>
            <p className="pt-subtitle">
              {filtrada.length} producto{filtrada.length !== 1 ? 's' : ''} · Verde = más barato · Rojo = más caro
            </p>
          </div>
        </div>

        {/* Barra de búsqueda + filtros */}
        <div className="pt-controls">
          <div className="pt-search-wrap">
            <Search size={16} className="pt-search-icon" />
            <input
              type="search"
              className="pt-search"
              placeholder="Buscar producto, marca o categoría…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              aria-label="Buscar productos"
            />
          </div>
          <div className="pt-filters">
            <button className={`filter-chip ${filtroCateg === 'Todos' ? 'active' : ''}`} onClick={() => setFiltroCateg('Todos')}>
              Todos
            </button>
            {categorias.map(c => (
              <button key={c} className={`filter-chip ${filtroCateg === c ? 'active' : ''}`} onClick={() => setFiltroCateg(c)}>
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Tabla */}
        <div className="pt-wrap">
          {loading ? (
            <div className="pt-loading">
              {Array.from({length: 8}).map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 52, marginBottom: 4 }} />
              ))}
            </div>
          ) : (
            <table className="pt-table" role="grid">
              <thead>
                <tr>
                  <th className="pt-th pt-th--producto">
                    <button className="pt-sort-btn" onClick={() => toggleSort('nombre')} aria-label="Ordenar por nombre">
                      Producto <SortIcon field="nombre" sortField={sortField} sortDir={sortDir} />
                    </button>
                  </th>
                  <th className="pt-th">Categoría</th>
                  {supersConDatos.map(s => (
                    <th key={s} className="pt-th pt-th--super">{s}</th>
                  ))}
                  <th className="pt-th">
                    <button className="pt-sort-btn" onClick={() => toggleSort('min')} aria-label="Ordenar por precio mínimo">
                      Precio min <SortIcon field="min" sortField={sortField} sortDir={sortDir} />
                    </button>
                  </th>
                  <th className="pt-th">
                    <button className="pt-sort-btn" onClick={() => toggleSort('gap')} aria-label="Ordenar por diferencia">
                      Diferencia <SortIcon field="gap" sortField={sortField} sortDir={sortDir} />
                    </button>
                  </th>
                  <th className="pt-th">
                    <button className="pt-sort-btn" onClick={() => toggleSort('pct')} aria-label="Ordenar por ahorro %">
                      Ahorro % <SortIcon field="pct" sortField={sortField} sortDir={sortDir} />
                    </button>
                  </th>
                  <th className="pt-th">Comprar</th>
                </tr>
              </thead>
              <tbody>
                {visible.length === 0 ? (
                  <tr>
                    <td colSpan={supersConDatos.length + 6} className="pt-empty">
                      <Search size={32} strokeWidth={1} />
                      <span>Sin resultados para "{query || filtroCateg}"</span>
                    </td>
                  </tr>
                ) : visible.map((row, i) => (
                  <tr key={`${row.producto}-${i}`} className="pt-row">
                    <td className="pt-td pt-td--producto">
                      <div className="pt-nombre" title={row.producto}>{row.producto}</div>
                      {row.marca && <div className="pt-marca">{row.marca}</div>}
                    </td>
                    <td className="pt-td">
                      <span className="badge badge-blue">{row.categoria}</span>
                    </td>
                    {supersConDatos.map(s => (
                      <PrecioCell
                        key={s}
                        precio={row.precios[s]}
                        isMin={row.precios[s] === row.minPrecio && row.minPrecio > 0}
                        isMax={row.precios[s] === row.maxPrecio && row.gap > 0}
                      />
                    ))}
                    <td className="pt-td">
                      <span className="price-num pt-min-precio">{formatPrecio(row.minPrecio)}</span>
                    </td>
                    <td className="pt-td">
                      <span className="price-num pt-gap">{row.gap > 0 ? formatPrecio(row.gap) : '—'}</span>
                    </td>
                    <td className="pt-td">
                      {row.gapPct > 0 ? (
                        <span className={`badge ${row.gapPct >= 20 ? 'badge-green' : row.gapPct >= 10 ? 'badge-yellow' : 'badge-blue'}`}>
                          {Math.round(row.gapPct)}%
                        </span>
                      ) : '—'}
                    </td>
                    <td className="pt-td">
                      {row.enlaceBarato ? (
                        <a href={row.enlaceBarato} target="_blank" rel="noopener noreferrer" className="pt-link" aria-label={`Comprar ${row.producto}`}>
                          <ExternalLink size={14} />
                        </a>
                      ) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Paginación */}
        {paginas > 1 && (
          <div className="pt-pagination">
            <button className="btn-ghost" onClick={() => setPagina(p => Math.max(0, p-1))} disabled={pagina === 0}>
              Anterior
            </button>
            <span className="pt-pag-info">
              Página {pagina + 1} de {paginas}
            </span>
            <button className="btn-ghost" onClick={() => setPagina(p => Math.min(paginas-1, p+1))} disabled={pagina >= paginas-1}>
              Siguiente
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

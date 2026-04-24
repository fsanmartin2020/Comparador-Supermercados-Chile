import { useState, useEffect, useRef } from 'react';
import { ExternalLink, TrendingDown, ArrowRight } from 'lucide-react';
import { formatPrecio, formatGap, formatPct } from '../utils/formatters';
import './GapCards.css';

const SUPERMERCADO_COLORS = {
  Jumbo:          { bg: 'rgba(34,83,180,0.12)', border: 'rgba(34,83,180,0.3)', text: '#6ba4ff' },
  'Santa Isabel': { bg: 'rgba(220,38,38,0.12)', border: 'rgba(220,38,38,0.3)',  text: '#f87171' },
  Unimarc:        { bg: 'rgba(124,58,237,0.12)', border: 'rgba(124,58,237,0.3)', text: '#a78bfa' },
  Lider:          { bg: 'rgba(234,179,8,0.12)',  border: 'rgba(234,179,8,0.3)',  text: '#fbbf24' },
  Alvi:           { bg: 'rgba(34,197,94,0.12)',  border: 'rgba(34,197,94,0.3)',  text: '#4ade80' },
  Acuenta:        { bg: 'rgba(251,146,60,0.12)', border: 'rgba(251,146,60,0.3)', text: '#fb923c' },
};

function SuperBadge({ nombre }) {
  const s = SUPERMERCADO_COLORS[nombre] || { bg: 'var(--bg-card)', border: 'var(--border)', text: 'var(--text-secondary)' };
  return (
    <span className="super-badge" style={{ background: s.bg, borderColor: s.border, color: s.text }}>
      {nombre}
    </span>
  );
}

function GapCard({ gap, index }) {
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) el.classList.add('visible'); },
      { threshold: 0.1 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const { producto, marca, categoria, masBarato, masCaro, gapPesos, gapPct, todasLasTiendas } = gap;

  return (
    <div
      ref={ref}
      className="gap-card glass-card fade-in"
      style={{ transitionDelay: `${index * 60}ms` }}
    >
      {/* Header de la card */}
      <div className="gap-card__header">
        <div className="gap-card__meta">
          <span className="badge badge-blue">{categoria}</span>
          {marca && <span className="gap-card__marca">{marca}</span>}
        </div>
        <div className="gap-card__savings-badge">
          <TrendingDown size={12} />
          Ahorrás {formatPct(gapPct)}
        </div>
      </div>

      {/* Nombre del producto */}
      <h3 className="gap-card__nombre" title={producto}>{producto}</h3>

      {/* Lista de tiendas ordenadas */}
      <div className="gap-card__tiendas">
        {todasLasTiendas.map((t, i) => {
          const esMasBarato = t.Supermercado === masBarato.Supermercado;
          const esMasCaro   = t.Supermercado === masCaro.Supermercado;
          return (
            <div
              key={i}
              className={`gap-card__tienda ${esMasBarato ? 'gap-card__tienda--best' : ''} ${esMasCaro ? 'gap-card__tienda--worst' : ''}`}
            >
              <div className="gap-card__tienda-left">
                {esMasBarato && <span className="gap-card__best-dot" aria-label="Más barato" />}
                {esMasCaro   && <span className="gap-card__worst-dot" aria-label="Más caro" />}
                {!esMasBarato && !esMasCaro && <span className="gap-card__neutral-dot" />}
                <SuperBadge nombre={t.Supermercado} />
              </div>
              <span className={`gap-card__precio price-num ${esMasBarato ? 'text-green' : esMasCaro ? 'text-red' : ''}`}>
                {formatPrecio(t.Precio)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Footer — ahorro y link */}
      <div className="gap-card__footer">
        <div className="gap-card__ahorro">
          <span className="gap-card__ahorro-label">Diferencia</span>
          <span className="gap-card__ahorro-valor price-num">{formatGap(gapPesos)}</span>
        </div>
        {masBarato.Enlace && (
          <a
            href={masBarato.Enlace}
            target="_blank"
            rel="noopener noreferrer"
            className="gap-card__link btn-primary"
            aria-label={`Ver ${producto} en ${masBarato.Supermercado}`}
          >
            Ver en {masBarato.Supermercado}
            <ExternalLink size={13} />
          </a>
        )}
      </div>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="gap-card glass-card">
      <div className="skeleton" style={{ height: 20, width: '40%', marginBottom: 12 }} />
      <div className="skeleton" style={{ height: 22, width: '80%', marginBottom: 16 }} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {[1,2,3].map(i => (
          <div key={i} className="skeleton" style={{ height: 36 }} />
        ))}
      </div>
      <div className="skeleton" style={{ height: 40, marginTop: 16 }} />
    </div>
  );
}

export default function GapCards({ gaps, categorias, loading }) {
  const [filtro, setFiltro] = useState('Todos');
  const [mostrar, setMostrar] = useState(12);

  const filtrados = filtro === 'Todos'
    ? gaps
    : gaps.filter((g) => g.categoria === filtro);

  const visibles = filtrados.slice(0, mostrar);

  return (
    <section id="ahorros" className="gapcards-section">
      <div className="container">
        {/* Título de sección */}
        <div className="gapcards-header">
          <div>
            <p className="section-label">Inteligencia de precios</p>
            <h2 className="gapcards-title">
              Mayores oportunidades de ahorro
            </h2>
            <p className="gapcards-subtitle">
              Productos con mayor diferencia de precio entre supermercados — de menor a mayor precio
            </p>
          </div>
        </div>

        {/* Filtros de categoría */}
        <div className="gapcards-filters" role="group" aria-label="Filtrar por categoría">
          <button
            className={`filter-chip ${filtro === 'Todos' ? 'active' : ''}`}
            onClick={() => { setFiltro('Todos'); setMostrar(12); }}
          >
            Todos
          </button>
          {categorias.map((cat) => (
            <button
              key={cat}
              className={`filter-chip ${filtro === cat ? 'active' : ''}`}
              onClick={() => { setFiltro(cat); setMostrar(12); }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Grid de cards */}
        <div className="gapcards-grid">
          {loading
            ? Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)
            : visibles.length > 0
              ? visibles.map((gap, i) => <GapCard key={`${gap.producto}-${i}`} gap={gap} index={i} />)
              : (
                <div className="gapcards-empty">
                  <TrendingDown size={40} strokeWidth={1} />
                  <p>No hay datos de precios para esta categoría todavía.</p>
                </div>
              )
          }
        </div>

        {/* Ver más */}
        {!loading && filtrados.length > mostrar && (
          <div className="gapcards-more">
            <button className="btn-ghost" onClick={() => setMostrar(m => m + 12)}>
              Ver más productos
              <ArrowRight size={16} />
            </button>
          </div>
        )}
      </div>
    </section>
  );
}

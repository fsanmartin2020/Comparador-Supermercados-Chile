import { useEffect, useRef } from 'react';
import { TrendingDown, ShoppingCart, Tag, RefreshCw, Award } from 'lucide-react';
import { formatFechaLegible, formatPrecio, formatGap } from '../utils/formatters';
import './StatsBar.css';

function AnimatedNumber({ value, prefix = '', suffix = '' }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current || !value) return;
    const target = Number(value);
    if (isNaN(target)) { ref.current.textContent = prefix + value + suffix; return; }
    const duration = 1200;
    const start = performance.now();
    const from = 0;

    function update(now) {
      const pct = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - pct, 3); // ease-out cubic
      const current = Math.round(from + ease * (target - from));
      if (ref.current) ref.current.textContent = prefix + current.toLocaleString('es-CL') + suffix;
      if (pct < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }, [value]);

  return <span ref={ref} className="price-num">—</span>;
}

export default function StatsBar({ stats, loading }) {
  const items = [
    {
      icon: <Tag size={18} />,
      label: 'Productos comparados',
      value: stats?.totalProductos,
      isNum: true,
    },
    {
      icon: <ShoppingCart size={18} />,
      label: 'Supermercados',
      value: stats?.totalSupermercados,
      isNum: true,
    },
    {
      icon: <Tag size={18} />,
      label: 'Categorías',
      value: stats?.totalCategorias,
      isNum: true,
    },
    {
      icon: <TrendingDown size={18} />,
      label: 'Mayor ahorro encontrado',
      value: stats?.mayorAhorro ? formatGap(stats.mayorAhorro.gapPesos) : null,
      isNum: false,
      highlight: true,
    },
    {
      icon: <Award size={18} />,
      label: 'Más veces más barato',
      value: stats?.supMasBarato || null,
      isNum: false,
    },
    {
      icon: <RefreshCw size={18} />,
      label: 'Última actualización',
      value: stats?.ultimaFecha ? formatFechaLegible(stats.ultimaFecha) : null,
      isNum: false,
    },
  ];

  return (
    <section className="statsbar">
      <div className="container">
        <div className="statsbar-grid">
          {items.map((item, i) => (
            <div key={i} className={`statsbar-item ${item.highlight ? 'statsbar-item--highlight' : ''}`}>
              <div className="statsbar-icon">{item.icon}</div>
              <div className="statsbar-content">
                <div className="statsbar-value price-num">
                  {loading ? (
                    <div className="skeleton" style={{ width: 60, height: 22 }} />
                  ) : item.isNum ? (
                    <AnimatedNumber value={item.value} />
                  ) : (
                    <span>{item.value || '—'}</span>
                  )}
                </div>
                <div className="statsbar-label">{item.label}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

import { useMemo } from 'react';
import { TrendingDown, Award } from 'lucide-react';
import { formatPrecio } from '../utils/formatters';
import { SUPERMERCADOS } from '../utils/priceAnalysis';
import './CategoryCards.css';

const CAT_ICONS = {
  'Tallarín':        '🍝',
  'Jurel':           '🐟',
  'Leche Entera':    '🥛',
  'Frac':            '🍪',
  'Porotos':         '🫘',
  'Arroz':           '🍚',
  'Aceite':          '🫙',
  'Azúcar':          '🍬',
  'Harina':          '🌾',
  'Atún':            '🐟',
  'Café':            '☕',
  'Té':              '🍵',
  'Salsa de Tomate': '🍅',
  'Detergente':      '🧺',
  'Suavizante':      '🌸',
  'Cloro':           '💧',
  'Lavaloza':        '🍽️',
  'Papel Higiénico': '🧻',
  'Toalla de Papel': '📄',
  'Jabón de Mano':   '🧼',
};

const CAT_GRUPOS = {
  'Alimentos originales': ['Tallarín', 'Jurel', 'Leche Entera', 'Frac', 'Porotos'],
  'Alimentos no perecibles': ['Arroz', 'Aceite', 'Azúcar', 'Harina', 'Atún', 'Café', 'Té', 'Salsa de Tomate'],
  'Productos de limpieza': ['Detergente', 'Suavizante', 'Cloro', 'Lavaloza', 'Papel Higiénico', 'Toalla de Papel', 'Jabón de Mano'],
};

export default function CategoryCards({ tabla, loading }) {
  // Para cada categoría, calcular cuál supermercado es más barato en promedio
  const catStats = useMemo(() => {
    if (!tabla.length) return {};
    const stats = {};
    const categorias = [...new Set(tabla.map(r => r.categoria).filter(Boolean))];

    for (const cat of categorias) {
      const rows = tabla.filter(r => r.categoria === cat);
      if (!rows.length) continue;

      // Promedio de precio mínimo por supermercado en esta categoría
      const promPorSuper = {};
      const cntPorSuper = {};

      for (const row of rows) {
        for (const [super_, precio] of Object.entries(row.precios)) {
          if (!precio || precio <= 0) continue;
          promPorSuper[super_] = (promPorSuper[super_] || 0) + precio;
          cntPorSuper[super_]  = (cntPorSuper[super_]  || 0) + 1;
        }
      }

      const promedios = Object.entries(promPorSuper).map(([s, total]) => ({
        supermercado: s,
        promedio: total / cntPorSuper[s],
      })).sort((a, b) => a.promedio - b.promedio);

      const gapPromedio = rows.reduce((acc, r) => acc + r.gap, 0) / rows.length;

      stats[cat] = {
        total: rows.length,
        ganador: promedios[0] || null,
        promedios,
        gapPromedio,
      };
    }
    return stats;
  }, [tabla]);

  if (loading) {
    return (
      <section id="categorias" className="catcards-section">
        <div className="container">
          <p className="section-label">Resumen por categoría</p>
          <h2 className="catcards-title">Por categoría</h2>
          <div className="catcards-grupos">
            {Array.from({length: 3}).map((_, i) => (
              <div key={i} className="catcards-grupo">
                <div className="skeleton" style={{ height: 24, width: 200, marginBottom: 16 }} />
                <div className="catcards-grid">
                  {Array.from({length: 3}).map((_, j) => (
                    <div key={j} className="skeleton" style={{ height: 120 }} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="categorias" className="catcards-section">
      <div className="container">
        <div className="catcards-header">
          <p className="section-label">Resumen por categoría</p>
          <h2 className="catcards-title">Compará por categoría</h2>
          <p className="catcards-subtitle">
            Cuál supermercado es más barato en promedio para cada grupo de productos
          </p>
        </div>

        <div className="catcards-grupos">
          {Object.entries(CAT_GRUPOS).map(([grupo, cats]) => (
            <div key={grupo} className="catcards-grupo">
              <h3 className="catcards-grupo-title">{grupo}</h3>
              <div className="catcards-grid">
                {cats.map((cat) => {
                  const s = catStats[cat];
                  const icon = CAT_ICONS[cat] || '🛒';
                  return (
                    <div key={cat} className="catcard glass-card">
                      <div className="catcard__icon">{icon}</div>
                      <div className="catcard__name">{cat}</div>
                      {s ? (
                        <>
                          <div className="catcard__count">{s.total} producto{s.total !== 1 ? 's' : ''}</div>
                          {s.ganador && (
                            <div className="catcard__winner">
                              <Award size={12} />
                              <span>Más barato en promedio:</span>
                              <strong>{s.ganador.supermercado}</strong>
                            </div>
                          )}
                          {s.ganador && (
                            <div className="catcard__avg price-num">
                              {formatPrecio(s.ganador.promedio)} prom.
                            </div>
                          )}
                          {s.gapPromedio > 0 && (
                            <div className="catcard__gap">
                              <TrendingDown size={11} />
                              Gap prom. {formatPrecio(s.gapPromedio)}
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="catcard__nodata">Sin datos aún</div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

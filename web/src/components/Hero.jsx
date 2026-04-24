import { TrendingDown, ChevronDown } from 'lucide-react';
import './Hero.css';

export default function Hero() {
  return (
    <section className="hero">
      {/* Glow de fondo */}
      <div className="hero-glow" aria-hidden />

      <div className="container hero-inner">
        <div className="hero-badge">
          <TrendingDown size={14} />
          Datos actualizados semanalmente desde GitHub Actions
        </div>

        <h1 className="hero-title">
          Compará precios en<br />
          <span className="hero-title--accent">supermercados chilenos</span>
        </h1>

        <p className="hero-desc">
          Encontrá dónde está más barato cada producto. Analizamos más de{' '}
          <strong>20 categorías</strong> en Jumbo, Lider, Santa Isabel, Unimarc, Alvi y Acuenta.
        </p>

        <div className="hero-actions">
          <a href="#ahorros" className="btn-primary hero-cta">
            <TrendingDown size={16} />
            Ver mayores ahorros
          </a>
          <a href="#tabla" className="btn-ghost">
            Ver todos los precios
          </a>
        </div>

        <div className="hero-stores">
          {['Jumbo', 'Lider', 'Santa Isabel', 'Unimarc', 'Alvi', 'Acuenta'].map(s => (
            <span key={s} className="hero-store-pill">{s}</span>
          ))}
        </div>
      </div>

      <a href="#ahorros" className="hero-scroll" aria-label="Ir a la sección de ahorros">
        <ChevronDown size={20} />
      </a>
    </section>
  );
}

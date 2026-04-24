import { ShoppingCart, TrendingDown, GitBranch } from 'lucide-react';
import './Header.css';

export default function Header() {
  return (
    <header className="header">
      <div className="container header-inner">
        <a href="#" className="header-logo">
          <div className="header-logo-icon">
            <ShoppingCart size={18} strokeWidth={2.5} />
          </div>
          <div className="header-logo-text">
            <span className="header-logo-name">Comparador</span>
            <span className="header-logo-sub">Supermercados Chile</span>
          </div>
        </a>

        <nav className="header-nav">
          <a href="#ahorros" className="header-nav-link">
            <TrendingDown size={14} />
            Mejores ahorros
          </a>
          <a href="#tabla" className="header-nav-link">
            Todos los precios
          </a>
          <a href="#categorias" className="header-nav-link">
            Por categoría
          </a>
          <a
            href="https://github.com/1bryanvalenzuela/Comparador-Supermercados-Chile"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost header-gh"
            aria-label="Ver código en GitHub"
          >
            <GitBranch size={16} />
            <span className="header-gh-label">GitHub</span>
          </a>
        </nav>
      </div>
    </header>
  );
}

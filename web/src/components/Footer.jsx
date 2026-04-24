import { GitBranch, ShoppingCart } from 'lucide-react';
import './Footer.css';

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div className="footer-brand">
          <div className="footer-logo">
            <ShoppingCart size={16} strokeWidth={2.5} />
          </div>
          <span className="footer-name">Comparador Supermercados Chile</span>
        </div>
        <p className="footer-desc">
          Datos obtenidos semanalmente mediante web scraping ético. Solo para uso informativo.
        </p>
        <div className="footer-links">
          <a
            href="https://github.com/1bryanvalenzuela/Comparador-Supermercados-Chile"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-link"
          >
            <GitBranch size={14} />
            Ver código fuente
          </a>
          <span className="footer-sep">·</span>
          <span className="footer-year">© {year}</span>
        </div>
      </div>
    </footer>
  );
}

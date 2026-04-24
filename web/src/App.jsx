import './index.css';
import { useProducts } from './hooks/useProducts';
import Header from './components/Header';
import Hero from './components/Hero';
import StatsBar from './components/StatsBar';
import GapCards from './components/GapCards';
import ProductTable from './components/ProductTable';
import CategoryCards from './components/CategoryCards';
import Footer from './components/Footer';
import './App.css';

function ErrorBanner({ message }) {
  return (
    <div className="error-banner">
      <div className="container">
        <strong>⚠️ No se pudieron cargar los datos:</strong> {message}
        <br />
        <small>
          Los datos se leen desde el CSV público de GitHub. Verificá tu conexión a internet.
        </small>
      </div>
    </div>
  );
}

export default function App() {
  const { loading, error, gaps, tabla, stats, categorias } = useProducts();

  return (
    <>
      <Header />
      {error && <ErrorBanner message={error} />}
      <main>
        <Hero />
        <StatsBar stats={stats} loading={loading} />
        <GapCards gaps={gaps} categorias={categorias} loading={loading} />
        <ProductTable tabla={tabla} categorias={categorias} loading={loading} />
        <CategoryCards tabla={tabla} loading={loading} />
      </main>
      <Footer />
    </>
  );
}

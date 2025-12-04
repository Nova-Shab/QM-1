import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Layout() {
  const { user, logout, canEdit, isAdmin } = useAuth();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <div className="app-layout">
      <header className="header">
        <div className="header-brand">
          <h1>Pharma DMS</h1>
          <span className="subtitle">Documentation Management System</span>
        </div>
        <div className="header-user">
          <span className="user-name">{user?.name}</span>
          <span className="user-role">{user?.role.replace('_', ' ').toUpperCase()}</span>
          <button onClick={logout} className="btn btn-sm btn-outline">Logout</button>
        </div>
      </header>

      <nav className="sidebar">
        <ul className="nav-list">
          <li className={isActive('/') && !isActive('/documents') && !isActive('/products') && !isActive('/search') ? 'active' : ''}>
            <Link to="/">Dashboard</Link>
          </li>
          <li className={isActive('/documents') ? 'active' : ''}>
            <Link to="/documents">Documents</Link>
          </li>
          <li className={isActive('/products') ? 'active' : ''}>
            <Link to="/products">Products</Link>
          </li>
          <li className={isActive('/search') ? 'active' : ''}>
            <Link to="/search">Search</Link>
          </li>
          {canEdit && (
            <li className="nav-divider">
              <span>Actions</span>
            </li>
          )}
          {canEdit && (
            <li>
              <Link to="/documents/new" className="btn btn-primary">+ New Document</Link>
            </li>
          )}
        </ul>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="footer">
        <p>Pharma DMS v1.0.0 - GxP Documentation Management System</p>
      </footer>
    </div>
  );
}

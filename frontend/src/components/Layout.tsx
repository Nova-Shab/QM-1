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
          <div className="logo">DP</div>
          <div>
            <h1>Dyckerhoff Pharma</h1>
          </div>
          <span className="subtitle">DMS</span>
        </div>
        <div className="header-user">
          <div className="user-info">
            <span className="user-name">{user?.name}</span>
            <span className="user-role">{user?.role.replace('_', ' ')}</span>
          </div>
          <button onClick={logout} className="logout-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/>
            </svg>
            Abmelden
          </button>
        </div>
      </header>

      <nav className="sidebar">
        <ul className="nav-list">
          <li className="nav-divider">
            <span>Navigation</span>
          </li>
          <li className={isActive('/') && !isActive('/documents') && !isActive('/products') && !isActive('/search') ? 'active' : ''}>
            <Link to="/">
              <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              Dashboard
            </Link>
          </li>
          <li className={isActive('/documents') ? 'active' : ''}>
            <Link to="/documents">
              <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              Dokumente
            </Link>
          </li>
          <li className={isActive('/products') ? 'active' : ''}>
            <Link to="/products">
              <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
              Produkte
            </Link>
          </li>
          <li className={isActive('/search') ? 'active' : ''}>
            <Link to="/search">
              <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              Suche
            </Link>
          </li>

          {canEdit && (
            <>
              <li className="nav-divider">
                <span>Aktionen</span>
              </li>
              <li>
                <Link to="/documents/new">
                  <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="12" y1="18" x2="12" y2="12"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                  </svg>
                  Neues Dokument
                </Link>
              </li>
            </>
          )}

          {isAdmin && (
            <>
              <li className="nav-divider">
                <span>Administration</span>
              </li>
              <li>
                <Link to="/admin/users">
                  <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                    <path d="M16 3.13a4 4 0 010 7.75"/>
                  </svg>
                  Benutzer
                </Link>
              </li>
              <li>
                <Link to="/admin/audit">
                  <svg className="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                  </svg>
                  Audit Log
                </Link>
              </li>
            </>
          )}
        </ul>

        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '16px',
          right: '16px',
          padding: '16px',
          background: 'linear-gradient(135deg, #F4FADC 0%, #E6FFFA 100%)',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <span className="gxp-badge">GxP Compliant</span>
          <p style={{ fontSize: '11px', color: '#4A5568', marginTop: '8px' }}>
            21 CFR Part 11
          </p>
        </div>
      </nav>

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="footer">
        <p>
          © 2024 <a href="https://www.dyckerhoff-pharma.de" target="_blank" rel="noopener noreferrer">Dyckerhoff Pharma GmbH & Co. KG</a> —
          Pharma DMS v1.0.0 — GxP Documentation Management System
        </p>
      </footer>
    </div>
  );
}

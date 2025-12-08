import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Anmeldung fehlgeschlagen. Bitte überprüfen Sie Ihre Zugangsdaten.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="logo-section">
          <div className="logo">DP</div>
        </div>

        <h1>Dyckerhoff Pharma</h1>
        <p className="subtitle">GxP Documentation Management System</p>

        {error && (
          <div className="login-error">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">E-Mail Adresse</label>
            <input
              id="email"
              type="email"
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@dyckerhoff-pharma.de"
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Passwort</label>
            <input
              id="password"
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Passwort eingeben"
              required
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="btn btn-primary btn-lg" disabled={isLoading}>
            {isLoading ? (
              <>
                <span className="spinner" style={{
                  width: '18px',
                  height: '18px',
                  border: '2px solid transparent',
                  borderTopColor: 'currentColor',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite',
                  display: 'inline-block'
                }}></span>
                Anmelden...
              </>
            ) : (
              'Anmelden'
            )}
          </button>
        </form>

        <div className="test-credentials">
          <h4>Test-Zugangsdaten</h4>
          <p>admin@pharma-dms.de / admin123</p>
          <p>author@pharma-dms.de / author123</p>
          <p>qa.approver@pharma-dms.de / approver123</p>
        </div>

        <div style={{
          marginTop: '24px',
          textAlign: 'center',
          fontSize: '11px',
          color: '#718096'
        }}>
          <span className="gxp-badge">GxP Compliant</span>
          <p style={{ marginTop: '12px' }}>
            © 2024 Dyckerhoff Pharma GmbH & Co. KG
          </p>
        </div>
      </div>
    </div>
  );
}

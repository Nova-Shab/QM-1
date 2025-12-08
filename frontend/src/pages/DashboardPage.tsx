import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { documentsApi, searchApi, productsApi } from '../services/api';
import type { Document, Product } from '../types';

export default function DashboardPage() {
  const { user, canReview, canEdit } = useAuth();
  const [stats, setStats] = useState({
    totalDocuments: 0,
    inReview: 0,
    reviewDue: 0,
    products: 0,
  });
  const [recentDocuments, setRecentDocuments] = useState<Document[]>([]);
  const [docsInReview, setDocsInReview] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);

      const [allDocs, inReviewDocs, reviewDueDocs, products] = await Promise.all([
        documentsApi.list({ page: 1, size: 5 }),
        searchApi.inReview(),
        searchApi.reviewDue(90),
        productsApi.list(),
      ]);

      setStats({
        totalDocuments: allDocs.total,
        inReview: inReviewDocs.total,
        reviewDue: reviewDueDocs.total,
        products: products.length,
      });

      setRecentDocuments(allDocs.items);
      setDocsInReview(inReviewDocs.items.slice(0, 5));
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusClass = (status: string) => `status-badge status-${status}`;

  const formatStatus = (status: string) => {
    const statusMap: { [key: string]: string } = {
      'draft': 'Entwurf',
      'in_review': 'In Prüfung',
      'approved': 'Genehmigt',
      'effective': 'Wirksam',
      'obsolete': 'Veraltet',
      'archived': 'Archiviert',
    };
    return statusMap[status] || status.replace('_', ' ');
  };

  if (isLoading) {
    return <div className="loading">Dashboard wird geladen...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Willkommen, {user?.name?.split(' ')[0]}</h1>
          <p className="breadcrumb">Dyckerhoff Pharma Dokumentenmanagementsystem</p>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="stat-card highlight">
          <h3>Dokumente Gesamt</h3>
          <div className="stat-value">{stats.totalDocuments}</div>
          <div className="stat-label">im System</div>
        </div>

        <div className="stat-card">
          <h3>In Prüfung</h3>
          <div className="stat-value" style={{ color: stats.inReview > 0 ? '#D69E2E' : undefined }}>
            {stats.inReview}
          </div>
          <div className="stat-label">warten auf Genehmigung</div>
        </div>

        <div className="stat-card">
          <h3>Review fällig (90 Tage)</h3>
          <div className="stat-value" style={{ color: stats.reviewDue > 0 ? '#E53E3E' : undefined }}>
            {stats.reviewDue}
          </div>
          <div className="stat-label">periodische Überprüfung</div>
        </div>

        <div className="stat-card">
          <h3>Produkte</h3>
          <div className="stat-value">{stats.products}</div>
          <div className="stat-label">im Produktkatalog</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: canReview ? '1fr 1fr' : '1fr', gap: '24px' }}>
        <div className="card">
          <div className="card-header">
            <h3>Aktuelle Dokumente</h3>
            <Link to="/documents" className="btn btn-sm btn-outline">Alle anzeigen</Link>
          </div>
          {recentDocuments.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <h3>Keine Dokumente</h3>
              <p>Es wurden noch keine Dokumente erstellt.</p>
              {canEdit && (
                <Link to="/documents/new" className="btn btn-primary" style={{ marginTop: '16px' }}>
                  Erstes Dokument erstellen
                </Link>
              )}
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Dokument-ID</th>
                    <th>Titel</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentDocuments.map((doc) => (
                    <tr key={doc.id}>
                      <td>
                        <Link to={`/documents/${doc.id}`}>
                          <strong>{doc.document_id}</strong>
                        </Link>
                      </td>
                      <td>{doc.title}</td>
                      <td>
                        <span className={getStatusClass(doc.status)}>
                          {formatStatus(doc.status)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {canReview && (
          <div className="card">
            <div className="card-header">
              <h3>Ausstehende Prüfungen</h3>
              <span className="status-badge status-in_review">{docsInReview.length}</span>
            </div>
            {docsInReview.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon" style={{ background: '#C6F6D5' }}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22543D" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
                <h3>Alles erledigt!</h3>
                <p>Keine Dokumente warten auf Ihre Prüfung.</p>
              </div>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Dokument-ID</th>
                      <th>Titel</th>
                      <th>Aktion</th>
                    </tr>
                  </thead>
                  <tbody>
                    {docsInReview.map((doc) => (
                      <tr key={doc.id}>
                        <td>
                          <strong>{doc.document_id}</strong>
                        </td>
                        <td>{doc.title}</td>
                        <td>
                          <Link to={`/documents/${doc.id}`} className="btn btn-sm btn-primary">
                            Prüfen
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h3>Schnellzugriff</h3>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {canEdit && (
            <Link to="/documents/new" className="btn btn-primary">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="12" y1="18" x2="12" y2="12"/>
                <line x1="9" y1="15" x2="15" y2="15"/>
              </svg>
              Neues Dokument
            </Link>
          )}
          <Link to="/search" className="btn btn-outline">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            Dokumente suchen
          </Link>
          <Link to="/products" className="btn btn-outline">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
            </svg>
            Produkte anzeigen
          </Link>
        </div>
      </div>

      <div style={{
        marginTop: '24px',
        padding: '20px',
        background: 'linear-gradient(135deg, #F4FADC 0%, #E6FFFA 100%)',
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <h4 style={{ margin: 0, color: '#2D3748' }}>Dyckerhoff Pharma GxP DMS</h4>
          <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#4A5568' }}>
            21 CFR Part 11 konform - EU GMP Annex 11 konform
          </p>
        </div>
        <span className="gxp-badge">GxP Compliant</span>
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { documentsApi, searchApi, productsApi } from '../services/api';
import type { Document, Product } from '../types';

export default function DashboardPage() {
  const { user, canReview } = useAuth();
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

  if (isLoading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>

      <div className="dashboard-grid">
        <div className="stat-card">
          <h3>Total Documents</h3>
          <div className="stat-value">{stats.totalDocuments}</div>
          <div className="stat-label">in the system</div>
        </div>

        <div className="stat-card">
          <h3>In Review</h3>
          <div className="stat-value" style={{ color: stats.inReview > 0 ? '#ca8a04' : undefined }}>
            {stats.inReview}
          </div>
          <div className="stat-label">awaiting approval</div>
        </div>

        <div className="stat-card">
          <h3>Review Due (90 days)</h3>
          <div className="stat-value" style={{ color: stats.reviewDue > 0 ? '#dc2626' : undefined }}>
            {stats.reviewDue}
          </div>
          <div className="stat-label">need periodic review</div>
        </div>

        <div className="stat-card">
          <h3>Products</h3>
          <div className="stat-value">{stats.products}</div>
          <div className="stat-label">in product catalog</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div className="card">
          <div className="card-header">
            <h3>Recent Documents</h3>
            <Link to="/documents" className="btn btn-sm btn-outline">View All</Link>
          </div>
          {recentDocuments.length === 0 ? (
            <div className="empty-state">
              <p>No documents yet.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Document ID</th>
                  <th>Title</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentDocuments.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <Link to={`/documents/${doc.id}`}>{doc.document_id}</Link>
                    </td>
                    <td>{doc.title}</td>
                    <td>
                      <span className={getStatusClass(doc.status)}>
                        {doc.status.replace('_', ' ')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {canReview && (
          <div className="card">
            <div className="card-header">
              <h3>Pending Review</h3>
            </div>
            {docsInReview.length === 0 ? (
              <div className="empty-state">
                <p>No documents pending review.</p>
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Document ID</th>
                    <th>Title</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {docsInReview.map((doc) => (
                    <tr key={doc.id}>
                      <td>{doc.document_id}</td>
                      <td>{doc.title}</td>
                      <td>
                        <Link to={`/documents/${doc.id}`} className="btn btn-sm btn-primary">
                          Review
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h3>Quick Actions</h3>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/documents/new" className="btn btn-primary">Create New Document</Link>
          <Link to="/search" className="btn btn-outline">Search Documents</Link>
          <Link to="/products" className="btn btn-outline">View Products</Link>
        </div>
      </div>
    </div>
  );
}

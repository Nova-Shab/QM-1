import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { documentsApi, versionsApi, approvalsApi, auditApi } from '../services/api';
import type { Document, DocumentVersion, AuditLog, ApprovalDecision } from '../types';

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, canEdit, canReview, canApprove } = useAuth();

  const [document, setDocument] = useState<Document | null>(null);
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('details');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modal states
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [showNewVersionModal, setShowNewVersionModal] = useState(false);
  const [approvalComment, setApprovalComment] = useState('');
  const [newVersionReason, setNewVersionReason] = useState('');
  const [isMajorVersion, setIsMajorVersion] = useState(false);

  useEffect(() => {
    if (id) {
      loadDocument();
    }
  }, [id]);

  const loadDocument = async () => {
    try {
      setIsLoading(true);
      const docId = parseInt(id!);

      const [docData, versionsData, auditData] = await Promise.all([
        documentsApi.get(docId),
        versionsApi.listByDocument(docId),
        auditApi.getEntityTrail('Document', docId),
      ]);

      setDocument(docData);
      setVersions(versionsData);
      setAuditLogs(auditData);
    } catch (error) {
      console.error('Error loading document:', error);
      setError('Error loading document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitForReview = async () => {
    if (!document) return;
    try {
      await documentsApi.submitForReview(document.id);
      setSuccess('Document submitted for review');
      loadDocument();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error submitting for review');
    }
  };

  const handleApproval = async (decision: ApprovalDecision) => {
    if (!versions.length) return;
    const latestVersion = versions[0];

    try {
      if (canApprove) {
        await approvalsApi.approve(latestVersion.id, {
          decision,
          comment: approvalComment || null,
        });
      } else {
        await approvalsApi.review(latestVersion.id, {
          decision,
          comment: approvalComment || null,
        });
      }
      setSuccess(`Document ${decision}`);
      setShowApprovalModal(false);
      setApprovalComment('');
      loadDocument();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error processing approval');
    }
  };

  const handleCreateNewVersion = async () => {
    if (!document) return;
    try {
      await versionsApi.createNewVersion(document.id, {
        is_major: isMajorVersion,
        change_reason: newVersionReason,
        change_summary: null,
        related_change_control_id: null,
        related_deviation_id: null,
        related_capa_id: null,
      });
      setSuccess('New version created');
      setShowNewVersionModal(false);
      setNewVersionReason('');
      setIsMajorVersion(false);
      loadDocument();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error creating new version');
    }
  };

  const getStatusClass = (status: string) => `status-badge status-${status}`;

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return <div className="loading">Loading document...</div>;
  }

  if (!document) {
    return (
      <div className="empty-state">
        <h3>Document not found</h3>
        <button onClick={() => navigate('/documents')} className="btn btn-primary">
          Back to Documents
        </button>
      </div>
    );
  }

  const latestVersion = versions.length > 0 ? versions[0] : null;
  const canSubmitForReview = document.status === 'draft' && canEdit;
  const canProcessApproval = document.status === 'in_review' && (canReview || canApprove);
  const canCreateNewVersion =
    (document.status === 'effective' || document.status === 'approved') && canEdit;

  return (
    <div>
      {error && (
        <div className="alert alert-error">
          {error}
          <button onClick={() => setError('')} style={{ float: 'right', border: 'none', background: 'none', cursor: 'pointer' }}>×</button>
        </div>
      )}
      {success && (
        <div className="alert alert-success">
          {success}
          <button onClick={() => setSuccess('')} style={{ float: 'right', border: 'none', background: 'none', cursor: 'pointer' }}>×</button>
        </div>
      )}

      <div className="document-header">
        <div>
          <h1>{document.document_id}</h1>
          <p style={{ fontSize: '18px', color: '#374151', marginBottom: '12px' }}>{document.title}</p>
          <div className="document-meta">
            <span>
              <strong>Status:</strong>{' '}
              <span className={getStatusClass(document.status)}>
                {document.status.replace('_', ' ')}
              </span>
            </span>
            <span>
              <strong>Type:</strong> {document.document_type?.code || '-'}
            </span>
            <span>
              <strong>Department:</strong> {document.department}
            </span>
            <span>
              <strong>Language:</strong> {document.language}
            </span>
            {latestVersion && (
              <span>
                <strong>Version:</strong> {latestVersion.version_label}
              </span>
            )}
          </div>
        </div>

        <div className="document-actions">
          {canSubmitForReview && (
            <button onClick={handleSubmitForReview} className="btn btn-primary">
              Submit for Review
            </button>
          )}
          {canProcessApproval && (
            <button onClick={() => setShowApprovalModal(true)} className="btn btn-success">
              Review / Approve
            </button>
          )}
          {canCreateNewVersion && (
            <button onClick={() => setShowNewVersionModal(true)} className="btn btn-outline">
              Create New Version
            </button>
          )}
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
        <button
          className={`tab ${activeTab === 'versions' ? 'active' : ''}`}
          onClick={() => setActiveTab('versions')}
        >
          Versions ({versions.length})
        </button>
        <button
          className={`tab ${activeTab === 'products' ? 'active' : ''}`}
          onClick={() => setActiveTab('products')}
        >
          Products ({document.products?.length || 0})
        </button>
        <button
          className={`tab ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          Audit Trail
        </button>
      </div>

      {activeTab === 'details' && (
        <div className="card">
          <div className="card-header">
            <h3>Document Details</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            <div>
              <p><strong>Document ID:</strong> {document.document_id}</p>
              <p><strong>Title:</strong> {document.title}</p>
              <p><strong>Description:</strong> {document.description || '-'}</p>
              <p><strong>Document Type:</strong> {document.document_type?.name || '-'}</p>
              <p><strong>Department:</strong> {document.department}</p>
            </div>
            <div>
              <p><strong>Language:</strong> {document.language}</p>
              <p><strong>Status:</strong> {document.status}</p>
              <p><strong>Effective Date:</strong> {formatDate(document.effective_date)}</p>
              <p><strong>Next Review Date:</strong> {formatDate(document.next_review_date)}</p>
              <p><strong>Created:</strong> {formatDate(document.created_at)}</p>
              <p><strong>Last Updated:</strong> {formatDate(document.updated_at)}</p>
            </div>
          </div>

          {latestVersion && latestVersion.approvals && latestVersion.approvals.length > 0 && (
            <div style={{ marginTop: '24px' }}>
              <h4 style={{ marginBottom: '12px' }}>Approvals</h4>
              <ul className="approval-list">
                {latestVersion.approvals.map((approval, idx) => (
                  <li key={idx} className="approval-item">
                    <div className={`approval-icon ${approval.decision}`}>
                      {approval.decision === 'approved' ? '✓' : approval.decision === 'rejected' ? '×' : '?'}
                    </div>
                    <div>
                      <strong>{approval.approver_name}</strong> ({approval.approval_role})
                      <br />
                      <span style={{ fontSize: '13px', color: '#6b7280' }}>
                        {approval.decision} - {formatDate(approval.decided_at)}
                      </span>
                      {approval.comment && (
                        <p style={{ fontSize: '13px', marginTop: '4px' }}>"{approval.comment}"</p>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {activeTab === 'versions' && (
        <div className="card">
          <div className="card-header">
            <h3>Version History</h3>
          </div>
          <ul className="version-list">
            {versions.map((version) => (
              <li key={version.id} className="version-item">
                <span className="version-badge">V{version.version_label}</span>
                <div className="version-info">
                  <h4>
                    <span className={getStatusClass(version.status)}>
                      {version.status.replace('_', ' ')}
                    </span>
                  </h4>
                  <p>
                    Created: {formatDate(version.created_at)}
                    {version.approved_at && ` | Approved: ${formatDate(version.approved_at)}`}
                  </p>
                  {version.change_reason && (
                    <p><strong>Change Reason:</strong> {version.change_reason}</p>
                  )}
                  {version.change_summary && (
                    <p><strong>Summary:</strong> {version.change_summary}</p>
                  )}
                  {version.file_path_full && (
                    <p><strong>File Path:</strong> <code>{version.file_path_full}</code></p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {activeTab === 'products' && (
        <div className="card">
          <div className="card-header">
            <h3>Linked Products</h3>
          </div>
          {document.products && document.products.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>Dosage Form</th>
                  <th>Strength</th>
                  <th>Family</th>
                </tr>
              </thead>
              <tbody>
                {document.products.map((product) => (
                  <tr key={product.id}>
                    <td>{product.short_name}</td>
                    <td>{product.dosage_form}</td>
                    <td>{product.strength || '-'}</td>
                    <td>{product.product_family || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <p>No products linked to this document.</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="card">
          <div className="card-header">
            <h3>Audit Trail</h3>
          </div>
          {auditLogs.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Action</th>
                  <th>User</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td>{formatDate(log.timestamp)}</td>
                    <td>
                      <span className="status-badge status-draft">{log.action}</span>
                    </td>
                    <td>{log.performed_by_name || '-'}</td>
                    <td>{log.description || JSON.stringify(log.details)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <p>No audit logs available.</p>
            </div>
          )}
        </div>
      )}

      {/* Approval Modal */}
      {showApprovalModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Review / Approve Document</h2>
            <p>Document: <strong>{document.document_id}</strong></p>
            <p>Version: <strong>{latestVersion?.version_label}</strong></p>

            <div className="form-group" style={{ marginTop: '16px' }}>
              <label>Comment (optional)</label>
              <textarea
                className="form-control"
                value={approvalComment}
                onChange={(e) => setApprovalComment(e.target.value)}
                placeholder="Enter your comments..."
              />
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowApprovalModal(false)} className="btn btn-outline">
                Cancel
              </button>
              <button onClick={() => handleApproval('rejected')} className="btn btn-danger">
                Reject
              </button>
              <button onClick={() => handleApproval('approved')} className="btn btn-success">
                {canApprove ? 'Approve' : 'Review & Recommend'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Version Modal */}
      {showNewVersionModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Create New Version</h2>
            <p>
              Current Version: <strong>{latestVersion?.version_label}</strong>
            </p>

            <div className="form-group" style={{ marginTop: '16px' }}>
              <label>
                <input
                  type="checkbox"
                  checked={isMajorVersion}
                  onChange={(e) => setIsMajorVersion(e.target.checked)}
                />{' '}
                Major version change (e.g., 1.0 → 2.0)
              </label>
            </div>

            <div className="form-group">
              <label>Reason for Change *</label>
              <textarea
                className="form-control"
                value={newVersionReason}
                onChange={(e) => setNewVersionReason(e.target.value)}
                placeholder="Describe the reason for creating a new version..."
                required
              />
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowNewVersionModal(false)} className="btn btn-outline">
                Cancel
              </button>
              <button
                onClick={handleCreateNewVersion}
                className="btn btn-primary"
                disabled={!newVersionReason.trim()}
              >
                Create Version
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

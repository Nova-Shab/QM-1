import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { documentsApi, documentTypesApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { Document, DocumentType, DocumentStatus } from '../types';

export default function DocumentsPage() {
  const { canEdit } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [departmentFilter, setDepartmentFilter] = useState('');

  useEffect(() => {
    loadDocumentTypes();
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [page, searchTerm, statusFilter, typeFilter, departmentFilter]);

  const loadDocumentTypes = async () => {
    try {
      const data = await documentTypesApi.list();
      setDocumentTypes(data);
    } catch (error) {
      console.error('Error loading document types:', error);
    }
  };

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const params: {
        page: number;
        size: number;
        search?: string;
        status?: string;
        document_type_id?: number;
        department?: string;
      } = { page, size: 20 };

      if (searchTerm) params.search = searchTerm;
      if (statusFilter) params.status = statusFilter;
      if (typeFilter) params.document_type_id = parseInt(typeFilter);
      if (departmentFilter) params.department = departmentFilter;

      const data = await documentsApi.list(params);
      setDocuments(data.items);
      setTotalPages(data.pages);
      setTotal(data.total);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusClass = (status: string) => `status-badge status-${status}`;

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('de-DE');
  };

  // Get unique departments from documents
  const departments = [...new Set(documents.map((d) => d.department))];

  return (
    <div>
      <div className="page-header">
        <h1>Documents / Dokumente</h1>
        {canEdit && (
          <Link to="/documents/new" className="btn btn-primary">
            + New Document
          </Link>
        )}
      </div>

      <div className="filter-bar">
        <input
          type="text"
          className="form-control"
          placeholder="Search by ID, title, or description..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setPage(1);
          }}
        />
        <select
          className="form-control"
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="in_review">In Review</option>
          <option value="approved">Approved</option>
          <option value="effective">Effective</option>
          <option value="obsolete">Obsolete</option>
        </select>
        <select
          className="form-control"
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Document Types</option>
          {documentTypes.map((dt) => (
            <option key={dt.id} value={dt.id}>
              {dt.code} - {dt.name}
            </option>
          ))}
        </select>
        <select
          className="form-control"
          value={departmentFilter}
          onChange={(e) => {
            setDepartmentFilter(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Departments</option>
          <option value="QA">QA</option>
          <option value="Production">Production</option>
          <option value="Regulatory">Regulatory</option>
          <option value="IT">IT</option>
        </select>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="loading">Loading documents...</div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <h3>No documents found</h3>
            <p>Try adjusting your search or filters, or create a new document.</p>
            {canEdit && (
              <Link to="/documents/new" className="btn btn-primary" style={{ marginTop: '16px' }}>
                Create Document
              </Link>
            )}
          </div>
        ) : (
          <>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Document ID</th>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Department</th>
                    <th>Status</th>
                    <th>Version</th>
                    <th>Updated</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id}>
                      <td>
                        <Link to={`/documents/${doc.id}`}>
                          <strong>{doc.document_id}</strong>
                        </Link>
                      </td>
                      <td>{doc.title}</td>
                      <td>{doc.document_type?.code || '-'}</td>
                      <td>{doc.department}</td>
                      <td>
                        <span className={getStatusClass(doc.status)}>
                          {doc.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>
                        {doc.versions && doc.versions.length > 0
                          ? `${doc.versions[0].version_major}.${doc.versions[0].version_minor}`
                          : '-'}
                      </td>
                      <td>{formatDate(doc.updated_at)}</td>
                      <td>
                        <Link to={`/documents/${doc.id}`} className="btn btn-sm btn-outline">
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <button
                className="btn btn-sm btn-outline"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages} ({total} total)
              </span>
              <button
                className="btn btn-sm btn-outline"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

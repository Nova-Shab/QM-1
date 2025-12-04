import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { searchApi, productsApi } from '../services/api';
import type { Document, Product } from '../types';

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Search filters from URL params
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [status, setStatus] = useState(searchParams.get('status') || '');
  const [documentType, setDocumentType] = useState(searchParams.get('type') || '');
  const [department, setDepartment] = useState(searchParams.get('department') || '');
  const [productId, setProductId] = useState(searchParams.get('product') || '');

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    performSearch();
  }, [page]);

  const loadProducts = async () => {
    try {
      const data = await productsApi.list();
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    }
  };

  const performSearch = async () => {
    try {
      setIsLoading(true);

      const params: {
        q?: string;
        status?: string;
        document_type?: string;
        department?: string;
        product?: string;
        page: number;
        size: number;
      } = { page, size: 20 };

      if (query) params.q = query;
      if (status) params.status = status;
      if (documentType) params.document_type = documentType;
      if (department) params.department = department;
      if (productId) params.product = productId;

      const data = await searchApi.documents(params);
      setDocuments(data.items);
      setTotal(data.total);
      setTotalPages(data.pages);

      // Update URL params
      const newParams = new URLSearchParams();
      if (query) newParams.set('q', query);
      if (status) newParams.set('status', status);
      if (documentType) newParams.set('type', documentType);
      if (department) newParams.set('department', department);
      if (productId) newParams.set('product', productId);
      setSearchParams(newParams);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    performSearch();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getStatusClass = (status: string) => `status-badge status-${status}`;

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('de-DE');
  };

  return (
    <div>
      <div className="page-header">
        <h1>Search Documents</h1>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Search Filters</h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <div className="form-group">
            <label>Search Query</label>
            <input
              type="text"
              className="form-control"
              placeholder="Search by ID, title, description..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
            />
          </div>

          <div className="form-group">
            <label>Status</label>
            <select
              className="form-control"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="in_review">In Review</option>
              <option value="approved">Approved</option>
              <option value="effective">Effective</option>
              <option value="obsolete">Obsolete</option>
            </select>
          </div>

          <div className="form-group">
            <label>Document Type</label>
            <select
              className="form-control"
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
            >
              <option value="">All Types</option>
              <option value="SOP">SOP</option>
              <option value="WI">Work Instruction</option>
              <option value="FI">Fachinformation</option>
              <option value="GI">Gebrauchsinformation</option>
              <option value="SPEC">Specification</option>
              <option value="MBR">Master Batch Record</option>
              <option value="VAL">Validation</option>
            </select>
          </div>

          <div className="form-group">
            <label>Department</label>
            <select
              className="form-control"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
            >
              <option value="">All Departments</option>
              <option value="QA">QA</option>
              <option value="Production">Production</option>
              <option value="Regulatory">Regulatory</option>
              <option value="IT">IT</option>
            </select>
          </div>

          <div className="form-group">
            <label>Product</label>
            <select
              className="form-control"
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
            >
              <option value="">All Products</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.short_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button className="btn btn-primary" onClick={handleSearch} style={{ width: '100%' }}>
              Search
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Results ({total})</h3>
        </div>

        {isLoading ? (
          <div className="loading">Searching...</div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <h3>No documents found</h3>
            <p>Try adjusting your search filters.</p>
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
                    <th>Products</th>
                    <th>Updated</th>
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
                        {doc.products && doc.products.length > 0
                          ? doc.products.map((p) => p.short_name).join(', ')
                          : '-'}
                      </td>
                      <td>{formatDate(doc.updated_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="pagination">
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Previous
                </button>
                <span className="page-info">
                  Page {page} of {totalPages}
                </span>
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <div className="card" style={{ marginTop: '16px' }}>
        <div className="card-header">
          <h3>Quick Reports</h3>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            className="btn btn-outline"
            onClick={async () => {
              setStatus('in_review');
              setQuery('');
              setDocumentType('');
              setDepartment('');
              setProductId('');
              setPage(1);
              const data = await searchApi.inReview();
              setDocuments(data.items);
              setTotal(data.total);
              setTotalPages(1);
            }}
          >
            Documents In Review
          </button>
          <button
            className="btn btn-outline"
            onClick={async () => {
              const data = await searchApi.reviewDue(90);
              setDocuments(data.items);
              setTotal(data.total);
              setTotalPages(1);
              setStatus('');
              setQuery('');
            }}
          >
            Review Due (90 days)
          </button>
        </div>
      </div>
    </div>
  );
}

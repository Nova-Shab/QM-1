import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentsApi, documentTypesApi, productsApi, templatesApi } from '../services/api';
import type { DocumentType, Product, Template, DocumentWizardRequest } from '../types';

export default function DocumentWizardPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Data
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);

  // Form data
  const [formData, setFormData] = useState<DocumentWizardRequest>({
    document_type_id: 0,
    product_ids: [],
    department: '',
    language: 'DE',
    title: '',
    description: null,
    template_id: null,
    initial_content: null,
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (formData.document_type_id) {
      loadTemplates();
    }
  }, [formData.document_type_id]);

  const loadInitialData = async () => {
    try {
      const [typesData, productsData] = await Promise.all([
        documentTypesApi.list(),
        productsApi.list(),
      ]);
      setDocumentTypes(typesData);
      setProducts(productsData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const templatesData = await templatesApi.list({
        document_type_id: formData.document_type_id,
        active_only: true,
      });
      setTemplates(templatesData);
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setIsLoading(true);
      setError('');
      const document = await documentsApi.createWithWizard(formData);
      navigate(`/documents/${document.id}`);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error creating document');
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = () => {
    if (!formData.document_type_id) {
      setError('Please select a document type');
      return false;
    }
    if (!formData.department) {
      setError('Please select a department');
      return false;
    }
    if (!formData.title.trim()) {
      setError('Please enter a document title');
      return false;
    }
    return true;
  };

  const handleProductToggle = (productId: number) => {
    const currentIds = formData.product_ids || [];
    if (currentIds.includes(productId)) {
      setFormData({
        ...formData,
        product_ids: currentIds.filter((id) => id !== productId),
      });
    } else {
      setFormData({
        ...formData,
        product_ids: [...currentIds, productId],
      });
    }
  };

  const selectedDocType = documentTypes.find((dt) => dt.id === formData.document_type_id);

  return (
    <div>
      <div className="page-header">
        <h1>Create New Document</h1>
      </div>

      <div className="wizard-steps">
        <div className={`wizard-step ${step >= 1 ? (step > 1 ? 'completed' : 'active') : ''}`}>
          <div className="step-number">{step > 1 ? '✓' : '1'}</div>
          <div>Document Type</div>
        </div>
        <div className={`wizard-step ${step >= 2 ? (step > 2 ? 'completed' : 'active') : ''}`}>
          <div className="step-number">{step > 2 ? '✓' : '2'}</div>
          <div>Details</div>
        </div>
        <div className={`wizard-step ${step >= 3 ? (step > 3 ? 'completed' : 'active') : ''}`}>
          <div className="step-number">{step > 3 ? '✓' : '3'}</div>
          <div>Products</div>
        </div>
        <div className={`wizard-step ${step === 4 ? 'active' : ''}`}>
          <div className="step-number">4</div>
          <div>Review</div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
          <button
            onClick={() => setError('')}
            style={{ float: 'right', border: 'none', background: 'none', cursor: 'pointer' }}
          >
            ×
          </button>
        </div>
      )}

      <div className="card">
        {step === 1 && (
          <div>
            <div className="card-header">
              <h3>Step 1: Select Document Type</h3>
            </div>

            <div className="form-group">
              <label>Document Type *</label>
              <select
                className="form-control"
                value={formData.document_type_id}
                onChange={(e) =>
                  setFormData({ ...formData, document_type_id: parseInt(e.target.value) || 0 })
                }
              >
                <option value="">Select a document type...</option>
                {documentTypes.map((dt) => (
                  <option key={dt.id} value={dt.id}>
                    {dt.code} - {dt.name}
                    {dt.name_de ? ` (${dt.name_de})` : ''}
                  </option>
                ))}
              </select>
            </div>

            {selectedDocType && (
              <div className="alert alert-info">
                <strong>{selectedDocType.name}</strong>
                <br />
                {selectedDocType.description}
                <br />
                <small>
                  GxP Relevant: {selectedDocType.gxp_relevant ? 'Yes' : 'No'} | QP Approval
                  Required: {selectedDocType.requires_qp_approval ? 'Yes' : 'No'}
                </small>
              </div>
            )}

            {templates.length > 0 && (
              <div className="form-group">
                <label>Template (optional)</label>
                <select
                  className="form-control"
                  value={formData.template_id || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      template_id: e.target.value ? parseInt(e.target.value) : null,
                    })
                  }
                >
                  <option value="">No template</option>
                  {templates.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} ({t.language})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div style={{ marginTop: '24px', textAlign: 'right' }}>
              <button
                className="btn btn-primary"
                onClick={() => setStep(2)}
                disabled={!formData.document_type_id}
              >
                Next: Document Details
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <div className="card-header">
              <h3>Step 2: Document Details</h3>
            </div>

            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                className="form-control"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter document title..."
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                className="form-control"
                value={formData.description || ''}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value || null })
                }
                placeholder="Enter a brief description..."
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="form-group">
                <label>Department *</label>
                <select
                  className="form-control"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                >
                  <option value="">Select department...</option>
                  <option value="QA">QA (Quality Assurance)</option>
                  <option value="Production">Production</option>
                  <option value="Regulatory">Regulatory Affairs</option>
                  <option value="IT">IT</option>
                  <option value="Logistics">Logistics</option>
                </select>
              </div>

              <div className="form-group">
                <label>Language *</label>
                <select
                  className="form-control"
                  value={formData.language}
                  onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                >
                  <option value="DE">German (DE)</option>
                  <option value="EN">English (EN)</option>
                </select>
              </div>
            </div>

            <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'space-between' }}>
              <button className="btn btn-outline" onClick={() => setStep(1)}>
                Back
              </button>
              <button
                className="btn btn-primary"
                onClick={() => setStep(3)}
                disabled={!formData.title.trim() || !formData.department}
              >
                Next: Link Products
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <div className="card-header">
              <h3>Step 3: Link Products (Optional)</h3>
            </div>

            <p style={{ marginBottom: '16px', color: '#6b7280' }}>
              Select products that this document relates to. The first selected product will be
              marked as the primary product.
            </p>

            <div className="multiselect">
              {products.map((product) => (
                <label key={product.id} className="multiselect-option">
                  <input
                    type="checkbox"
                    checked={formData.product_ids?.includes(product.id) || false}
                    onChange={() => handleProductToggle(product.id)}
                  />
                  <span>
                    <strong>{product.short_name}</strong>
                    {product.strength && ` - ${product.strength}`}
                    <br />
                    <small style={{ color: '#6b7280' }}>{product.product_family}</small>
                  </span>
                </label>
              ))}
            </div>

            <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'space-between' }}>
              <button className="btn btn-outline" onClick={() => setStep(2)}>
                Back
              </button>
              <button className="btn btn-primary" onClick={() => setStep(4)}>
                Next: Review
              </button>
            </div>
          </div>
        )}

        {step === 4 && (
          <div>
            <div className="card-header">
              <h3>Step 4: Review & Create</h3>
            </div>

            <div className="alert alert-info" style={{ marginBottom: '24px' }}>
              Please review the document details before creating.
            </div>

            <table>
              <tbody>
                <tr>
                  <td><strong>Document Type</strong></td>
                  <td>{selectedDocType?.name} ({selectedDocType?.code})</td>
                </tr>
                <tr>
                  <td><strong>Title</strong></td>
                  <td>{formData.title}</td>
                </tr>
                <tr>
                  <td><strong>Description</strong></td>
                  <td>{formData.description || '-'}</td>
                </tr>
                <tr>
                  <td><strong>Department</strong></td>
                  <td>{formData.department}</td>
                </tr>
                <tr>
                  <td><strong>Language</strong></td>
                  <td>{formData.language}</td>
                </tr>
                <tr>
                  <td><strong>Linked Products</strong></td>
                  <td>
                    {formData.product_ids && formData.product_ids.length > 0
                      ? products
                          .filter((p) => formData.product_ids?.includes(p.id))
                          .map((p) => p.short_name)
                          .join(', ')
                      : 'None'}
                  </td>
                </tr>
                <tr>
                  <td><strong>Template</strong></td>
                  <td>
                    {formData.template_id
                      ? templates.find((t) => t.id === formData.template_id)?.name || '-'
                      : 'None'}
                  </td>
                </tr>
              </tbody>
            </table>

            <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'space-between' }}>
              <button className="btn btn-outline" onClick={() => setStep(3)}>
                Back
              </button>
              <button className="btn btn-primary" onClick={handleSubmit} disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Create Document'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

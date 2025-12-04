import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productsApi, searchApi } from '../services/api';
import type { Product, DocumentListResponse } from '../types';

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [familyFilter, setFamilyFilter] = useState('');

  useEffect(() => {
    loadProducts();
  }, [searchTerm, familyFilter]);

  const loadProducts = async () => {
    try {
      setIsLoading(true);
      const params: { search?: string; product_family?: string } = {};
      if (searchTerm) params.search = searchTerm;
      if (familyFilter) params.product_family = familyFilter;

      const data = await productsApi.list(params);
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDosageForm = (form: string) => {
    const forms: Record<string, string> = {
      drops: 'Tropfen',
      injection_solution: 'Injektionslösung',
      tablet: 'Tablette',
      ampoule: 'Ampulle',
      oral_solution: 'Lösung',
      cream: 'Creme',
      extract: 'Extrakt',
    };
    return forms[form] || form;
  };

  const formatStatus = (status: string) => {
    const statuses: Record<string, string> = {
      in_development: 'In Entwicklung',
      approved: 'Zugelassen',
      marketed: 'Im Markt',
      discontinued: 'Eingestellt',
    };
    return statuses[status] || status;
  };

  // Get unique product families
  const productFamilies = [...new Set(products.map((p) => p.product_family).filter(Boolean))];

  return (
    <div>
      <div className="page-header">
        <h1>Products / Produkte</h1>
      </div>

      <div className="filter-bar">
        <input
          type="text"
          className="form-control"
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <select
          className="form-control"
          value={familyFilter}
          onChange={(e) => setFamilyFilter(e.target.value)}
        >
          <option value="">All Product Families</option>
          {productFamilies.map((family) => (
            <option key={family} value={family!}>
              {family}
            </option>
          ))}
        </select>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="loading">Loading products...</div>
        ) : products.length === 0 ? (
          <div className="empty-state">
            <h3>No products found</h3>
            <p>Try adjusting your search or filters.</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>Short Name</th>
                  <th>Dosage Form</th>
                  <th>Strength</th>
                  <th>Family</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <strong>{product.name}</strong>
                    </td>
                    <td>{product.short_name}</td>
                    <td>{formatDosageForm(product.dosage_form)}</td>
                    <td>{product.strength || '-'}</td>
                    <td>{product.product_family || '-'}</td>
                    <td>
                      <span
                        className={`status-badge status-${
                          product.market_status === 'marketed'
                            ? 'effective'
                            : product.market_status === 'discontinued'
                            ? 'obsolete'
                            : 'draft'
                        }`}
                      >
                        {formatStatus(product.market_status)}
                      </span>
                    </td>
                    <td>
                      <Link
                        to={`/search?product=${product.id}`}
                        className="btn btn-sm btn-outline"
                      >
                        View Documents
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '16px' }}>
        <div className="card-header">
          <h3>Product Statistics</h3>
        </div>
        <div style={{ display: 'flex', gap: '32px' }}>
          <div>
            <strong>Total Products:</strong> {products.length}
          </div>
          <div>
            <strong>Marketed:</strong>{' '}
            {products.filter((p) => p.market_status === 'marketed').length}
          </div>
          <div>
            <strong>In Development:</strong>{' '}
            {products.filter((p) => p.market_status === 'in_development').length}
          </div>
        </div>
      </div>
    </div>
  );
}

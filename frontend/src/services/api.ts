import axios from 'axios';
import type {
  AuthResponse,
  LoginCredentials,
  User,
  Product,
  DocumentType,
  Document,
  DocumentListResponse,
  DocumentVersion,
  Approval,
  Template,
  AuditLog,
  DocumentWizardRequest,
  NewVersionRequest,
  ApprovalDecisionRequest,
} from '../types';

const API_BASE = '/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  console.log('API Request:', config.url, 'Token exists:', !!token);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors - don't auto-redirect, let components handle it
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log the error for debugging
    console.error('API Error:', error.response?.status, error.config?.url);
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login/json', credentials);
    return response.data;
  },

  register: async (data: { email: string; name: string; password: string; role?: string; department?: string }): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Products API
export const productsApi = {
  list: async (params?: { search?: string; market_status?: string; product_family?: string }): Promise<Product[]> => {
    const response = await api.get<Product[]>('/products', { params });
    return response.data;
  },

  get: async (id: number): Promise<Product> => {
    const response = await api.get<Product>(`/products/${id}`);
    return response.data;
  },

  create: async (data: Partial<Product>): Promise<Product> => {
    const response = await api.post<Product>('/products', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Product>): Promise<Product> => {
    const response = await api.put<Product>(`/products/${id}`, data);
    return response.data;
  },
};

// Document Types API
export const documentTypesApi = {
  list: async (): Promise<DocumentType[]> => {
    const response = await api.get<DocumentType[]>('/document-types');
    return response.data;
  },

  get: async (id: number): Promise<DocumentType> => {
    const response = await api.get<DocumentType>(`/document-types/${id}`);
    return response.data;
  },
};

// Documents API
export const documentsApi = {
  list: async (params?: {
    page?: number;
    size?: number;
    search?: string;
    status?: string;
    document_type_id?: number;
    department?: string;
    product_id?: number;
    owner_id?: number;
    review_due_days?: number;
  }): Promise<DocumentListResponse> => {
    const response = await api.get<DocumentListResponse>('/documents', { params });
    return response.data;
  },

  get: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${id}`);
    return response.data;
  },

  createWithWizard: async (data: DocumentWizardRequest): Promise<Document> => {
    const response = await api.post<Document>('/documents/wizard', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Document>): Promise<Document> => {
    const response = await api.put<Document>(`/documents/${id}`, data);
    return response.data;
  },

  submitForReview: async (id: number): Promise<Document> => {
    const response = await api.post<Document>(`/documents/${id}/submit-for-review`);
    return response.data;
  },
};

// Document Versions API
export const versionsApi = {
  listByDocument: async (documentId: number): Promise<DocumentVersion[]> => {
    const response = await api.get<DocumentVersion[]>(`/versions/document/${documentId}`);
    return response.data;
  },

  get: async (id: number): Promise<DocumentVersion> => {
    const response = await api.get<DocumentVersion>(`/versions/${id}`);
    return response.data;
  },

  createNewVersion: async (documentId: number, data: NewVersionRequest): Promise<DocumentVersion> => {
    const response = await api.post<DocumentVersion>(`/versions/document/${documentId}/new-version`, data);
    return response.data;
  },

  update: async (id: number, data: Partial<DocumentVersion>): Promise<DocumentVersion> => {
    const response = await api.put<DocumentVersion>(`/versions/${id}`, data);
    return response.data;
  },
};

// Approvals API
export const approvalsApi = {
  listByVersion: async (versionId: number): Promise<Approval[]> => {
    const response = await api.get<Approval[]>(`/approvals/version/${versionId}`);
    return response.data;
  },

  review: async (versionId: number, data: ApprovalDecisionRequest): Promise<Approval> => {
    const response = await api.post<Approval>(`/approvals/version/${versionId}/review`, data);
    return response.data;
  },

  approve: async (versionId: number, data: ApprovalDecisionRequest): Promise<Approval> => {
    const response = await api.post<Approval>(`/approvals/version/${versionId}/approve`, data);
    return response.data;
  },

  getPending: async (): Promise<Approval[]> => {
    const response = await api.get<Approval[]>('/approvals/pending');
    return response.data;
  },
};

// Templates API
export const templatesApi = {
  list: async (params?: { document_type_id?: number; language?: string; active_only?: boolean }): Promise<Template[]> => {
    const response = await api.get<Template[]>('/templates', { params });
    return response.data;
  },

  get: async (id: number): Promise<Template> => {
    const response = await api.get<Template>(`/templates/${id}`);
    return response.data;
  },
};

// Search API
export const searchApi = {
  documents: async (params: {
    q?: string;
    status?: string;
    document_type?: string;
    department?: string;
    product?: string;
    owner?: string;
    page?: number;
    size?: number;
  }): Promise<DocumentListResponse> => {
    const response = await api.get<DocumentListResponse>('/search/documents', { params });
    return response.data;
  },

  reviewDue: async (days: number = 90): Promise<DocumentListResponse> => {
    const response = await api.get<DocumentListResponse>('/search/reports/review-due', { params: { days } });
    return response.data;
  },

  inReview: async (): Promise<DocumentListResponse> => {
    const response = await api.get<DocumentListResponse>('/search/reports/in-review');
    return response.data;
  },

  byProduct: async (productId: number): Promise<DocumentListResponse> => {
    const response = await api.get<DocumentListResponse>(`/search/reports/by-product/${productId}`);
    return response.data;
  },
};

// Audit API
export const auditApi = {
  list: async (params?: {
    entity_type?: string;
    entity_id?: number;
    action?: string;
    performed_by_id?: number;
    page?: number;
    size?: number;
  }): Promise<{ items: AuditLog[]; total: number; page: number; size: number; pages: number }> => {
    const response = await api.get('/audit', { params });
    return response.data;
  },

  getEntityTrail: async (entityType: string, entityId: number): Promise<AuditLog[]> => {
    const response = await api.get<AuditLog[]>(`/audit/entity/${entityType}/${entityId}`);
    return response.data;
  },
};

// Users API
export const usersApi = {
  list: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/users');
    return response.data;
  },

  get: async (id: number): Promise<User> => {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },
};

export default api;

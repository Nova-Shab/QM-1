// User types
export type UserRole = 'admin' | 'author' | 'qa_reviewer' | 'qa_approver' | 'qp' | 'ra' | 'production' | 'read_only';

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  department: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Product types
export type DosageForm = 'drops' | 'injection_solution' | 'tablet' | 'ampoule' | 'oral_solution' | 'cream' | 'ointment' | 'capsule' | 'powder' | 'extract' | 'other';
export type MarketStatus = 'in_development' | 'approved' | 'marketed' | 'discontinued' | 'withdrawn';

export interface Product {
  id: number;
  name: string;
  short_name: string;
  dosage_form: DosageForm;
  strength: string | null;
  product_family: string | null;
  market_status: MarketStatus;
  country: string;
  description: string | null;
  ma_number: string | null;
  created_at: string;
  updated_at: string;
}

// Document type types
export interface DocumentType {
  id: number;
  code: string;
  name: string;
  name_de: string | null;
  description: string | null;
  gxp_relevant: boolean;
  requires_qp_approval: boolean;
  default_review_period_months: number;
  category: string | null;
  created_at: string;
  updated_at: string;
}

// Document types
export type DocumentStatus = 'draft' | 'in_review' | 'approved' | 'effective' | 'obsolete' | 'archived';

export interface DocumentVersionSummary {
  id: number;
  version_major: number;
  version_minor: number;
  status: string;
  created_at: string;
}

export interface Document {
  id: number;
  document_id: string;
  title: string;
  description: string | null;
  department: string;
  language: string;
  status: DocumentStatus;
  effective_date: string | null;
  next_review_date: string | null;
  created_at: string;
  updated_at: string;
  document_type: DocumentType | null;
  owner_id: number;
  versions: DocumentVersionSummary[] | null;
  products: Product[] | null;
}

export interface DocumentListResponse {
  items: Document[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Document version types
export type VersionStatus = 'draft' | 'in_review' | 'approved' | 'effective' | 'superseded' | 'obsolete';

export interface ApprovalSummary {
  id: number;
  approver_name: string;
  approval_role: string;
  decision: string;
  comment: string | null;
  decided_at: string | null;
}

export interface DocumentVersion {
  id: number;
  document_id: number;
  version_major: number;
  version_minor: number;
  version_label: string;
  status: VersionStatus;
  content: Record<string, unknown> | null;
  content_text: string | null;
  file_path: string | null;
  file_name: string | null;
  change_summary: string | null;
  change_reason: string | null;
  related_change_control_id: string | null;
  related_deviation_id: string | null;
  related_capa_id: string | null;
  created_by_id: number;
  created_at: string;
  updated_at: string;
  approved_at: string | null;
  effective_at: string | null;
  superseded_at: string | null;
  superseded_by_version_id: number | null;
  approvals: ApprovalSummary[] | null;
  file_path_full: string | null;
}

// Approval types
export type ApprovalDecision = 'approved' | 'rejected' | 'pending';
export type ApprovalRole = 'author' | 'qa_reviewer' | 'qa_approver' | 'qp' | 'department_head' | 'ra';

export interface Approval {
  id: number;
  document_version_id: number;
  approver_id: number;
  approver_name: string;
  approval_role: ApprovalRole;
  decision: ApprovalDecision;
  comment: string | null;
  sequence_number: number;
  requested_at: string;
  decided_at: string | null;
}

// Template types
export interface Template {
  id: number;
  document_type_id: number;
  name: string;
  description: string | null;
  language: string;
  structure_definition: Record<string, unknown> | null;
  default_content: string | null;
  default_title_pattern: string | null;
  default_document_id_pattern: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Audit log types
export interface AuditLog {
  id: number;
  entity_type: string;
  entity_id: number;
  action: string;
  performed_by_id: number;
  performed_by_name: string | null;
  timestamp: string;
  details: Record<string, unknown> | null;
  description: string | null;
  ip_address: string | null;
}

// Document wizard request
export interface DocumentWizardRequest {
  document_type_id: number;
  product_ids: number[] | null;
  department: string;
  language: string;
  title: string;
  description: string | null;
  template_id: number | null;
  initial_content: Record<string, unknown> | null;
}

// New version request
export interface NewVersionRequest {
  is_major: boolean;
  change_reason: string;
  change_summary: string | null;
  related_change_control_id: string | null;
  related_deviation_id: string | null;
  related_capa_id: string | null;
}

// Approval decision request
export interface ApprovalDecisionRequest {
  decision: ApprovalDecision;
  comment: string | null;
}

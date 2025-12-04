# Pharma DMS - Pharmaceutical Documentation Management System

A GxP-compliant document management system prototype for pharmaceutical manufacturers, designed for companies similar to Dyckerhoff Pharma (GMP-compliant production of sterile small-volume parenterals, vitamin preparations, NaCl solutions, organ extracts, etc.).

## Features

### Document Lifecycle Management
- Create, edit, version, review, approve, and archive documents
- Track status: Draft → InReview → Approved → Effective → Obsolete
- Link documents to products, processes, sites, and departments

### Structured Filing System (Ablagesystem)
- Automatic folder/category assignment based on metadata
- Human-readable document paths, e.g.:
  - `/QA/SOP/QA-SOP-0001/V1.0/`
  - `/Regulatory/FI/REG-FI-0005/V2.0/`
- Consistent document ID system: `{DEPT}-{DOCTYPE}-{NUMBER}`

### Revisions & Versioning
- Major/minor version numbering (e.g., 1.0 → 1.1 → 2.0)
- Change tracking with:
  - Change summary
  - Reason for change
  - Linked change control / deviation / CAPA IDs
- Only one "current approved" version; older ones become superseded

### Approval Workflow (Freigabe)
- Role-based workflow:
  - Author (Fachabteilung)
  - QA Reviewer
  - QA Approver
  - Qualified Person (QP) for certain document types
- Electronic approval with name, role, timestamp, and comment
- Complete audit trail for every status change

### Document Creation Wizard
- Select document type, products, department, language
- Template-based document generation
- Pre-filled metadata and section structure

### Search & Reporting
- Full-text search across title and description
- Filter by product, document type, status, department, owner
- Reports:
  - Documents linked to a specific product
  - Documents currently "In Review"
  - Documents due for review within 90 days

### Compliance Features
- No hard deletion of approved documents (only supersede/archive)
- Complete audit trail for all changes
- Role-based permissions (Author, Reviewer, Approver, QA, QP, Read-only, Admin)

## Technology Stack

### Backend
- **Framework**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT tokens with bcrypt password hashing

### Frontend
- **Framework**: React 18 with TypeScript
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Build Tool**: Vite

## Data Model

### Core Entities

1. **User** - Authentication and authorization
   - Roles: admin, author, qa_reviewer, qa_approver, qp, ra, production, read_only

2. **Product** - Pharmaceutical products
   - Examples: Natriumperchlorat 300 mg/ml, B1-ASmedic, Isotone NaCl-Lösung

3. **DocumentType** - Document categories
   - SOP, WI, FI, GI, SPEC, MBR, COA, VAL, DEV, CAPA, CC, etc.

4. **Document** - Main document entity
   - Links to document type, owner, department
   - Status tracking and review dates

5. **DocumentVersion** - Version control
   - Version numbers, content, change tracking
   - Supersession chain

6. **Approval** - Workflow approvals
   - Approver, role, decision, comments

7. **AuditLog** - Complete audit trail
   - Entity, action, performer, timestamp, details

8. **Template** - Document templates
   - Structure definitions, default patterns

## API Endpoints

### Authentication
```
POST /api/v1/auth/register     - Register new user
POST /api/v1/auth/login        - Login (OAuth2 form)
POST /api/v1/auth/login/json   - Login (JSON body)
GET  /api/v1/auth/me           - Get current user
```

### Products
```
GET    /api/v1/products        - List products
GET    /api/v1/products/{id}   - Get product
POST   /api/v1/products        - Create product
PUT    /api/v1/products/{id}   - Update product
DELETE /api/v1/products/{id}   - Soft delete product
```

### Documents
```
GET    /api/v1/documents                     - List documents (with filters)
GET    /api/v1/documents/{id}                - Get document
POST   /api/v1/documents/wizard              - Create via wizard
PUT    /api/v1/documents/{id}                - Update document
POST   /api/v1/documents/{id}/submit-for-review - Submit for review
```

### Document Versions
```
GET    /api/v1/versions/document/{doc_id}           - List versions
GET    /api/v1/versions/{id}                        - Get version
POST   /api/v1/versions/document/{doc_id}/new-version - Create new version
PUT    /api/v1/versions/{id}                        - Update version
```

### Approvals
```
GET  /api/v1/approvals/version/{ver_id}     - List approvals
POST /api/v1/approvals/version/{ver_id}/review  - Submit review
POST /api/v1/approvals/version/{ver_id}/approve - Final approval
GET  /api/v1/approvals/pending              - Get pending approvals
```

### Search & Reports
```
GET /api/v1/search/documents                    - Search documents
GET /api/v1/search/reports/review-due           - Documents due for review
GET /api/v1/search/reports/in-review            - Documents in review
GET /api/v1/search/reports/by-product/{prod_id} - Documents by product
```

### Audit Trail
```
GET /api/v1/audit                           - List audit logs
GET /api/v1/audit/entity/{type}/{id}        - Entity audit trail
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create database
createdb pharma_dms

# Run migrations
alembic upgrade head

# Seed initial data
python seed_data.py

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Test Users

After seeding the database, the following test users are available:

| Email | Password | Role |
|-------|----------|------|
| admin@pharma-dms.local | admin123 | Admin |
| author@pharma-dms.local | author123 | Author |
| qa.reviewer@pharma-dms.local | reviewer123 | QA Reviewer |
| qa.approver@pharma-dms.local | approver123 | QA Approver |
| qp@pharma-dms.local | qp123 | Qualified Person |
| ra@pharma-dms.local | ra123 | Regulatory Affairs |
| production@pharma-dms.local | prod123 | Production |

## Usage Example: End-to-End Document Workflow

### 1. Create a New SOP

```bash
# Login as author
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email": "author@pharma-dms.local", "password": "author123"}'

# Save the access_token from the response

# Create document via wizard
curl -X POST http://localhost:8000/api/v1/documents/wizard \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "document_type_id": 1,
    "department": "Production",
    "language": "DE",
    "title": "SOP: Herstellung Natriumperchlorat 300 mg/ml Tropfen",
    "description": "Herstellungsanweisung für Natriumperchlorat Tropfen",
    "product_ids": [1]
  }'
```

### 2. Submit for Review

```bash
# Submit document for review (document_id from step 1)
curl -X POST http://localhost:8000/api/v1/documents/1/submit-for-review \
  -H "Authorization: Bearer {access_token}"
```

### 3. Review and Approve

```bash
# Login as QA Approver
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email": "qa.approver@pharma-dms.local", "password": "approver123"}'

# Approve the document version (version_id = 1)
curl -X POST http://localhost:8000/api/v1/approvals/version/1/approve \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approved",
    "comment": "Document reviewed and approved. Content meets GMP requirements."
  }'
```

### 4. Create New Version

```bash
# Login as author again
# Create new version of the approved document
curl -X POST http://localhost:8000/api/v1/versions/document/1/new-version \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "is_major": false,
    "change_reason": "Updated procedure step 5.3 per change control CC-2024-001",
    "change_summary": "Added clarification for mixing time",
    "related_change_control_id": "CC-2024-001"
  }'
```

### 5. Search Documents

```bash
# Search for all documents linked to Natriumperchlorat product
curl -X GET "http://localhost:8000/api/v1/search/reports/by-product/1" \
  -H "Authorization: Bearer {access_token}"

# Search for all documents in review
curl -X GET "http://localhost:8000/api/v1/search/reports/in-review" \
  -H "Authorization: Bearer {access_token}"

# Full-text search
curl -X GET "http://localhost:8000/api/v1/search/documents?q=Natriumperchlorat&status=effective" \
  -H "Authorization: Bearer {access_token}"
```

## Document Status Flow

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌─────────┐   ┌───────────┐   ┌──────────┐   ┌───────────┐
│  DRAFT  │──▶│ IN_REVIEW │──▶│ APPROVED │──▶│ EFFECTIVE │
└─────────┘   └───────────┘   └──────────┘   └───────────┘
     ▲              │                              │
     │              │                              │
     │   (reject)   │                              │
     └──────────────┘                              │
                                                   │
                    ┌──────────────────────────────┘
                    │  (new version created)
                    ▼
              ┌────────────┐   ┌──────────┐
              │ SUPERSEDED │──▶│ OBSOLETE │
              └────────────┘   └──────────┘
```

## Future Enhancements

This prototype can be extended towards:

1. **21 CFR Part 11 Compliance**
   - Electronic signatures
   - Signature manifestations
   - Time-stamped audit trails

2. **Training Management**
   - Read & Understand tracking
   - Training task assignments
   - Competency tracking

3. **Integration Capabilities**
   - External DMS/SharePoint integration
   - ERP system integration
   - Email notifications

4. **Advanced Features**
   - Document comparison (diff)
   - PDF generation
   - Batch record execution
   - Deviation/CAPA linkage

## License

This is a prototype for educational and planning purposes.

## Author

Pharma DMS Development Team

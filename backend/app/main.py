"""
Pharma DMS - Pharmaceutical Documentation Management System
Main application entry point.

This is a GxP-aligned document management system prototype for
pharmaceutical manufacturers, featuring:
- Document lifecycle management (Draft → InReview → Approved → Effective → Obsolete)
- Structured filing system with automatic document IDs
- Version control with change tracking
- Review and approval workflows
- Complete audit trail for GxP compliance
- Document creation wizard with templates

Author: Pharma DMS Team
Version: 1.0.0
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import (
    auth,
    users,
    products,
    document_types,
    documents,
    versions,
    approvals,
    templates,
    search,
    audit,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Pharmaceutical Documentation Management System

A GxP-compliant document management system for pharmaceutical manufacturers.

### Features

- **Document Lifecycle Management**: Create, edit, version, review, approve, and archive documents
- **Structured Filing System**: Automatic folder/category assignment based on metadata
- **Version Control**: Full version history with change tracking and reason documentation
- **Approval Workflow**: Role-based workflow (Author → QA Reviewer → QA Approver → QP)
- **Audit Trail**: Complete logging of all actions for GxP compliance
- **Document Wizard**: Template-based document creation

### Document Status Flow

```
Draft → InReview → Approved → Effective → Obsolete
         ↑ reject           ↓ new version
         └─────────────────┘
```

### Role-Based Access

- **Admin**: Full system access
- **Author**: Create and edit documents
- **QA Reviewer**: Review documents
- **QA Approver**: Approve documents
- **QP (Qualified Person)**: Required for certain document types
- **Read-Only**: View-only access
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(document_types.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(versions.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(templates.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Pharmaceutical Documentation Management System",
        "documentation": "/docs",
        "api_prefix": "/api/v1"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

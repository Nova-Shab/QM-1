"""
Document service for complex document operations.
"""
from typing import Optional, List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.document import Document, DocumentStatus
from app.models.document_version import DocumentVersion, VersionStatus
from app.models.document_type import DocumentType
from app.models.document_product_link import DocumentProductLink, RelationType
from app.models.template import Template
from app.models.user import User
from app.services.audit import create_audit_log


async def generate_document_id(
    db: AsyncSession,
    department: str,
    document_type_code: str
) -> str:
    """
    Generate a unique document ID based on department and document type.

    Format: {DEPT}-{DOCTYPE}-{RUNNING_NUMBER}
    Example: QA-SOP-0001, REG-FI-0005

    Args:
        db: Database session
        department: Department code (e.g., QA, REG, PROD)
        document_type_code: Document type code (e.g., SOP, FI, WI)

    Returns:
        Generated document ID
    """
    # Count existing documents with this prefix
    prefix = f"{department}-{document_type_code}-"

    result = await db.execute(
        select(func.count(Document.id)).where(Document.document_id.like(f"{prefix}%"))
    )
    count = result.scalar() or 0

    # Generate the next number (zero-padded to 4 digits)
    next_number = count + 1
    return f"{prefix}{next_number:04d}"


async def create_document_from_wizard(
    db: AsyncSession,
    document_type_id: int,
    department: str,
    language: str,
    title: str,
    description: Optional[str],
    created_by: User,
    product_ids: Optional[List[int]] = None,
    template_id: Optional[int] = None,
    initial_content: Optional[dict] = None
) -> Document:
    """
    Create a new document using the document creation wizard.

    This function:
    1. Generates a unique document ID
    2. Creates the Document record
    3. Creates the initial DocumentVersion (v1.0)
    4. Links products if specified
    5. Applies template structure if specified
    6. Creates audit log entries

    Args:
        db: Database session
        document_type_id: ID of the document type
        department: Department code
        language: Language code (DE, EN)
        title: Document title
        description: Optional description
        created_by: User creating the document
        product_ids: Optional list of product IDs to link
        template_id: Optional template ID to use
        initial_content: Optional initial content

    Returns:
        Created Document with initial version
    """
    # Get document type
    result = await db.execute(select(DocumentType).where(DocumentType.id == document_type_id))
    doc_type = result.scalar_one_or_none()
    if not doc_type:
        raise ValueError(f"Document type {document_type_id} not found")

    # Generate document ID
    document_id = await generate_document_id(db, department, doc_type.code)

    # Calculate next review date based on document type's default review period
    review_period = doc_type.default_review_period_months or 24
    next_review_date = (datetime.utcnow() + relativedelta(months=review_period)).date()

    # Create document
    document = Document(
        document_id=document_id,
        title=title,
        description=description,
        document_type_id=document_type_id,
        department=department,
        language=language,
        owner_id=created_by.id,
        status=DocumentStatus.DRAFT,
        next_review_date=next_review_date
    )
    db.add(document)
    await db.flush()  # Get the document ID

    # Prepare content from template if specified
    content = initial_content
    if template_id:
        result = await db.execute(select(Template).where(Template.id == template_id))
        template = result.scalar_one_or_none()
        if template and template.structure_definition:
            content = content or {}
            content["_template"] = template.structure_definition
            content["_template_id"] = template_id

    # Create initial version (v1.0)
    version = DocumentVersion(
        document_id=document.id,
        version_major=1,
        version_minor=0,
        status=VersionStatus.DRAFT,
        content=content,
        created_by_id=created_by.id
    )
    db.add(version)

    # Link products if specified
    if product_ids:
        for i, product_id in enumerate(product_ids):
            link = DocumentProductLink(
                document_id=document.id,
                product_id=product_id,
                relation_type=RelationType.PRIMARY if i == 0 else RelationType.RELATED
            )
            db.add(link)

    await db.flush()

    # Create audit logs
    await create_audit_log(
        db=db,
        entity_type="Document",
        entity_id=document.id,
        action="create",
        performed_by_id=created_by.id,
        details={
            "document_id": document_id,
            "title": title,
            "document_type": doc_type.code,
            "method": "wizard"
        },
        description=f"Document {document_id} created via wizard"
    )

    await create_audit_log(
        db=db,
        entity_type="DocumentVersion",
        entity_id=version.id,
        action="create",
        performed_by_id=created_by.id,
        details={
            "version": "1.0",
            "status": "draft"
        }
    )

    return document


async def create_new_version(
    db: AsyncSession,
    document_id: int,
    created_by: User,
    is_major: bool = False,
    change_reason: str = "",
    change_summary: Optional[str] = None,
    related_change_control_id: Optional[str] = None,
    related_deviation_id: Optional[str] = None,
    related_capa_id: Optional[str] = None
) -> DocumentVersion:
    """
    Create a new version of an existing document.

    This function:
    1. Finds the current approved version
    2. Copies its content
    3. Increments version number (major or minor)
    4. Creates a new draft version

    Args:
        db: Database session
        document_id: ID of the document
        created_by: User creating the new version
        is_major: If True, increment major version; else increment minor
        change_reason: Reason for creating new version
        change_summary: Optional summary of changes
        related_change_control_id: Optional related change control ID
        related_deviation_id: Optional related deviation ID
        related_capa_id: Optional related CAPA ID

    Returns:
        Created DocumentVersion
    """
    # Get document
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise ValueError(f"Document {document_id} not found")

    # Get current effective/approved version
    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document_id)
        .where(DocumentVersion.status.in_([VersionStatus.EFFECTIVE, VersionStatus.APPROVED]))
        .order_by(DocumentVersion.version_major.desc(), DocumentVersion.version_minor.desc())
        .limit(1)
    )
    current_version = result.scalar_one_or_none()

    if current_version:
        if is_major:
            new_major = current_version.version_major + 1
            new_minor = 0
        else:
            new_major = current_version.version_major
            new_minor = current_version.version_minor + 1
        content = current_version.content
        content_text = current_version.content_text
    else:
        # No approved version yet, start from 1.0 or 0.1
        new_major = 1
        new_minor = 0
        content = None
        content_text = None

    # Create new version
    new_version = DocumentVersion(
        document_id=document_id,
        version_major=new_major,
        version_minor=new_minor,
        status=VersionStatus.DRAFT,
        content=content,
        content_text=content_text,
        change_reason=change_reason,
        change_summary=change_summary,
        related_change_control_id=related_change_control_id,
        related_deviation_id=related_deviation_id,
        related_capa_id=related_capa_id,
        created_by_id=created_by.id
    )
    db.add(new_version)

    # Update document status to draft
    document.status = DocumentStatus.DRAFT
    await db.flush()

    # Create audit log
    await create_audit_log(
        db=db,
        entity_type="DocumentVersion",
        entity_id=new_version.id,
        action="create",
        performed_by_id=created_by.id,
        details={
            "version": f"{new_major}.{new_minor}",
            "is_major": is_major,
            "change_reason": change_reason,
            "from_version": f"{current_version.version_major}.{current_version.version_minor}" if current_version else None
        },
        description=f"New version {new_major}.{new_minor} created"
    )

    return new_version


def compute_file_path(document: Document, version: DocumentVersion) -> str:
    """
    Compute the file storage path for a document version.

    Format: /{department}/{document_type_code}/{document_id}/V{version}/
    Example: /QA/SOP/QA-SOP-0001/V1.0/

    Args:
        document: The document
        version: The document version

    Returns:
        File path string
    """
    doc_type_code = document.document_type.code if document.document_type else "UNKNOWN"
    return f"/{document.department}/{doc_type_code}/{document.document_id}/V{version.version_major}.{version.version_minor}/"

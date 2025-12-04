"""Initial schema for Pharma DMS

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'author', 'qa_reviewer', 'qa_approver', 'qp', 'ra', 'production', 'read_only', name='userrole'), nullable=False),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_users'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_id', 'users', ['id'])

    # Products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('short_name', sa.String(200), nullable=False),
        sa.Column('dosage_form', sa.Enum('drops', 'injection_solution', 'tablet', 'ampoule', 'oral_solution', 'cream', 'ointment', 'capsule', 'powder', 'extract', 'other', name='dosageform'), nullable=False),
        sa.Column('strength', sa.String(100), nullable=True),
        sa.Column('product_family', sa.String(100), nullable=True),
        sa.Column('market_status', sa.Enum('in_development', 'approved', 'marketed', 'discontinued', 'withdrawn', name='marketstatus'), nullable=True),
        sa.Column('country', sa.String(10), default='DE'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ma_number', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_products')
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_name', 'products', ['name'])

    # Document types table
    op.create_table(
        'document_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('name_de', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('gxp_relevant', sa.Boolean(), default=True),
        sa.Column('requires_qp_approval', sa.Boolean(), default=False),
        sa.Column('default_review_period_months', sa.Integer(), default=24),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_document_types'),
        sa.UniqueConstraint('code', name='uq_document_types_code')
    )
    op.create_index('ix_document_types_id', 'document_types', ['id'])
    op.create_index('ix_document_types_code', 'document_types', ['code'])

    # Documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.String(100), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('document_type_id', sa.Integer(), nullable=False),
        sa.Column('department', sa.String(100), nullable=False),
        sa.Column('language', sa.String(10), default='DE'),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'in_review', 'approved', 'effective', 'obsolete', 'archived', name='documentstatus'), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('next_review_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_type_id'], ['document_types.id'], name='fk_documents_document_type_id_document_types'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='fk_documents_owner_id_users'),
        sa.PrimaryKeyConstraint('id', name='pk_documents'),
        sa.UniqueConstraint('document_id', name='uq_documents_document_id')
    )
    op.create_index('ix_documents_id', 'documents', ['id'])
    op.create_index('ix_documents_document_id', 'documents', ['document_id'])

    # Document versions table
    op.create_table(
        'document_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_major', sa.Integer(), nullable=False, default=1),
        sa.Column('version_minor', sa.Integer(), nullable=False, default=0),
        sa.Column('status', sa.Enum('draft', 'in_review', 'approved', 'effective', 'superseded', 'obsolete', name='versionstatus'), nullable=True),
        sa.Column('content', sa.JSON(), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('related_change_control_id', sa.String(100), nullable=True),
        sa.Column('related_deviation_id', sa.String(100), nullable=True),
        sa.Column('related_capa_id', sa.String(100), nullable=True),
        sa.Column('superseded_by_version_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('effective_at', sa.DateTime(), nullable=True),
        sa.Column('superseded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='fk_document_versions_document_id_documents'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='fk_document_versions_created_by_id_users'),
        sa.ForeignKeyConstraint(['superseded_by_version_id'], ['document_versions.id'], name='fk_document_versions_superseded_by_version_id_document_versions'),
        sa.PrimaryKeyConstraint('id', name='pk_document_versions')
    )
    op.create_index('ix_document_versions_id', 'document_versions', ['id'])

    # Document product links table
    op.create_table(
        'document_product_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('relation_type', sa.Enum('primary', 'related', 'reference', name='relationtype'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='fk_document_product_links_document_id_documents'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_document_product_links_product_id_products'),
        sa.PrimaryKeyConstraint('id', name='pk_document_product_links')
    )
    op.create_index('ix_document_product_links_id', 'document_product_links', ['id'])

    # Approvals table
    op.create_table(
        'approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_version_id', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=False),
        sa.Column('approval_role', sa.Enum('author', 'qa_reviewer', 'qa_approver', 'qp', 'department_head', 'ra', name='approvalrole'), nullable=False),
        sa.Column('decision', sa.Enum('approved', 'rejected', 'pending', name='approvaldecision'), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('sequence_number', sa.Integer(), default=1),
        sa.Column('requested_at', sa.DateTime(), nullable=True),
        sa.Column('decided_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_version_id'], ['document_versions.id'], name='fk_approvals_document_version_id_document_versions'),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], name='fk_approvals_approver_id_users'),
        sa.PrimaryKeyConstraint('id', name='pk_approvals')
    )
    op.create_index('ix_approvals_id', 'approvals', ['id'])

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('performed_by_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['performed_by_id'], ['users.id'], name='fk_audit_logs_performed_by_id_users'),
        sa.PrimaryKeyConstraint('id', name='pk_audit_logs')
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])

    # Templates table
    op.create_table(
        'templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_type_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('language', sa.String(10), default='DE'),
        sa.Column('structure_definition', sa.JSON(), nullable=True),
        sa.Column('default_content', sa.Text(), nullable=True),
        sa.Column('default_title_pattern', sa.String(500), nullable=True),
        sa.Column('default_document_id_pattern', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_type_id'], ['document_types.id'], name='fk_templates_document_type_id_document_types'),
        sa.PrimaryKeyConstraint('id', name='pk_templates')
    )
    op.create_index('ix_templates_id', 'templates', ['id'])

    # Training tasks table
    op.create_table(
        'training_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_version_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'completed', 'overdue', 'exempt', name='trainingstatus'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('completion_comment', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_version_id'], ['document_versions.id'], name='fk_training_tasks_document_version_id_document_versions'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_training_tasks_user_id_users'),
        sa.PrimaryKeyConstraint('id', name='pk_training_tasks')
    )
    op.create_index('ix_training_tasks_id', 'training_tasks', ['id'])


def downgrade() -> None:
    op.drop_table('training_tasks')
    op.drop_table('templates')
    op.drop_table('audit_logs')
    op.drop_table('approvals')
    op.drop_table('document_product_links')
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('document_types')
    op.drop_table('products')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS trainingstatus')
    op.execute('DROP TYPE IF EXISTS approvaldecision')
    op.execute('DROP TYPE IF EXISTS approvalrole')
    op.execute('DROP TYPE IF EXISTS relationtype')
    op.execute('DROP TYPE IF EXISTS versionstatus')
    op.execute('DROP TYPE IF EXISTS documentstatus')
    op.execute('DROP TYPE IF EXISTS marketstatus')
    op.execute('DROP TYPE IF EXISTS dosageform')
    op.execute('DROP TYPE IF EXISTS userrole')

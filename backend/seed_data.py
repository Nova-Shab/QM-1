"""
Seed data script for Pharma DMS.

This script populates the database with example data for testing
and demonstration purposes, including:
- Users (Admin, Author, QA Reviewer, QA Approver, QP)
- Products (based on Dyckerhoff Pharma portfolio)
- Document types (SOP, WI, FI, GI, etc.)
- Templates for document creation
"""
import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.product import Product, DosageForm, MarketStatus
from app.models.document_type import DocumentType
from app.models.template import Template


# Test users
USERS = [
    {
        "email": "admin@pharma-dms.local",
        "name": "System Administrator",
        "password": "admin123",
        "role": UserRole.ADMIN,
        "department": "IT"
    },
    {
        "email": "author@pharma-dms.local",
        "name": "Dr. Maria Schmidt",
        "password": "author123",
        "role": UserRole.AUTHOR,
        "department": "Production"
    },
    {
        "email": "qa.reviewer@pharma-dms.local",
        "name": "Thomas Müller",
        "password": "reviewer123",
        "role": UserRole.QA_REVIEWER,
        "department": "QA"
    },
    {
        "email": "qa.approver@pharma-dms.local",
        "name": "Dr. Anna Weber",
        "password": "approver123",
        "role": UserRole.QA_APPROVER,
        "department": "QA"
    },
    {
        "email": "qp@pharma-dms.local",
        "name": "Prof. Dr. Hans Fischer",
        "password": "qp123",
        "role": UserRole.QP,
        "department": "QA"
    },
    {
        "email": "ra@pharma-dms.local",
        "name": "Lisa Braun",
        "password": "ra123",
        "role": UserRole.RA,
        "department": "Regulatory Affairs"
    },
    {
        "email": "production@pharma-dms.local",
        "name": "Klaus Wagner",
        "password": "prod123",
        "role": UserRole.PRODUCTION,
        "department": "Production"
    },
]

# Products (based on Dyckerhoff Pharma portfolio)
PRODUCTS = [
    {
        "name": "Natriumperchlorat Dyckerhoff 300 mg/ml Tropfen zum Einnehmen",
        "short_name": "Natriumperchlorat 300 mg/ml",
        "dosage_form": DosageForm.DROPS,
        "strength": "300 mg/ml",
        "product_family": "Dyckerhoff",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Tropfen zum Einnehmen, Natriumperchlorat zur Schilddrüsenblockade",
        "ma_number": "6180580.00.00"
    },
    {
        "name": "Isotone Natriumchlorid-Lösung ASmedic 0,9%",
        "short_name": "Isotone NaCl ASmedic",
        "dosage_form": DosageForm.INJECTION_SOLUTION,
        "strength": "0.9%",
        "product_family": "ASmedic",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Isotone Natriumchlorid-Lösung zur parenteralen Anwendung"
    },
    {
        "name": "B1-ASmedic 100 mg Tabletten",
        "short_name": "B1-ASmedic",
        "dosage_form": DosageForm.TABLET,
        "strength": "100 mg",
        "product_family": "ASmedic",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Thiaminhydrochlorid (Vitamin B1) Tabletten"
    },
    {
        "name": "B12-ASmedic 1000 µg Injektionslösung",
        "short_name": "B12-ASmedic Ampullen",
        "dosage_form": DosageForm.AMPOULE,
        "strength": "1000 µg",
        "product_family": "ASmedic",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Cyanocobalamin (Vitamin B12) Injektionslösung"
    },
    {
        "name": "B12-ASmedic Tropfen zum Einnehmen",
        "short_name": "B12-ASmedic Tropfen",
        "dosage_form": DosageForm.DROPS,
        "strength": "500 µg/ml",
        "product_family": "ASmedic",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Cyanocobalamin (Vitamin B12) Tropfen zum Einnehmen"
    },
    {
        "name": "Wasser für Injektionszwecke",
        "short_name": "WFI",
        "dosage_form": DosageForm.INJECTION_SOLUTION,
        "strength": None,
        "product_family": "ASmedic",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Steriles Wasser für Injektionszwecke (Water for Injection)"
    },
    {
        "name": "REGENERESEN Na-RNA Organextrakte",
        "short_name": "Regeneresen Na-RNA",
        "dosage_form": DosageForm.EXTRACT,
        "strength": None,
        "product_family": "Regeneresen",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Natrium-Ribonukleinat Organextrakte"
    },
    {
        "name": "Regeneresen Night Care Creme",
        "short_name": "Regeneresen Night Care",
        "dosage_form": DosageForm.CREAM,
        "strength": None,
        "product_family": "Regeneresen",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Kosmetische Nachtpflegecreme mit regenerierenden Wirkstoffen"
    },
]

# Document types
DOCUMENT_TYPES = [
    {
        "code": "SOP",
        "name": "Standard Operating Procedure",
        "name_de": "Standardarbeitsanweisung",
        "description": "Detailed written instructions to achieve uniformity in the performance of a specific function",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 24,
        "category": "Quality"
    },
    {
        "code": "WI",
        "name": "Work Instruction",
        "name_de": "Arbeitsanweisung",
        "description": "Step-by-step instructions for performing specific tasks",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 24,
        "category": "Quality"
    },
    {
        "code": "FORM",
        "name": "Form/Template",
        "name_de": "Formular/Vorlage",
        "description": "Standardized forms and templates for documentation",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 36,
        "category": "Quality"
    },
    {
        "code": "SPEC",
        "name": "Specification",
        "name_de": "Spezifikation",
        "description": "Product or material specifications",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 24,
        "category": "Quality"
    },
    {
        "code": "MBR",
        "name": "Master Batch Record",
        "name_de": "Muster-Herstellungsanweisung",
        "description": "Master document for batch production",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 24,
        "category": "Production"
    },
    {
        "code": "FI",
        "name": "Summary of Product Characteristics (SmPC)",
        "name_de": "Fachinformation",
        "description": "Summary of Product Characteristics for healthcare professionals",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 12,
        "category": "Regulatory"
    },
    {
        "code": "GI",
        "name": "Package Insert (PIL)",
        "name_de": "Gebrauchsinformation (Packungsbeilage)",
        "description": "Patient Information Leaflet / Package Insert",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 12,
        "category": "Regulatory"
    },
    {
        "code": "COA",
        "name": "Certificate of Analysis",
        "name_de": "Analysenzertifikat",
        "description": "Certificate documenting analytical test results",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": None,
        "category": "Quality"
    },
    {
        "code": "TEST",
        "name": "Test Instruction",
        "name_de": "Prüfanweisung",
        "description": "Instructions for analytical testing procedures",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 24,
        "category": "Quality"
    },
    {
        "code": "VAL",
        "name": "Validation Document",
        "name_de": "Validierungsdokument",
        "description": "Process, method, or equipment validation documents",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 36,
        "category": "Quality"
    },
    {
        "code": "DEV",
        "name": "Deviation Report",
        "name_de": "Abweichungsbericht",
        "description": "Documentation of deviations from established procedures",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": None,
        "category": "Quality"
    },
    {
        "code": "CAPA",
        "name": "CAPA Report",
        "name_de": "CAPA-Bericht",
        "description": "Corrective and Preventive Action documentation",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": None,
        "category": "Quality"
    },
    {
        "code": "CC",
        "name": "Change Control",
        "name_de": "Änderungskontrolle",
        "description": "Change control documentation",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": None,
        "category": "Quality"
    },
    {
        "code": "GMP-CERT",
        "name": "GMP Certificate",
        "name_de": "GMP-Zertifikat",
        "description": "Good Manufacturing Practice Certificate",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 36,
        "category": "Quality"
    },
    {
        "code": "QUAL",
        "name": "Qualification Document",
        "name_de": "Qualifizierungsdokument",
        "description": "Equipment or facility qualification documents (IQ/OQ/PQ)",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 36,
        "category": "Quality"
    },
]

# Templates
TEMPLATES = [
    {
        "document_type_code": "SOP",
        "name": "Standard SOP Template (German)",
        "description": "Standard template for SOPs in German language",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "purpose", "title": "1. Zweck", "required": True, "default_content": "Diese SOP beschreibt..."},
                {"id": "scope", "title": "2. Geltungsbereich", "required": True, "default_content": "Diese SOP gilt für..."},
                {"id": "responsibilities", "title": "3. Verantwortlichkeiten", "required": True, "default_content": ""},
                {"id": "definitions", "title": "4. Definitionen und Abkürzungen", "required": False, "default_content": ""},
                {"id": "procedure", "title": "5. Verfahren", "required": True, "default_content": ""},
                {"id": "records", "title": "6. Aufzeichnungen", "required": True, "default_content": ""},
                {"id": "references", "title": "7. Referenzen", "required": False, "default_content": ""},
                {"id": "attachments", "title": "8. Anlagen", "required": False, "default_content": ""},
                {"id": "history", "title": "9. Dokumentenhistorie", "required": True, "default_content": ""}
            ]
        },
        "default_title_pattern": "SOP: {{process_name}}",
        "default_document_id_pattern": "{{dept}}-SOP-{{number}}"
    },
    {
        "document_type_code": "WI",
        "name": "Work Instruction Template (German)",
        "description": "Standard template for Work Instructions in German language",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "purpose", "title": "1. Zweck", "required": True},
                {"id": "scope", "title": "2. Geltungsbereich", "required": True},
                {"id": "materials", "title": "3. Materialien und Geräte", "required": True},
                {"id": "procedure", "title": "4. Durchführung", "required": True},
                {"id": "safety", "title": "5. Sicherheitshinweise", "required": False},
                {"id": "records", "title": "6. Aufzeichnungen", "required": True}
            ]
        },
        "default_title_pattern": "AA: {{task_name}}",
        "default_document_id_pattern": "{{dept}}-WI-{{number}}"
    },
    {
        "document_type_code": "SPEC",
        "name": "Product Specification Template (German)",
        "description": "Template for product specifications",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "product_info", "title": "1. Produktinformationen", "required": True},
                {"id": "description", "title": "2. Beschreibung", "required": True},
                {"id": "composition", "title": "3. Zusammensetzung", "required": True},
                {"id": "tests", "title": "4. Prüfungen", "required": True},
                {"id": "limits", "title": "5. Grenzwerte", "required": True},
                {"id": "storage", "title": "6. Lagerung", "required": True},
                {"id": "shelf_life", "title": "7. Haltbarkeit", "required": True}
            ]
        },
        "default_title_pattern": "Spezifikation: {{product_name}}",
        "default_document_id_pattern": "{{dept}}-SPEC-{{number}}"
    },
    {
        "document_type_code": "MBR",
        "name": "Master Batch Record Template",
        "description": "Template for Master Batch Records",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "header", "title": "1. Kopfdaten", "required": True},
                {"id": "materials", "title": "2. Ausgangsmaterialien", "required": True},
                {"id": "equipment", "title": "3. Geräte und Anlagen", "required": True},
                {"id": "production_steps", "title": "4. Herstellungsschritte", "required": True},
                {"id": "ipc", "title": "5. In-Prozess-Kontrollen", "required": True},
                {"id": "packaging", "title": "6. Verpackung", "required": True},
                {"id": "yields", "title": "7. Ausbeuten", "required": True},
                {"id": "release", "title": "8. Freigabe", "required": True}
            ]
        },
        "default_title_pattern": "MBR: {{product_name}} - Chargengröße {{batch_size}}",
        "default_document_id_pattern": "PROD-MBR-{{number}}"
    },
]


async def seed_database():
    """Seed the database with initial data."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping...")
            return

        print("Seeding database...")

        # Create users
        print("Creating users...")
        for user_data in USERS:
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                department=user_data["department"]
            )
            session.add(user)
        await session.commit()
        print(f"  Created {len(USERS)} users")

        # Create products
        print("Creating products...")
        for product_data in PRODUCTS:
            product = Product(**product_data)
            session.add(product)
        await session.commit()
        print(f"  Created {len(PRODUCTS)} products")

        # Create document types
        print("Creating document types...")
        doc_type_map = {}
        for dt_data in DOCUMENT_TYPES:
            doc_type = DocumentType(**dt_data)
            session.add(doc_type)
            await session.flush()
            doc_type_map[dt_data["code"]] = doc_type.id
        await session.commit()
        print(f"  Created {len(DOCUMENT_TYPES)} document types")

        # Create templates
        print("Creating templates...")
        for tmpl_data in TEMPLATES:
            code = tmpl_data.pop("document_type_code")
            template = Template(
                document_type_id=doc_type_map[code],
                **tmpl_data
            )
            session.add(template)
        await session.commit()
        print(f"  Created {len(TEMPLATES)} templates")

        print("\nDatabase seeding completed successfully!")
        print("\nTest users created:")
        for user in USERS:
            print(f"  - {user['email']} / {user['password']} ({user['role'].value})")


if __name__ == "__main__":
    asyncio.run(seed_database())

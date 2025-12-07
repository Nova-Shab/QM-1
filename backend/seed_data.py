"""
Seed data script for Pharma DMS.

This script populates the database with example data for testing
and demonstration purposes, including:
- Users (Admin, Author, QA Reviewer, QA Approver, QP)
- Products (based on Dyckerhoff Pharma portfolio)
- Document types (SOP, WI, FI, GI, etc.)
- Templates for document creation
- Sample documents for each product
"""
import asyncio
from datetime import datetime, timedelta
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.product import Product, DosageForm, MarketStatus
from app.models.document_type import DocumentType
from app.models.template import Template
from app.models.document import Document, DocumentStatus
from app.models.document_version import DocumentVersion
from app.models.document_product_link import DocumentProductLink


# Test users
USERS = [
    {
        "email": "admin@pharma-dms.de",
        "name": "System Administrator",
        "password": "admin123",
        "role": UserRole.ADMIN,
        "department": "IT"
    },
    {
        "email": "author@pharma-dms.de",
        "name": "Dr. Maria Schmidt",
        "password": "author123",
        "role": UserRole.AUTHOR,
        "department": "Production"
    },
    {
        "email": "qa.reviewer@pharma-dms.de",
        "name": "Thomas Müller",
        "password": "reviewer123",
        "role": UserRole.QA_REVIEWER,
        "department": "QA"
    },
    {
        "email": "qa.approver@pharma-dms.de",
        "name": "Dr. Anna Weber",
        "password": "approver123",
        "role": UserRole.QA_APPROVER,
        "department": "QA"
    },
    {
        "email": "qp@pharma-dms.de",
        "name": "Prof. Dr. Hans Fischer",
        "password": "qp123",
        "role": UserRole.QP,
        "department": "QA"
    },
    {
        "email": "ra@pharma-dms.de",
        "name": "Lisa Braun",
        "password": "ra123",
        "role": UserRole.RA,
        "department": "Regulatory Affairs"
    },
    {
        "email": "production@pharma-dms.de",
        "name": "Klaus Wagner",
        "password": "prod123",
        "role": UserRole.PRODUCTION,
        "department": "Production"
    },
]

# Products (based on Dyckerhoff Pharma portfolio from website)
PRODUCTS = [
    {
        "name": "Natriumperchlorat Dyckerhoff 300 mg/ml Tropfen zum Einnehmen",
        "short_name": "Natriumperchlorat 300 mg/ml",
        "dosage_form": DosageForm.DROPS,
        "strength": "300 mg/ml",
        "product_family": "Dyckerhoff",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Tropfen zum Einnehmen, Natriumperchlorat zur Schilddrüsenblockade. Eigenproduktion in Köln.",
        "ma_number": "6180580.00.00"
    },
    {
        "name": "B1-ASmedic 100 mg Tabletten",
        "short_name": "B1-ASmedic",
        "dosage_form": DosageForm.TABLET,
        "strength": "100 mg",
        "product_family": "ASmedic",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Thiaminnitrat (Vitamin B1) Tabletten zur Behandlung von Vitamin B1-Mangel"
    },
    {
        "name": "B12-ASmedic 1 mg/1 ml Injektionslösung",
        "short_name": "B12-ASmedic Ampullen",
        "dosage_form": DosageForm.AMPOULE,
        "strength": "1 mg/1 ml",
        "product_family": "ASmedic",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Cyanocobalamin (Vitamin B12) Injektionslösung in Ampullen"
    },
    {
        "name": "B12-ASmedic 50 µg/ml Tropfen zum Einnehmen",
        "short_name": "B12-ASmedic Tropfen",
        "dosage_form": DosageForm.DROPS,
        "strength": "50 µg/ml",
        "product_family": "ASmedic",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Cyanocobalamin (Vitamin B12) Lösung zum Einnehmen"
    },
    {
        "name": "Aqua ad Iniectabilia ex Colonia 2 ml",
        "short_name": "WFI 2 ml",
        "dosage_form": DosageForm.AMPOULE,
        "strength": "2 ml",
        "product_family": "Aqua",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Wasser für Injektionszwecke (Water for Injection) in 2 ml Ampullen"
    },
    {
        "name": "Aqua ad Iniectabilia ex Colonia 5 ml",
        "short_name": "WFI 5 ml",
        "dosage_form": DosageForm.AMPOULE,
        "strength": "5 ml",
        "product_family": "Aqua",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Wasser für Injektionszwecke (Water for Injection) in 5 ml Ampullen"
    },
    {
        "name": "Dyckerhoff Organextrakte Na-RNA",
        "short_name": "Na-RNA Extrakte",
        "dosage_form": DosageForm.EXTRACT,
        "strength": None,
        "product_family": "Dyckerhoff",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Organextrakte und Na-RNA-Extrakt aus Hefe zur Herstellung von Apothekenrezepturen"
    },
    {
        "name": "Regeneresen Creme Night Care",
        "short_name": "Regeneresen Night Care",
        "dosage_form": DosageForm.CREAM,
        "strength": "30 ml",
        "product_family": "Regeneresen",
        "market_status": MarketStatus.MARKETED,
        "country": "DE",
        "description": "Kosmetische Nachtpflegecreme im Spender (30 ml)"
    },
]

# Document types
DOCUMENT_TYPES = [
    {
        "code": "SOP",
        "name": "Standard Operating Procedure",
        "name_de": "Standardarbeitsanweisung",
        "description": "Detaillierte schriftliche Anweisungen zur einheitlichen Durchführung von Prozessen",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 24,
        "category": "Quality"
    },
    {
        "code": "WI",
        "name": "Work Instruction",
        "name_de": "Arbeitsanweisung",
        "description": "Schritt-für-Schritt Anleitung für spezifische Tätigkeiten",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 24,
        "category": "Quality"
    },
    {
        "code": "FORM",
        "name": "Form/Template",
        "name_de": "Formular/Vorlage",
        "description": "Standardisierte Formulare und Vorlagen für die Dokumentation",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 36,
        "category": "Quality"
    },
    {
        "code": "SPEC",
        "name": "Specification",
        "name_de": "Spezifikation",
        "description": "Produkt- oder Materialspezifikationen mit Prüfkriterien und Grenzwerten",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 24,
        "category": "Quality"
    },
    {
        "code": "MBR",
        "name": "Master Batch Record",
        "name_de": "Muster-Herstellungsanweisung",
        "description": "Masterdokument für die Chargenproduktion",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 24,
        "category": "Production"
    },
    {
        "code": "FI",
        "name": "Summary of Product Characteristics (SmPC)",
        "name_de": "Fachinformation",
        "description": "Zusammenfassung der Merkmale des Arzneimittels für Fachkreise",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 12,
        "category": "Regulatory"
    },
    {
        "code": "GI",
        "name": "Package Leaflet (PIL)",
        "name_de": "Gebrauchsinformation (Packungsbeilage)",
        "description": "Beipackzettel / Patienteninformation",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 12,
        "category": "Regulatory"
    },
    {
        "code": "COA",
        "name": "Certificate of Analysis",
        "name_de": "Analysenzertifikat",
        "description": "Zertifikat mit dokumentierten Analyseergebnissen",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": None,
        "category": "Quality"
    },
    {
        "code": "TEST",
        "name": "Test Instruction",
        "name_de": "Prüfanweisung",
        "description": "Anweisungen für analytische Prüfverfahren",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 24,
        "category": "Quality"
    },
    {
        "code": "VAL",
        "name": "Validation Document",
        "name_de": "Validierungsdokument",
        "description": "Prozess-, Methoden- oder Gerätevalidierung",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 36,
        "category": "Quality"
    },
    {
        "code": "DEV",
        "name": "Deviation Report",
        "name_de": "Abweichungsbericht",
        "description": "Dokumentation von Abweichungen von etablierten Verfahren",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": None,
        "category": "Quality"
    },
    {
        "code": "CAPA",
        "name": "CAPA Report",
        "name_de": "CAPA-Bericht",
        "description": "Korrektur- und Vorbeugemaßnahmen Dokumentation",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": None,
        "category": "Quality"
    },
    {
        "code": "CC",
        "name": "Change Control",
        "name_de": "Änderungskontrolle",
        "description": "Änderungskontrolle-Dokumentation",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": None,
        "category": "Quality"
    },
    {
        "code": "QUAL",
        "name": "Qualification Document",
        "name_de": "Qualifizierungsdokument",
        "description": "Geräte- oder Anlagenqualifizierung (IQ/OQ/PQ)",
        "gxp_relevant": True,
        "requires_qp_approval": True,
        "default_review_period_months": 36,
        "category": "Quality"
    },
    {
        "code": "RISK",
        "name": "Risk Assessment",
        "name_de": "Risikobewertung",
        "description": "Risikobewertung und -management Dokumentation",
        "gxp_relevant": True,
        "requires_qp_approval": False,
        "default_review_period_months": 24,
        "category": "Quality"
    },
]

# Templates for all document types
TEMPLATES = [
    # SOP Template
    {
        "document_type_code": "SOP",
        "name": "Standard SOP Vorlage",
        "description": "Standardvorlage für Standardarbeitsanweisungen",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "purpose", "title": "1. Zweck", "required": True, "default_content": "Diese SOP beschreibt das Verfahren für..."},
                {"id": "scope", "title": "2. Geltungsbereich", "required": True, "default_content": "Diese SOP gilt für alle Mitarbeiter der Abteilung..."},
                {"id": "responsibilities", "title": "3. Verantwortlichkeiten", "required": True, "default_content": "- Abteilungsleiter: Genehmigung und Überwachung\n- Mitarbeiter: Durchführung gemäß SOP"},
                {"id": "definitions", "title": "4. Definitionen und Abkürzungen", "required": False, "default_content": ""},
                {"id": "procedure", "title": "5. Verfahren", "required": True, "default_content": "5.1 Vorbereitung\n\n5.2 Durchführung\n\n5.3 Dokumentation"},
                {"id": "records", "title": "6. Aufzeichnungen", "required": True, "default_content": "Folgende Aufzeichnungen sind zu führen:"},
                {"id": "references", "title": "7. Referenzen", "required": False, "default_content": ""},
                {"id": "attachments", "title": "8. Anlagen", "required": False, "default_content": ""},
                {"id": "history", "title": "9. Dokumentenhistorie", "required": True, "default_content": "| Version | Datum | Änderung | Autor |\n|---------|-------|----------|-------|"}
            ]
        },
        "default_title_pattern": "SOP: {{process_name}}",
        "default_document_id_pattern": "{{dept}}-SOP-{{number}}"
    },
    # Work Instruction Template
    {
        "document_type_code": "WI",
        "name": "Arbeitsanweisung Vorlage",
        "description": "Standardvorlage für Arbeitsanweisungen",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "purpose", "title": "1. Zweck", "required": True, "default_content": ""},
                {"id": "scope", "title": "2. Geltungsbereich", "required": True, "default_content": ""},
                {"id": "materials", "title": "3. Materialien und Geräte", "required": True, "default_content": "- Material 1\n- Gerät 1"},
                {"id": "safety", "title": "4. Sicherheitshinweise", "required": True, "default_content": "⚠️ Persönliche Schutzausrüstung tragen"},
                {"id": "procedure", "title": "5. Durchführung", "required": True, "default_content": "Schritt 1:\nSchritt 2:\nSchritt 3:"},
                {"id": "records", "title": "6. Aufzeichnungen", "required": True, "default_content": ""}
            ]
        },
        "default_title_pattern": "AA: {{task_name}}",
        "default_document_id_pattern": "{{dept}}-AA-{{number}}"
    },
    # Specification Template
    {
        "document_type_code": "SPEC",
        "name": "Spezifikation Vorlage",
        "description": "Vorlage für Produkt- und Materialspezifikationen",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "product_info", "title": "1. Produktinformationen", "required": True, "default_content": "Produktname:\nChargennummer:\nHerstelldatum:"},
                {"id": "description", "title": "2. Beschreibung", "required": True, "default_content": "Aussehen:\nFarbe:\nGeruch:"},
                {"id": "composition", "title": "3. Zusammensetzung", "required": True, "default_content": "| Bestandteil | Menge | Einheit |\n|-------------|-------|---------|"},
                {"id": "tests", "title": "4. Prüfungen", "required": True, "default_content": "| Prüfung | Methode | Grenzwert |\n|---------|---------|-----------|"},
                {"id": "storage", "title": "5. Lagerung", "required": True, "default_content": "Lagerbedingungen:\nTemperatur:\nLuftfeuchtigkeit:"},
                {"id": "shelf_life", "title": "6. Haltbarkeit", "required": True, "default_content": "Haltbarkeit: XX Monate"}
            ]
        },
        "default_title_pattern": "SPEC: {{product_name}}",
        "default_document_id_pattern": "QA-SPEC-{{number}}"
    },
    # Master Batch Record Template
    {
        "document_type_code": "MBR",
        "name": "Herstellungsanweisung Vorlage",
        "description": "Vorlage für Muster-Herstellungsanweisungen",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "header", "title": "1. Kopfdaten", "required": True, "default_content": "Produkt:\nChargengröße:\nVersion:"},
                {"id": "materials", "title": "2. Ausgangsmaterialien", "required": True, "default_content": "| Material | Menge | Einheit | Chargennr. |\n|----------|-------|---------|------------|"},
                {"id": "equipment", "title": "3. Geräte und Anlagen", "required": True, "default_content": "| Gerät | ID | Status |\n|-------|----|---------"},
                {"id": "production_steps", "title": "4. Herstellungsschritte", "required": True, "default_content": "Schritt 1:\nSchritt 2:"},
                {"id": "ipc", "title": "5. In-Prozess-Kontrollen", "required": True, "default_content": "| IPC | Grenzwert | Ergebnis | Visum |\n|-----|-----------|----------|-------|"},
                {"id": "packaging", "title": "6. Verpackung", "required": True, "default_content": ""},
                {"id": "yields", "title": "7. Ausbeuten", "required": True, "default_content": "Theoretische Ausbeute:\nTatsächliche Ausbeute:\nAusbeute %:"},
                {"id": "release", "title": "8. Freigabe", "required": True, "default_content": "QA Freigabe:\nQP Freigabe:"}
            ]
        },
        "default_title_pattern": "MBR: {{product_name}}",
        "default_document_id_pattern": "PROD-MBR-{{number}}"
    },
    # Fachinformation Template
    {
        "document_type_code": "FI",
        "name": "Fachinformation Vorlage",
        "description": "Vorlage für Fachinformationen (SmPC)",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "name", "title": "1. Bezeichnung des Arzneimittels", "required": True, "default_content": ""},
                {"id": "composition", "title": "2. Qualitative und quantitative Zusammensetzung", "required": True, "default_content": "Wirkstoff(e):\nSonstige Bestandteile:"},
                {"id": "form", "title": "3. Darreichungsform", "required": True, "default_content": ""},
                {"id": "clinical", "title": "4. Klinische Angaben", "required": True, "default_content": "4.1 Anwendungsgebiete\n4.2 Dosierung\n4.3 Gegenanzeigen\n4.4 Warnhinweise\n4.5 Wechselwirkungen\n4.6 Schwangerschaft\n4.7 Fahrtüchtigkeit\n4.8 Nebenwirkungen\n4.9 Überdosierung"},
                {"id": "pharma", "title": "5. Pharmakologische Eigenschaften", "required": True, "default_content": "5.1 Pharmakodynamik\n5.2 Pharmakokinetik"},
                {"id": "pharma_data", "title": "6. Pharmazeutische Angaben", "required": True, "default_content": "6.1 Hilfsstoffe\n6.2 Inkompatibilitäten\n6.3 Haltbarkeit\n6.4 Lagerung\n6.5 Packungsgrößen"},
                {"id": "holder", "title": "7. Inhaber der Zulassung", "required": True, "default_content": "Dyckerhoff Pharma GmbH & Co. KG\nKöln, Deutschland"},
                {"id": "approval", "title": "8. Zulassungsnummer", "required": True, "default_content": ""},
                {"id": "date", "title": "9. Stand der Information", "required": True, "default_content": ""}
            ]
        },
        "default_title_pattern": "FI: {{product_name}}",
        "default_document_id_pattern": "RA-FI-{{number}}"
    },
    # Gebrauchsinformation Template
    {
        "document_type_code": "GI",
        "name": "Gebrauchsinformation Vorlage",
        "description": "Vorlage für Packungsbeilagen (PIL)",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "header", "title": "Gebrauchsinformation: Information für Patienten", "required": True, "default_content": "Lesen Sie die gesamte Packungsbeilage sorgfältig durch, bevor Sie mit der Einnahme dieses Arzneimittels beginnen."},
                {"id": "what_is", "title": "1. Was ist {{product}} und wofür wird es angewendet?", "required": True, "default_content": ""},
                {"id": "before", "title": "2. Was sollten Sie vor der Einnahme beachten?", "required": True, "default_content": "Nehmen Sie {{product}} nicht ein, wenn...\nWarnhinweise und Vorsichtsmaßnahmen:"},
                {"id": "how", "title": "3. Wie ist {{product}} einzunehmen?", "required": True, "default_content": "Dosierung:\nArt der Anwendung:"},
                {"id": "side_effects", "title": "4. Welche Nebenwirkungen sind möglich?", "required": True, "default_content": "Wie alle Arzneimittel kann auch dieses Arzneimittel Nebenwirkungen haben."},
                {"id": "storage", "title": "5. Wie ist {{product}} aufzubewahren?", "required": True, "default_content": "Für Kinder unzugänglich aufbewahren.\nLagertemperatur:"},
                {"id": "contents", "title": "6. Inhalt der Packung und weitere Informationen", "required": True, "default_content": "Was {{product}} enthält:\nWie {{product}} aussieht:\nPharmazeutischer Unternehmer:"}
            ]
        },
        "default_title_pattern": "GI: {{product_name}}",
        "default_document_id_pattern": "RA-GI-{{number}}"
    },
    # Test Instruction Template
    {
        "document_type_code": "TEST",
        "name": "Prüfanweisung Vorlage",
        "description": "Vorlage für analytische Prüfanweisungen",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "purpose", "title": "1. Zweck und Anwendungsbereich", "required": True, "default_content": ""},
                {"id": "principle", "title": "2. Prinzip der Methode", "required": True, "default_content": ""},
                {"id": "equipment", "title": "3. Geräte und Materialien", "required": True, "default_content": "3.1 Geräte\n3.2 Reagenzien\n3.3 Referenzsubstanzen"},
                {"id": "sample", "title": "4. Probenvorbereitung", "required": True, "default_content": ""},
                {"id": "procedure", "title": "5. Durchführung", "required": True, "default_content": ""},
                {"id": "calculation", "title": "6. Berechnung und Auswertung", "required": True, "default_content": ""},
                {"id": "acceptance", "title": "7. Akzeptanzkriterien", "required": True, "default_content": ""},
                {"id": "documentation", "title": "8. Dokumentation", "required": True, "default_content": ""}
            ]
        },
        "default_title_pattern": "PA: {{test_name}}",
        "default_document_id_pattern": "QC-PA-{{number}}"
    },
    # Deviation Report Template
    {
        "document_type_code": "DEV",
        "name": "Abweichungsbericht Vorlage",
        "description": "Vorlage für Abweichungsberichte",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "info", "title": "1. Allgemeine Informationen", "required": True, "default_content": "Abweichungs-Nr.:\nEntdeckungsdatum:\nMelder:"},
                {"id": "description", "title": "2. Beschreibung der Abweichung", "required": True, "default_content": "Was ist passiert?\nWann ist es passiert?\nWo ist es passiert?"},
                {"id": "impact", "title": "3. Auswirkungsbeurteilung", "required": True, "default_content": "Betroffene Chargen:\nBetroffene Produkte:\nRisikoeinschätzung:"},
                {"id": "root_cause", "title": "4. Ursachenanalyse", "required": True, "default_content": "Ermittelte Ursache:"},
                {"id": "actions", "title": "5. Sofortmaßnahmen", "required": True, "default_content": "Durchgeführte Maßnahmen:"},
                {"id": "capa", "title": "6. CAPA-Referenz", "required": False, "default_content": "CAPA erforderlich: Ja/Nein\nCAPA-Nr.:"},
                {"id": "approval", "title": "7. Genehmigung und Abschluss", "required": True, "default_content": "QA Review:\nAbschlussdatum:"}
            ]
        },
        "default_title_pattern": "DEV: {{deviation_title}}",
        "default_document_id_pattern": "QA-DEV-{{number}}"
    },
    # CAPA Template
    {
        "document_type_code": "CAPA",
        "name": "CAPA-Bericht Vorlage",
        "description": "Vorlage für Korrektur- und Vorbeugemaßnahmen",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "info", "title": "1. CAPA-Informationen", "required": True, "default_content": "CAPA-Nr.:\nInitiator:\nDatum:"},
                {"id": "source", "title": "2. Quelle/Auslöser", "required": True, "default_content": "Art: [ ] Abweichung [ ] Beschwerde [ ] Audit [ ] Trend\nReferenz-Nr.:"},
                {"id": "description", "title": "3. Problembeschreibung", "required": True, "default_content": ""},
                {"id": "investigation", "title": "4. Untersuchung und Ursachenanalyse", "required": True, "default_content": "Methode: [ ] 5-Why [ ] Ishikawa [ ] Andere\nErgebnis:"},
                {"id": "corrective", "title": "5. Korrekturmaßnahmen", "required": True, "default_content": "| Maßnahme | Verantwortlich | Termin | Status |"},
                {"id": "preventive", "title": "6. Vorbeugemaßnahmen", "required": True, "default_content": "| Maßnahme | Verantwortlich | Termin | Status |"},
                {"id": "effectiveness", "title": "7. Wirksamkeitsprüfung", "required": True, "default_content": "Prüfungsmethode:\nPrüfungsdatum:\nErgebnis:"},
                {"id": "closure", "title": "8. Abschluss", "required": True, "default_content": "QA Genehmigung:\nAbschlussdatum:"}
            ]
        },
        "default_title_pattern": "CAPA: {{capa_title}}",
        "default_document_id_pattern": "QA-CAPA-{{number}}"
    },
    # Change Control Template
    {
        "document_type_code": "CC",
        "name": "Änderungskontrolle Vorlage",
        "description": "Vorlage für Änderungskontrollen",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "info", "title": "1. Änderungsantrag", "required": True, "default_content": "CC-Nr.:\nAntragsteller:\nDatum:"},
                {"id": "description", "title": "2. Beschreibung der Änderung", "required": True, "default_content": "Ist-Zustand:\nSoll-Zustand:\nBegründung:"},
                {"id": "classification", "title": "3. Klassifizierung", "required": True, "default_content": "Typ: [ ] Minor [ ] Major [ ] Kritisch\nGxP-Relevant: [ ] Ja [ ] Nein"},
                {"id": "impact", "title": "4. Auswirkungsanalyse", "required": True, "default_content": "Betroffene Bereiche:\nBetroffene Dokumente:\nRegulatorische Auswirkungen:"},
                {"id": "plan", "title": "5. Umsetzungsplan", "required": True, "default_content": "| Aktivität | Verantwortlich | Termin |"},
                {"id": "approval", "title": "6. Genehmigungen", "required": True, "default_content": "Abteilungsleiter:\nQA:\nRA (falls erforderlich):\nQP (falls erforderlich):"},
                {"id": "implementation", "title": "7. Umsetzung und Abschluss", "required": True, "default_content": "Umsetzungsdatum:\nVerifizierung:\nAbschluss QA:"}
            ]
        },
        "default_title_pattern": "CC: {{change_title}}",
        "default_document_id_pattern": "QA-CC-{{number}}"
    },
    # Validation Document Template
    {
        "document_type_code": "VAL",
        "name": "Validierungsdokument Vorlage",
        "description": "Vorlage für Validierungsdokumente",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "purpose", "title": "1. Zweck und Geltungsbereich", "required": True, "default_content": ""},
                {"id": "description", "title": "2. System-/Prozessbeschreibung", "required": True, "default_content": ""},
                {"id": "acceptance", "title": "3. Akzeptanzkriterien", "required": True, "default_content": ""},
                {"id": "test_plan", "title": "4. Prüfplan", "required": True, "default_content": "| Test-ID | Beschreibung | Akzeptanzkriterium |"},
                {"id": "results", "title": "5. Ergebnisse", "required": True, "default_content": "| Test-ID | Ergebnis | Bestanden |"},
                {"id": "deviations", "title": "6. Abweichungen", "required": False, "default_content": ""},
                {"id": "conclusion", "title": "7. Schlussfolgerung", "required": True, "default_content": ""},
                {"id": "approval", "title": "8. Genehmigung", "required": True, "default_content": "Autor:\nQA:\nQP (falls erforderlich):"}
            ]
        },
        "default_title_pattern": "VAL: {{validation_subject}}",
        "default_document_id_pattern": "QA-VAL-{{number}}"
    },
    # Risk Assessment Template
    {
        "document_type_code": "RISK",
        "name": "Risikobewertung Vorlage",
        "description": "Vorlage für Risikobewertungen",
        "language": "DE",
        "structure_definition": {
            "sections": [
                {"id": "scope", "title": "1. Geltungsbereich", "required": True, "default_content": ""},
                {"id": "methodology", "title": "2. Methodik", "required": True, "default_content": "Angewandte Methode: [ ] FMEA [ ] HACCP [ ] Andere"},
                {"id": "hazards", "title": "3. Identifizierte Risiken", "required": True, "default_content": "| ID | Gefährdung | Auswirkung | W | S | RPN |"},
                {"id": "controls", "title": "4. Kontrollmaßnahmen", "required": True, "default_content": "| Risiko-ID | Maßnahme | Verantwortlich |"},
                {"id": "residual", "title": "5. Restrisikobewertung", "required": True, "default_content": ""},
                {"id": "conclusion", "title": "6. Schlussfolgerung", "required": True, "default_content": "Das Restrisiko ist akzeptabel: [ ] Ja [ ] Nein"},
                {"id": "review", "title": "7. Überprüfung", "required": True, "default_content": "Nächste Überprüfung:"}
            ]
        },
        "default_title_pattern": "RISK: {{risk_subject}}",
        "default_document_id_pattern": "QA-RISK-{{number}}"
    },
]

# Sample documents to create
SAMPLE_DOCUMENTS = [
    # SOPs
    {
        "title": "SOP: Herstellung von Natriumperchlorat Tropfen",
        "document_id": "PROD-SOP-001",
        "document_type_code": "SOP",
        "department": "Production",
        "product_short_name": "Natriumperchlorat 300 mg/ml",
        "status": DocumentStatus.EFFECTIVE,
        "content": {
            "purpose": "Diese SOP beschreibt das Verfahren zur Herstellung von Natriumperchlorat Dyckerhoff 300 mg/ml Tropfen zum Einnehmen.",
            "scope": "Diese SOP gilt für alle Mitarbeiter der Herstellungsabteilung, die an der Produktion von Natriumperchlorat Tropfen beteiligt sind.",
            "responsibilities": "- Herstellungsleiter: Genehmigung und Überwachung der Herstellung\n- Produktionsmitarbeiter: Durchführung gemäß SOP\n- QA: Freigabe der Charge",
            "definitions": "- WFI: Water for Injection\n- IPC: In-Process Control",
            "procedure": "5.1 Vorbereitung\n- Reinraum vorbereiten\n- Materialien bereitstellen\n\n5.2 Herstellung\n- Natriumperchlorat einwiegen\n- In WFI lösen\n- pH-Wert einstellen\n\n5.3 Abfüllung\n- In Braunglas-Tropfflaschen abfüllen\n- Verschließen und etikettieren",
            "records": "- Chargenprotokoll\n- IPC-Ergebnisse\n- Wiegeprotokolle",
            "references": "- Ph. Eur. Monographie\n- Zulassungsdokumentation",
            "history": "| Version | Datum | Änderung | Autor |\n|---------|-------|----------|-------|\n| 1.0 | 2024-01-15 | Erstversion | Dr. Schmidt |"
        }
    },
    {
        "title": "SOP: Reinigung von Produktionsanlagen",
        "document_id": "PROD-SOP-002",
        "document_type_code": "SOP",
        "department": "Production",
        "product_short_name": None,
        "status": DocumentStatus.EFFECTIVE,
        "content": {
            "purpose": "Diese SOP beschreibt die Reinigungsverfahren für Produktionsanlagen.",
            "scope": "Gilt für alle Produktionsanlagen in der Herstellung.",
            "responsibilities": "- Produktionsmitarbeiter: Durchführung der Reinigung\n- QA: Überprüfung",
            "procedure": "5.1 Vorreinigung mit Wasser\n5.2 Reinigung mit alkalischem Reiniger\n5.3 Spülung mit gereinigtem Wasser\n5.4 Finale Spülung mit WFI\n5.5 Trocknung",
            "records": "- Reinigungsprotokoll\n- Visuelle Inspektion",
            "history": "| 1.0 | 2024-01-10 | Erstversion | Wagner |"
        }
    },
    # Specifications
    {
        "title": "Spezifikation: Natriumperchlorat Rohstoff",
        "document_id": "QA-SPEC-001",
        "document_type_code": "SPEC",
        "department": "QA",
        "product_short_name": "Natriumperchlorat 300 mg/ml",
        "status": DocumentStatus.EFFECTIVE,
        "content": {
            "product_info": "Produktname: Natriumperchlorat\nCAS-Nr.: 7601-89-0\nPh. Eur. Monographie: Ja",
            "description": "Aussehen: Weißes, kristallines Pulver\nGeruch: Geruchlos",
            "composition": "NaClO4 ≥ 99,0%",
            "tests": "| Prüfung | Methode | Grenzwert |\n|---------|---------|-----------|---\n| Gehalt | Ph. Eur. | 99,0 - 101,0% |\n| Chlorid | Ph. Eur. | ≤ 150 ppm |\n| Schwermetalle | Ph. Eur. | ≤ 10 ppm |",
            "storage": "Trocken lagern, vor Licht schützen\nTemperatur: 15-25°C",
            "shelf_life": "Haltbarkeit: 36 Monate"
        }
    },
    {
        "title": "Spezifikation: B1-ASmedic 100 mg Tabletten",
        "document_id": "QA-SPEC-002",
        "document_type_code": "SPEC",
        "department": "QA",
        "product_short_name": "B1-ASmedic",
        "status": DocumentStatus.EFFECTIVE,
        "content": {
            "product_info": "Produktname: B1-ASmedic 100 mg Tabletten\nWirkstoff: Thiaminnitrat",
            "description": "Aussehen: Weiße bis cremefarbene Tabletten\nForm: Rund, bikonvex",
            "composition": "| Bestandteil | Menge pro Tablette |\n|-------------|--------------------|\n| Thiaminnitrat | 100 mg |\n| Lactose | q.s. |",
            "tests": "| Prüfung | Grenzwert |\n|---------|-----------|---\n| Gehalt | 95,0 - 105,0% |\n| Zerfall | ≤ 15 min |\n| Gleichförmigkeit | AV ≤ 15 |",
            "storage": "Vor Feuchtigkeit schützen\nTemperatur: max. 25°C",
            "shelf_life": "Haltbarkeit: 24 Monate"
        }
    },
    # Fachinformation
    {
        "title": "Fachinformation: Natriumperchlorat Dyckerhoff 300 mg/ml",
        "document_id": "RA-FI-001",
        "document_type_code": "FI",
        "department": "Regulatory Affairs",
        "product_short_name": "Natriumperchlorat 300 mg/ml",
        "status": DocumentStatus.EFFECTIVE,
        "content": {
            "name": "Natriumperchlorat Dyckerhoff 300 mg/ml Tropfen zum Einnehmen",
            "composition": "1 ml Lösung enthält 300 mg Natriumperchlorat.\nSonstige Bestandteile: Gereinigtes Wasser",
            "form": "Tropfen zum Einnehmen\nKlare, farblose Lösung",
            "clinical": "4.1 Anwendungsgebiete\nZur Blockade der Schilddrüse vor diagnostischen oder therapeutischen Maßnahmen mit radioaktivem Jod.\n\n4.2 Dosierung\nErwachsene: 3 x täglich 15-20 Tropfen\n\n4.3 Gegenanzeigen\nÜberempfindlichkeit gegen den Wirkstoff",
            "pharma": "5.1 Pharmakodynamik\nNatriumperchlorat hemmt kompetitiv die Jodidaufnahme in die Schilddrüse.",
            "pharma_data": "6.1 Hilfsstoffe: Gereinigtes Wasser\n6.3 Haltbarkeit: 3 Jahre\n6.4 Lagerung: Nicht über 25°C lagern",
            "holder": "Dyckerhoff Pharma GmbH & Co. KG\n50933 Köln",
            "approval": "6180580.00.00",
            "date": "Januar 2024"
        }
    },
    # Gebrauchsinformation
    {
        "title": "Gebrauchsinformation: Natriumperchlorat Dyckerhoff 300 mg/ml",
        "document_id": "RA-GI-001",
        "document_type_code": "GI",
        "department": "Regulatory Affairs",
        "product_short_name": "Natriumperchlorat 300 mg/ml",
        "status": DocumentStatus.EFFECTIVE,
        "content": {
            "header": "Gebrauchsinformation: Information für Patienten\n\nNatriumperchlorat Dyckerhoff 300 mg/ml Tropfen zum Einnehmen\n\nLesen Sie die gesamte Packungsbeilage sorgfältig durch.",
            "what_is": "Natriumperchlorat Dyckerhoff ist ein Arzneimittel zur Blockade der Jodaufnahme in die Schilddrüse.\n\nEs wird angewendet vor Untersuchungen oder Behandlungen mit radioaktivem Jod.",
            "before": "Nehmen Sie Natriumperchlorat Dyckerhoff nicht ein, wenn Sie allergisch gegen Natriumperchlorat sind.",
            "how": "Dosierung:\nErwachsene: 3 x täglich 15-20 Tropfen\n\nArt der Anwendung:\nZum Einnehmen. Die Tropfen in etwas Wasser geben.",
            "side_effects": "Wie alle Arzneimittel kann auch dieses Arzneimittel Nebenwirkungen haben.\n\nSelten: Hautausschlag, Magen-Darm-Beschwerden",
            "storage": "Für Kinder unzugänglich aufbewahren.\nNicht über 25°C lagern.\nIn der Originalverpackung aufbewahren.",
            "contents": "Was Natriumperchlorat Dyckerhoff enthält:\n- Der Wirkstoff ist: Natriumperchlorat 300 mg/ml\n- Der sonstige Bestandteil ist: Gereinigtes Wasser\n\nPharmazeutischer Unternehmer:\nDyckerhoff Pharma GmbH & Co. KG, Köln"
        }
    },
    # Master Batch Record
    {
        "title": "MBR: B12-ASmedic Ampullen Chargengröße 10.000",
        "document_id": "PROD-MBR-001",
        "document_type_code": "MBR",
        "department": "Production",
        "product_short_name": "B12-ASmedic Ampullen",
        "status": DocumentStatus.EFFECTIVE,
        "content": {
            "header": "Produkt: B12-ASmedic 1 mg/1 ml Injektionslösung\nChargengröße: 10.000 Ampullen\nVersion: 1.0",
            "materials": "| Material | Menge | Einheit |\n|----------|-------|---------|---\n| Cyanocobalamin | 10,0 | g |\n| Natriumchlorid | 90,0 | g |\n| WFI | ad 10 | L |",
            "equipment": "| Gerät | ID |\n|-------|----|\n| Ansatzkessel | AK-001 |\n| Sterilfilter | SF-001 |\n| Ampullenfüllanlage | AF-001 |",
            "production_steps": "1. WFI vorlegen\n2. Natriumchlorid lösen\n3. Cyanocobalamin zugeben\n4. Auf 10 L auffüllen\n5. Sterilfiltration\n6. Ampullen füllen\n7. Ampullen verschmelzen",
            "ipc": "| IPC | Grenzwert |\n|-----|-----------|---\n| pH-Wert | 4,5-7,0 |\n| Füllmenge | 1,0-1,1 ml |\n| Dichtheit | 100% dicht |",
            "packaging": "1 ml Braunglas-Ampullen\n5 Ampullen pro Tray\n10 Trays pro Karton",
            "yields": "Theoretische Ausbeute: 10.000 Ampullen\nAkzeptabler Bereich: 95-100%",
            "release": "QA Freigabe: _______________\nQP Freigabe: _______________"
        }
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

        print("Seeding database with Dyckerhoff Pharma data...")

        # Create users
        print("\n📁 Creating users...")
        user_map = {}
        for user_data in USERS:
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                department=user_data["department"]
            )
            session.add(user)
            await session.flush()
            user_map[user_data["email"]] = user.id
        await session.commit()
        print(f"  ✓ Created {len(USERS)} users")

        # Create products
        print("\n📦 Creating products...")
        product_map = {}
        for product_data in PRODUCTS:
            product = Product(**product_data)
            session.add(product)
            await session.flush()
            product_map[product_data["short_name"]] = product.id
        await session.commit()
        print(f"  ✓ Created {len(PRODUCTS)} products")

        # Create document types
        print("\n📑 Creating document types...")
        doc_type_map = {}
        for dt_data in DOCUMENT_TYPES:
            doc_type = DocumentType(**dt_data)
            session.add(doc_type)
            await session.flush()
            doc_type_map[dt_data["code"]] = doc_type.id
        await session.commit()
        print(f"  ✓ Created {len(DOCUMENT_TYPES)} document types")

        # Create templates
        print("\n📝 Creating templates...")
        for tmpl_data in TEMPLATES:
            code = tmpl_data.pop("document_type_code")
            template = Template(
                document_type_id=doc_type_map[code],
                **tmpl_data
            )
            session.add(template)
        await session.commit()
        print(f"  ✓ Created {len(TEMPLATES)} templates")

        # Create sample documents
        print("\n📄 Creating sample documents...")
        admin_id = user_map["admin@pharma-dms.de"]
        author_id = user_map["author@pharma-dms.de"]

        for doc_data in SAMPLE_DOCUMENTS:
            # Create document
            doc = Document(
                document_id=doc_data["document_id"],
                title=doc_data["title"],
                document_type_id=doc_type_map[doc_data["document_type_code"]],
                department=doc_data["department"],
                owner_id=author_id,
                status=doc_data["status"],
                effective_date=datetime.now() if doc_data["status"] == DocumentStatus.EFFECTIVE else None,
                review_date=datetime.now() + timedelta(days=730) if doc_data["status"] == DocumentStatus.EFFECTIVE else None,
            )
            session.add(doc)
            await session.flush()

            # Create version
            version = DocumentVersion(
                document_id=doc.id,
                version_number="1.0",
                content=json.dumps(doc_data["content"], ensure_ascii=False),
                change_reason="Erstversion",
                created_by_id=author_id,
                is_current=True,
            )
            session.add(version)

            # Link to product if specified
            if doc_data.get("product_short_name"):
                product_id = product_map.get(doc_data["product_short_name"])
                if product_id:
                    link = DocumentProductLink(
                        document_id=doc.id,
                        product_id=product_id
                    )
                    session.add(link)

        await session.commit()
        print(f"  ✓ Created {len(SAMPLE_DOCUMENTS)} sample documents")

        print("\n" + "="*50)
        print("✅ Database seeding completed successfully!")
        print("="*50)
        print("\n👥 Test users created:")
        for user in USERS:
            print(f"  - {user['email']} / {user['password']} ({user['role'].value})")
        print("\n📦 Products created:")
        for product in PRODUCTS:
            print(f"  - {product['short_name']}")
        print("\n📄 Document types created:")
        for dt in DOCUMENT_TYPES:
            print(f"  - {dt['code']}: {dt['name_de']}")


if __name__ == "__main__":
    asyncio.run(seed_database())

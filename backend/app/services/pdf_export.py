"""
PDF Export Service for Pharma DMS.

Generates professional PDF documents from document content.
"""
import io
import json
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class PharmaPDFGenerator:
    """Generate professional PDF documents for pharmaceutical documentation."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for pharma documents."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='DocTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#1e40af'),
            alignment=TA_CENTER,
        ))

        # Document ID style
        self.styles.add(ParagraphStyle(
            name='DocID',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=TA_CENTER,
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=16,
            spaceAfter=8,
            textColor=colors.HexColor('#1e3a8a'),
            borderWidth=0,
            borderColor=colors.HexColor('#3b82f6'),
            borderPadding=4,
        ))

        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14,
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER,
        ))

        # Header info style
        self.styles.add(ParagraphStyle(
            name='HeaderInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
        ))

    def generate_document_pdf(
        self,
        document_id: str,
        title: str,
        document_type: str,
        department: str,
        version: str,
        status: str,
        owner: str,
        effective_date: Optional[datetime],
        review_date: Optional[datetime],
        content: dict,
        created_at: datetime,
    ) -> bytes:
        """Generate a PDF for a document."""
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm,
        )

        story = []

        # Header with company info
        header_data = [
            ['Dyckerhoff Pharma GmbH & Co. KG', f'Dokument-ID: {document_id}'],
            ['Dokumentenmanagementsystem', f'Version: {version}'],
            ['', f'Status: {status}'],
        ]
        header_table = Table(header_data, colWidths=[9*cm, 7*cm])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(header_table)

        # Horizontal line
        story.append(Spacer(1, 6))
        story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#3b82f6'),
            spaceBefore=0,
            spaceAfter=12,
        ))

        # Document title
        story.append(Paragraph(title, self.styles['DocTitle']))
        story.append(Paragraph(f'{document_type} | {department}', self.styles['DocID']))
        story.append(Spacer(1, 12))

        # Document metadata table
        meta_data = [
            ['Eigentümer:', owner, 'Gültig ab:', effective_date.strftime('%d.%m.%Y') if effective_date else '-'],
            ['Erstellt am:', created_at.strftime('%d.%m.%Y'), 'Nächste Überprüfung:', review_date.strftime('%d.%m.%Y') if review_date else '-'],
        ]
        meta_table = Table(meta_data, colWidths=[3*cm, 5*cm, 4*cm, 4*cm])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 20))

        # Document content sections
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                content = {"content": content}

        if isinstance(content, dict):
            for section_id, section_content in content.items():
                if section_content:
                    # Format section title
                    section_title = section_id.replace('_', ' ').title()
                    story.append(Paragraph(section_title, self.styles['SectionHeader']))

                    # Handle multiline content
                    if isinstance(section_content, str):
                        paragraphs = section_content.split('\n\n')
                        for para in paragraphs:
                            if para.strip():
                                # Check if it's a table (contains |)
                                if '|' in para and para.count('|') > 2:
                                    table_story = self._parse_markdown_table(para)
                                    if table_story:
                                        story.extend(table_story)
                                else:
                                    # Regular paragraph
                                    lines = para.split('\n')
                                    for line in lines:
                                        if line.strip():
                                            story.append(Paragraph(
                                                line.replace('<', '&lt;').replace('>', '&gt;'),
                                                self.styles['BodyText']
                                            ))
                    story.append(Spacer(1, 8))

        # Footer with approval section
        story.append(Spacer(1, 30))
        story.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor('#e2e8f0'),
            spaceBefore=0,
            spaceAfter=12,
        ))

        # Approval signature block
        approval_data = [
            ['Erstellt von:', '_' * 30, 'Datum:', '_' * 15],
            ['Geprüft von:', '_' * 30, 'Datum:', '_' * 15],
            ['Genehmigt von:', '_' * 30, 'Datum:', '_' * 15],
        ]
        approval_table = Table(approval_data, colWidths=[3*cm, 6*cm, 2*cm, 4*cm])
        approval_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(approval_table)

        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)

        buffer.seek(0)
        return buffer.getvalue()

    def _parse_markdown_table(self, table_text: str) -> list:
        """Parse a markdown-style table and convert to ReportLab table."""
        lines = [l.strip() for l in table_text.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            return []

        # Parse rows
        rows = []
        for line in lines:
            if line.startswith('|'):
                line = line[1:]
            if line.endswith('|'):
                line = line[:-1]

            # Skip separator lines
            if set(line.replace('|', '').replace('-', '').replace(' ', '')) == set():
                continue

            cells = [cell.strip() for cell in line.split('|')]
            if cells and any(cells):
                rows.append(cells)

        if not rows:
            return []

        # Determine column widths
        num_cols = max(len(row) for row in rows)
        col_width = 15 * cm / num_cols

        # Create table
        table = Table(rows, colWidths=[col_width] * num_cols)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cbd5e1')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        return [table, Spacer(1, 8)]

    def _add_page_number(self, canvas, doc):
        """Add page number and footer to each page."""
        canvas.saveState()

        # Page number
        page_num = canvas.getPageNumber()
        text = f"Seite {page_num}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        canvas.drawCentredString(A4[0] / 2, 1.5 * cm, text)

        # Confidentiality notice
        canvas.drawCentredString(
            A4[0] / 2,
            1 * cm,
            "VERTRAULICH - Nur für internen Gebrauch | Dyckerhoff Pharma GmbH & Co. KG"
        )

        canvas.restoreState()


# Singleton instance
pdf_generator = PharmaPDFGenerator()

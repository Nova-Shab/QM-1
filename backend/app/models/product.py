"""
Product model for pharmaceutical products.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class DosageForm(str, enum.Enum):
    """Pharmaceutical dosage forms."""
    DROPS = "drops"  # Tropfen
    INJECTION_SOLUTION = "injection_solution"  # Injektionslösung
    TABLET = "tablet"  # Tablette
    AMPOULE = "ampoule"  # Ampulle
    ORAL_SOLUTION = "oral_solution"  # Lösung zum Einnehmen
    CREAM = "cream"  # Creme
    OINTMENT = "ointment"  # Salbe
    CAPSULE = "capsule"  # Kapsel
    POWDER = "powder"  # Pulver
    EXTRACT = "extract"  # Extrakt
    OTHER = "other"


class MarketStatus(str, enum.Enum):
    """Product market status."""
    IN_DEVELOPMENT = "in_development"
    APPROVED = "approved"
    MARKETED = "marketed"
    DISCONTINUED = "discontinued"
    WITHDRAWN = "withdrawn"


class Product(Base):
    """
    Product entity representing pharmaceutical products.

    Examples from a company like Dyckerhoff Pharma:
    - Natriumperchlorat Dyckerhoff 300 mg/ml Tropfen zum Einnehmen
    - Isotone NaCl-Lösung ASmedic
    - B1-ASmedic (Thiamine tablets)
    - B12-ASmedic (ampoules and oral drops)
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    short_name = Column(String(200), nullable=False)
    dosage_form = Column(Enum(DosageForm), nullable=False)
    strength = Column(String(100), nullable=True)  # e.g., "300 mg/ml"
    product_family = Column(String(100), nullable=True)  # e.g., "ASmedic", "Regeneresen"
    market_status = Column(Enum(MarketStatus), default=MarketStatus.IN_DEVELOPMENT)
    country = Column(String(10), default="DE")  # ISO country code
    description = Column(Text, nullable=True)
    ma_number = Column(String(100), nullable=True)  # Marketing Authorization Number
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document_links = relationship("DocumentProductLink", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.short_name}')>"

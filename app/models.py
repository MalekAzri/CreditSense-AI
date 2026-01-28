from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# Tone Analysis Schema (Used in SyntheticEmail)
class Tone(BaseModel):
    seriousness: float = Field(..., ge=0.0, le=1.0, description="Niveau de sérieux (0-1)")
    stress: float = Field(..., ge=0.0, le=1.0, description="Niveau de stress (0-1)")
    urgency: float = Field(..., ge=0.0, le=1.0, description="Niveau d'urgence (0-1)")

# Basic Message Schema (Real Emails)
class Message(BaseModel):
    source: str
    sender: str
    client_id: Optional[str] = None
    timestamp: str
    subject: Optional[str] = None
    content_text: str
    attachments: List[str] = []
    metadata: Dict = {}
    status: str = "raw"
    extracted_data: Optional[Dict] = None

# Synthetic Email Schema (Inherits from Message for consistency)
class SyntheticEmail(Message):
    """
    Structure identique au Message réel, enrichie avec les labels d'entraînement.
    """
    synthetic_id: str
    intent: str
    tone: Tone

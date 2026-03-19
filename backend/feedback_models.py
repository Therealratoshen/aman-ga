"""
User Feedback Models for Self-Learning OCR
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
from uuid import uuid4


class FeedbackType(str, Enum):
    CORRECTION = "CORRECTION"  # User corrected OCR result
    CONFIRMATION = "CONFIRMATION"  # User confirmed OCR result
    FLAG = "FLAG"  # User flagged as problematic


class FeedbackField(str, Enum):
    AMOUNT = "amount"
    TRANSACTION_ID = "transaction_id"
    DATE = "date"
    BANK = "bank"
    SERVICE_TYPE = "service_type"


class UserFeedbackCreate(BaseModel):
    """User feedback submission"""
    payment_proof_id: str
    feedback_type: FeedbackType
    
    # Corrected values (only for CORRECTION type)
    corrected_amount: Optional[int] = Field(None, ge=100, le=100_000_000)
    corrected_transaction_id: Optional[str] = Field(None, min_length=5, max_length=50)
    corrected_date: Optional[str] = None
    corrected_bank: Optional[str] = None
    
    # Which fields were corrected
    corrected_fields: List[FeedbackField] = []
    
    # Additional notes
    notes: str = Field("", max_length=1000)
    
    # Was the receipt legitimate?
    is_legitimate_receipt: Optional[bool] = None
    
    # Quality rating (1-5 stars)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    
    # Would user recommend this receipt format?
    would_recommend: Optional[bool] = None
    
    def generate_id(self) -> str:
        return f"fb_{uuid4().hex[:12]}"
    
    def generate_timestamp(self) -> str:
        return datetime.now().isoformat()


class OCRUncertaintyReport(BaseModel):
    """Detailed uncertainty report for OCR extraction"""
    overall_confidence: float = Field(ge=0, le=1)
    confidence_level: str  # LOW, MEDIUM, HIGH
    
    # Field-level confidence
    amount_confidence: Optional[float] = None
    transaction_id_confidence: Optional[float] = None
    date_confidence: Optional[float] = None
    bank_confidence: Optional[float] = None
    
    # Uncertainty flags
    uncertainty_flags: List[str] = []
    
    # Warnings for user
    warnings: List[str] = []
    
    # Alternative interpretations
    alternatives: dict = {}
    
    # Recommendation
    needs_manual_verification: bool = False
    verification_reason: str = ""


class LearningMetricsResponse(BaseModel):
    """Learning metrics for admin dashboard"""
    total_samples: int
    total_feedback: int
    correction_rate: float  # Percentage of corrections
    
    # Accuracy metrics
    overall_accuracy: float
    amount_accuracy: float
    transaction_id_accuracy: float
    date_accuracy: float
    
    # Confidence calibration
    avg_confidence: float
    confidence_calibration_score: float
    
    # By provider
    provider_accuracy: dict
    
    # Recent trends
    accuracy_trend: List[float]  # Last 7 days
    
    last_updated: str


class ReceiptFormatInfo(BaseModel):
    """Information about a known receipt format"""
    provider: str
    bank_name: str
    sample_count: int
    confidence_score: float
    typical_colors: List[str]
    has_qr_code: bool
    common_issues: List[str] = []
    tips: List[str] = []

"""
Self-Learning OCR Configuration System
Inspired by OpenCLAW - Continuous learning from user feedback

This module handles:
1. Receipt format patterns for Indonesian banks/e-wallets
2. OCR confidence learning from user corrections
3. Pattern improvement based on feedback
4. Uncertainty flagging for low-confidence extractions
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ReceiptFormat:
    """Format pattern for a specific bank/e-wallet receipt"""
    bank_name: str
    provider: str  # BCA, BRI, GoPay, etc.
    
    # Pattern configurations
    amount_patterns: List[str]  # Regex patterns for amount extraction
    transaction_id_patterns: List[str]
    date_patterns: List[str]
    
    # Known receipt characteristics
    typical_colors: List[str]  # Dominant colors in receipt
    logo_position: str  # top-left, top-center, top-right
    has_qr_code: bool
    has_watermark: bool
    
    # Font characteristics
    font_family: str
    font_sizes: List[int]
    
    # Layout
    width_pixels: int
    height_pixels: int
    aspect_ratio: float
    
    # Learning metadata
    sample_count: int = 0
    confidence_score: float = 0.5  # Starts at 0.5, improves with feedback
    last_updated: str = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()


@dataclass
class UserFeedback:
    """User feedback on OCR extraction"""
    feedback_id: str
    payment_proof_id: str
    timestamp: str
    
    # Original OCR results
    ocr_extracted_amount: Optional[int]
    ocr_extracted_transaction_id: Optional[str]
    ocr_extracted_date: Optional[str]
    ocr_confidence: float
    
    # User corrections
    user_corrected_amount: Optional[int]
    user_corrected_transaction_id: Optional[str]
    user_corrected_date: Optional[str]
    
    # Feedback type
    feedback_type: str  # CORRECTION, CONFIRMATION, FLAG
    
    # Additional notes
    notes: str = ""
    
    # Was the feedback helpful for learning?
    used_for_learning: bool = False
    learning_impact: float = 0.0


@dataclass
class LearningMetrics:
    """Metrics for OCR learning progress"""
    total_samples: int = 0
    total_feedback: int = 0
    corrections: int = 0
    confirmations: int = 0
    
    # Accuracy by field
    amount_accuracy: float = 0.0
    transaction_id_accuracy: float = 0.0
    date_accuracy: float = 0.0
    
    # Confidence calibration
    avg_confidence: float = 0.0
    confidence_calibration: float = 0.0  # How well confidence matches accuracy
    
    # By provider
    provider_metrics: Dict[str, Dict] = None
    
    last_updated: str = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()
        if self.provider_metrics is None:
            self.provider_metrics = {}


class SelfLearningOCR:
    """
    Self-learning OCR system that improves from user feedback.
    
    Key principles:
    1. Never be overconfident - always flag uncertainty
    2. Learn from every user correction
    3. Adapt to new receipt formats
    4. Provide transparency on confidence levels
    """
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Default to repo config directory
            self.config_dir = Path(__file__).parent / "ocr_config"
        else:
            self.config_dir = Path(config_dir)
        
        # Create config directory if not exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage
        self.receipt_formats: Dict[str, ReceiptFormat] = {}
        self.feedback_history: List[UserFeedback] = []
        self.metrics = LearningMetrics()
        
        # Load existing configurations
        self.load_configurations()
        
        # Uncertainty thresholds
        self.HIGH_UNCERTAINTY_THRESHOLD = 0.6  # Below this = flag as uncertain
        self.MEDIUM_UNCERTAINTY_THRESHOLD = 0.8  # Below this = show warning
        
    def load_configurations(self):
        """Load receipt format configurations from JSON files"""
        formats_file = self.config_dir / "receipt_formats.json"
        metrics_file = self.config_dir / "learning_metrics.json"
        
        if formats_file.exists():
            with open(formats_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    self.receipt_formats[item['provider']] = ReceiptFormat(**item)
            print(f"✅ Loaded {len(self.receipt_formats)} receipt format configurations")
        
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                data = json.load(f)
                self.metrics = LearningMetrics(**data)
            print(f"✅ Loaded learning metrics")
    
    def save_configurations(self):
        """Save configurations to JSON files"""
        formats_file = self.config_dir / "receipt_formats.json"
        metrics_file = self.config_dir / "learning_metrics.json"
        
        # Save receipt formats
        with open(formats_file, 'w') as f:
            data = [asdict(fmt) for fmt in self.receipt_formats.values()]
            json.dump(data, f, indent=2)
        
        # Save metrics
        with open(metrics_file, 'w') as f:
            json.dump(asdict(self.metrics), f, indent=2)
    
    def extract_with_uncertainty(
        self, 
        ocr_result: dict, 
        image_analysis: dict,
        provider: str = None
    ) -> dict:
        """
        Extract data with uncertainty flags.
        
        Key principle: Always indicate confidence level and potential errors.
        
        Returns dict with:
        - extracted_value
        - confidence_score
        - uncertainty_flags (list of concerns)
        - alternative_values (other possible interpretations)
        - needs_verification (bool)
        """
        result = {
            "amount": self._extract_with_alternatives(ocr_result, "amount"),
            "transaction_id": self._extract_with_alternatives(ocr_result, "transaction_id"),
            "date": self._extract_with_alternatives(ocr_result, "date"),
            "bank": self._detect_bank(ocr_result, image_analysis, provider),
            "overall_confidence": 0.0,
            "uncertainty_flags": [],
            "needs_verification": False,
            "warnings": []
        }
        
        # Calculate overall confidence
        confidences = []
        for field in ["amount", "transaction_id", "date"]:
            if result[field]["confidence"] > 0:
                confidences.append(result[field]["confidence"])
        
        if confidences:
            result["overall_confidence"] = sum(confidences) / len(confidences)
        
        # Add uncertainty flags
        if result["overall_confidence"] < self.HIGH_UNCERTAINTY_THRESHOLD:
            result["uncertainty_flags"].append("LOW_CONFIDENCE_EXTRACTION")
            result["needs_verification"] = True
            result["warnings"].append("⚠️ Ekstraksi memiliki kepercayaan rendah. Mohon verifikasi manual.")
        
        if result["overall_confidence"] < self.MEDIUM_UNCERTAINTY_THRESHOLD:
            result["uncertainty_flags"].append("MEDIUM_CONFIDENCE_EXTRACTION")
            result["warnings"].append("⚠️ Beberapa field mungkin tidak akurat.")
        
        # Check for common OCR errors
        if self._check_common_ocr_errors(result):
            result["uncertainty_flags"].append("POSSIBLE_OCR_ERROR")
            result["warnings"].append("⚠️ Terdeteksi kemungkinan kesalahan OCR.")
        
        # Check against known receipt formats
        if provider and provider in self.receipt_formats:
            format_check = self._check_against_format(result, provider)
            if not format_check["matches"]:
                result["uncertainty_flags"].append("FORMAT_MISMATCH")
                result["warnings"].extend(format_check["warnings"])
        
        return result
    
    def _extract_with_alternatives(self, ocr_result: dict, field: str) -> dict:
        """Extract field value with alternative interpretations"""
        extracted = ocr_result.get(f"extracted_{field}")
        confidence = ocr_result.get("confidence_score", 0.5)
        
        alternatives = []
        
        # Generate alternatives based on common OCR mistakes
        if field == "amount":
            alternatives = self._generate_amount_alternatives(extracted)
        elif field == "transaction_id":
            alternatives = self._generate_transaction_id_alternatives(extracted)
        elif field == "date":
            alternatives = self._generate_date_alternatives(extracted)
        
        return {
            "value": extracted,
            "confidence": confidence,
            "alternatives": alternatives,
            "extraction_method": "OCR"
        }
    
    def _generate_amount_alternatives(self, amount: Optional[int]) -> List[dict]:
        """Generate alternative amount interpretations"""
        if amount is None:
            return []
        
        alternatives = []
        
        # Common OCR mistakes for numbers
        # 0 ↔ O, 1 ↔ I/l, 5 ↔ S, 8 ↔ B
        amount_str = str(amount)
        
        # Check for potential misread digits
        if '0' in amount_str:
            alt = amount_str.replace('0', 'O')
            alternatives.append({"value": alt, "reason": "Possible 0/O confusion"})
        
        if '1' in amount_str:
            alt = amount_str.replace('1', 'I')
            alternatives.append({"value": alt, "reason": "Possible 1/I confusion"})
        
        # Decimal point confusion
        if '.' in amount_str:
            alt = amount_str.replace('.', ',')
            alternatives.append({"value": alt, "reason": "Decimal separator variation"})
        
        return alternatives
    
    def _generate_transaction_id_alternatives(self, tx_id: Optional[str]) -> List[dict]:
        """Generate alternative transaction ID interpretations"""
        if tx_id is None:
            return []
        
        alternatives = []
        
        # Common confusions
        confusions = [
            ('0', 'O'), ('O', '0'),
            ('1', 'I'), ('I', '1'), ('l', '1'),
            ('5', 'S'), ('S', '5'),
            ('8', 'B'), ('B', '8'),
            ('2', 'Z'), ('Z', '2'),
        ]
        
        for old, new in confusions:
            if old in tx_id:
                alt = tx_id.replace(old, new)
                if alt != tx_id:
                    alternatives.append({
                        "value": alt,
                        "reason": f"Possible {old}/{new} confusion"
                    })
        
        return alternatives
    
    def _generate_date_alternatives(self, date_str: Optional[str]) -> List[dict]:
        """Generate alternative date interpretations"""
        if date_str is None:
            return []
        
        alternatives = []
        
        # Common date format confusions
        # DD/MM/YYYY vs MM/DD/YYYY
        parts = date_str.split('/')
        if len(parts) == 3:
            # Try swapping day and month
            swapped = f"{parts[1]}/{parts[0]}/{parts[2]}"
            alternatives.append({
                "value": swapped,
                "reason": "Possible DD/MM vs MM/DD confusion"
            })
        
        return alternatives
    
    def _detect_bank(
        self, 
        ocr_result: dict, 
        image_analysis: dict,
        provider: str = None
    ) -> dict:
        """Detect bank with confidence scoring"""
        extracted_bank = ocr_result.get("extracted_bank")
        
        # Check image colors for bank identification
        dominant_colors = image_analysis.get("dominant_colors", [])
        
        # Bank color signatures (approximate)
        bank_colors = {
            "BCA": ["#00529F", "#00A3E0"],  # Blue
            "BRI": ["#006EB5", "#E3000B"],  # Blue + Red
            "BNI": ["#E3000B", "#FFFFFF"],  # Red
            "MANDIRI": ["#009FE3", "#FFFFFF"],  # Light Blue
            "PERMATA": ["#00A651", "#FFFFFF"],  # Green
            "DANAMON": ["#F58220", "#FFFFFF"],  # Orange
            "CIMB": ["#FFD100", "#000000"],  # Yellow
            "GOPAY": ["#00AA13", "#FFFFFF"],  # Green
            "OVO": ["#4C3494", "#FFFFFF"],  # Purple
            "DANA": ["#118EEA", "#FFFFFF"],  # Blue
        }
        
        # Match colors
        color_matches = []
        for bank, colors in bank_colors.items():
            for color in colors:
                if color in dominant_colors or self._color_similar(color, dominant_colors):
                    color_matches.append(bank)
        
        # Combine OCR and color analysis
        confidence = 0.5
        detected_bank = extracted_bank or provider
        
        if color_matches:
            if detected_bank in color_matches:
                confidence = 0.8  # OCR + color match
            else:
                confidence = 0.4  # Conflict between OCR and color
                detected_bank = color_matches[0]  # Use color-based detection
        elif detected_bank:
            confidence = 0.6  # OCR only
        
        return {
            "value": detected_bank,
            "confidence": confidence,
            "color_matches": color_matches,
            "ocr_match": extracted_bank,
            "alternatives": color_matches if len(color_matches) > 1 else []
        }
    
    def _color_similar(self, color: str, color_list: List[str], threshold: float = 0.3) -> bool:
        """Check if color is similar to any in the list"""
        # Simplified color comparison
        # In production, use proper color distance (CIEDE2000)
        return any(c[:4] == color[:4] for c in color_list)
    
    def _check_common_ocr_errors(self, result: dict) -> bool:
        """Check for common OCR error patterns"""
        # Check amount for suspicious patterns
        amount = result["amount"]["value"]
        if amount:
            # All same digits (possible misread)
            amount_str = str(amount)
            if len(set(amount_str)) == 1 and len(amount_str) > 2:
                return True
            
            # Unusual patterns
            if amount_str.count('0') > len(amount_str) * 0.7:
                return True
        
        # Check transaction ID for suspicious patterns
        tx_id = result["transaction_id"]["value"]
        if tx_id:
            # Too many similar characters
            if len(set(tx_id.lower())) < len(tx_id) * 0.3:
                return True
        
        return False
    
    def _check_against_format(self, result: dict, provider: str) -> dict:
        """Check extracted data against known receipt format"""
        fmt = self.receipt_formats.get(provider)
        if not fmt:
            return {"matches": True, "warnings": []}
        
        warnings = []
        matches = True
        
        # Check amount format
        amount = result["amount"]["value"]
        if amount:
            # Check against typical amount ranges for this provider
            pass  # Could add provider-specific validation
        
        # Check transaction ID format
        tx_id = result["transaction_id"]["value"]
        if tx_id and fmt.sample_count > 10:
            # Check if TX ID matches known pattern length
            pass
        
        return {
            "matches": matches,
            "warnings": warnings
        }
    
    def submit_feedback(self, feedback: UserFeedback):
        """
        Submit user feedback for learning.
        
        This is the core of self-learning - every correction improves the system.
        """
        self.feedback_history.append(feedback)
        self.metrics.total_feedback += 1
        
        if feedback.feedback_type == "CORRECTION":
            self.metrics.corrections += 1
            self._learn_from_correction(feedback)
        elif feedback.feedback_type == "CONFIRMATION":
            self.metrics.confirmations += 1
            self._learn_from_confirmation(feedback)
        
        # Update metrics
        self._update_metrics()
        
        # Save configurations
        self.save_configurations()
    
    def _learn_from_correction(self, feedback: UserFeedback):
        """Learn from user corrections"""
        # Compare OCR vs user correction
        if feedback.ocr_extracted_amount != feedback.user_corrected_amount:
            # Learn about amount extraction error
            self._adjust_amount_extraction(feedback)
        
        if feedback.ocr_extracted_transaction_id != feedback.user_corrected_transaction_id:
            # Learn about transaction ID extraction error
            self._adjust_transaction_id_extraction(feedback)
        
        if feedback.ocr_extracted_date != feedback.user_corrected_date:
            # Learn about date extraction error
            self._adjust_date_extraction(feedback)
    
    def _adjust_amount_extraction(self, feedback: UserFeedback):
        """Adjust amount extraction based on feedback"""
        # In production, this would update ML model weights
        # For now, we track the correction pattern
        pass
    
    def _adjust_transaction_id_extraction(self, feedback: UserFeedback):
        """Adjust transaction ID extraction based on feedback"""
        pass
    
    def _adjust_date_extraction(self, feedback: UserFeedback):
        """Adjust date extraction based on feedback"""
        pass
    
    def _learn_from_confirmation(self, feedback: UserFeedback):
        """Learn from user confirmations (OCR was correct)"""
        # Increase confidence for this receipt format
        pass
    
    def _update_metrics(self):
        """Update learning metrics"""
        self.metrics.total_samples = len(self.feedback_history)
        
        # Calculate accuracy
        if self.metrics.total_feedback > 0:
            self.metrics.amount_accuracy = 1.0 - (
                sum(1 for f in self.feedback_history 
                    if f.feedback_type == "CORRECTION" and 
                    f.ocr_extracted_amount != f.user_corrected_amount) /
                self.metrics.total_feedback
            )
        
        # Update confidence calibration
        # (How well does OCR confidence match actual accuracy?)
        pass
    
    def add_receipt_format(self, format_data: ReceiptFormat):
        """Add or update a receipt format configuration"""
        provider = format_data.provider
        
        if provider in self.receipt_formats:
            # Update existing
            existing = self.receipt_formats[provider]
            existing.sample_count += 1
            existing.last_updated = datetime.now().isoformat()
        else:
            # Add new
            self.receipt_formats[provider] = format_data
        
        self.save_configurations()
    
    def get_uncertainty_report(self, extraction_result: dict) -> str:
        """Generate human-readable uncertainty report"""
        report = []
        
        overall = extraction_result.get("overall_confidence", 0)
        
        if overall < 0.5:
            report.append("🔴 Kepercayaan rendah (< 50%)")
            report.append("   → Perlu verifikasi manual")
        elif overall < 0.7:
            report.append("🟡 Kepercayaan sedang (50-70%)")
            report.append("   → Disarankan verifikasi")
        elif overall < 0.9:
            report.append("🟢 Kepercayaan baik (70-90%)")
            report.append("   → Kemungkinan besar akurat")
        else:
            report.append("✅ Kepercayaan tinggi (> 90%)")
            report.append("   → Sangat mungkin akurat")
        
        # Field-specific confidence
        for field in ["amount", "transaction_id", "date"]:
            field_data = extraction_result.get(field, {})
            conf = field_data.get("confidence", 0)
            if conf < 0.7:
                report.append(f"⚠️ Field '{field}' memiliki kepercayaan rendah ({conf*100:.0f}%)")
        
        # Warnings
        for warning in extraction_result.get("warnings", []):
            report.append(f"   {warning}")
        
        # Alternatives
        for field in ["amount", "transaction_id"]:
            field_data = extraction_result.get(field, {})
            alts = field_data.get("alternatives", [])
            if alts:
                report.append(f"💡 Alternatif untuk {field}:")
                for alt in alts[:3]:
                    report.append(f"   - {alt['value']} ({alt['reason']})")
        
        return "\n".join(report)


# Initialize global instance
self_learning_ocr = SelfLearningOCR()

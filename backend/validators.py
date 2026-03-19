"""
Comprehensive Validation Module for Payment Verification
Handles input validation, file validation, OCR, and image analysis
"""

import re
import hashlib
import io
import magic
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from PIL import Image
import imagehash
import cv2
import numpy as np
import pytesseract
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ServiceType(str, Enum):
    CEK_DASAR = "CEK_DASAR"
    CEK_DEEP = "CEK_DEEP"
    CEK_PLUS = "CEK_PLUS"
    WALLET_TOPUP = "WALLET_TOPUP"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    GOPAY = "GOPAY"
    OVO = "OVO"
    DANA = "DANA"
    LINKAJA = "LINKAJA"


class BankName(str, Enum):
    BCA = "BCA"
    BRI = "BRI"
    BNI = "BNI"
    MANDIRI = "MANDIRI"
    PERMATA = "PERMATA"
    DANAMON = "DANAMON"
    CIMB = "CIMB"
    MAYBANK = "MAYBANK"
    BTN = "BTN"
    OTHER = "OTHER"


class PaymentProofCreate(BaseModel):
    """Validated payment proof data"""
    service_type: ServiceType
    amount: int = Field(ge=100, le=100_000_000, description="Amount must be between Rp 100 and Rp 100,000,000")
    payment_method: PaymentMethod
    bank_name: BankName
    transaction_id: str = Field(min_length=5, max_length=50, description="Transaction ID must be 5-50 characters")
    transaction_date: str
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('transaction_id')
    @classmethod
    def validate_transaction_id(cls, v):
        # Allow alphanumeric, dash, underscore only
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError('Transaction ID can only contain letters, numbers, dash, and underscore')
        # Check for suspicious patterns
        if v.lower() in ['test', 'fake', 'demo', 'sample', 'example']:
            raise ValueError('Invalid transaction ID format')
        return v.upper()
    
    @field_validator('transaction_date')
    @classmethod
    def validate_transaction_date(cls, v):
        try:
            tx_date = datetime.fromisoformat(v.replace('Z', '+00:00'))
            now = datetime.now(tx_date.tzinfo) if tx_date.tzinfo else datetime.now()
            
            # Cannot be in the future (with 1 hour buffer for timezone issues)
            if tx_date > now + timedelta(hours=1):
                raise ValueError('Transaction date cannot be in the future')
            
            # Cannot be too old (max 1 year)
            if tx_date < now - timedelta(days=365):
                raise ValueError('Transaction date too old (max 1 year)')
            
            return v
        except ValueError as e:
            if 'Transaction' in str(e):
                raise
            raise ValueError('Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)')


class FileValidationResult(BaseModel):
    """Result of file validation"""
    is_valid: bool
    error_message: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    image_hash: Optional[str] = None
    mime_type: Optional[str] = None


class OCRResult(BaseModel):
    """OCR extraction result"""
    extracted_text: str
    extracted_amount: Optional[int] = None
    extracted_transaction_id: Optional[str] = None
    extracted_date: Optional[str] = None
    extracted_bank: Optional[str] = None
    confidence_score: float = 0.0
    matches_form: bool = False
    mismatches: List[str] = []


class ImageAnalysisResult(BaseModel):
    """AI image analysis result"""
    is_manipulated: bool = False
    manipulation_confidence: float = 0.0
    manipulation_indicators: List[str] = []
    is_screenshot: bool = True
    quality_score: float = 0.0
    metadata: Dict = {}
    risk_level: str = "LOW"


class ValidationError(Exception):
    """Custom validation error"""
    pass


class PaymentValidator:
    """Main payment validation service"""
    
    # File constraints
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_FILE_SIZE = 10 * 1024  # 10KB
    MIN_IMAGE_WIDTH = 200
    MIN_IMAGE_HEIGHT = 200
    MAX_IMAGE_WIDTH = 10000
    MAX_IMAGE_HEIGHT = 10000
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/png',
        'image/webp',
        'application/pdf'
    }
    
    # Amount thresholds
    AUTO_APPROVE_MAX = 1000
    MIN_PAYMENT = 100
    
    def __init__(self):
        pass
    
    def validate_file(self, file_content: bytes, filename: str) -> FileValidationResult:
        """Comprehensive file validation"""
        
        # Check file size
        file_size = len(file_content)
        if file_size < self.MIN_FILE_SIZE:
            return FileValidationResult(
                is_valid=False,
                error_message=f"File too small. Minimum size is {self.MIN_FILE_SIZE // 1024}KB"
            )
        
        if file_size > self.MAX_FILE_SIZE:
            return FileValidationResult(
                is_valid=False,
                error_message=f"File too large. Maximum size is {self.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Detect actual MIME type (not just extension)
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file_content)
        
        if mime_type not in self.ALLOWED_MIME_TYPES:
            return FileValidationResult(
                is_valid=False,
                error_message=f"File type not allowed. Allowed: JPG, PNG, WebP, PDF. Detected: {mime_type}"
            )
        
        # Reject PDFs (require actual image for analysis)
        if mime_type == 'application/pdf':
            return FileValidationResult(
                is_valid=False,
                error_message="PDF not supported. Please upload a screenshot as JPG or PNG"
            )
        
        # Validate image properties
        try:
            image = Image.open(io.BytesIO(file_content))
            width, height = image.size
            
            if width < self.MIN_IMAGE_WIDTH or height < self.MIN_IMAGE_HEIGHT:
                return FileValidationResult(
                    is_valid=False,
                    error_message=f"Image too small. Minimum dimensions: {self.MIN_IMAGE_WIDTH}x{self.MIN_IMAGE_HEIGHT}px"
                )
            
            if width > self.MAX_IMAGE_WIDTH or height > self.MAX_IMAGE_HEIGHT:
                return FileValidationResult(
                    is_valid=False,
                    error_message=f"Image too large. Maximum dimensions: {self.MAX_IMAGE_WIDTH}x{self.MAX_IMAGE_HEIGHT}px"
                )
            
            # Calculate perceptual hash for duplicate detection
            img_hash = imagehash.phash(image)
            
            return FileValidationResult(
                is_valid=True,
                file_type='image',
                file_size=file_size,
                image_width=width,
                image_height=height,
                image_hash=str(img_hash),
                mime_type=mime_type
            )
            
        except Exception as e:
            return FileValidationResult(
                is_valid=False,
                error_message=f"Invalid image file: {str(e)}"
            )
    
    def validate_payment_data(self, data: dict) -> Tuple[bool, Optional[str], Optional[PaymentProofCreate]]:
        """Validate payment proof data"""
        
        try:
            # Create validated model
            validated = PaymentProofCreate(
                service_type=data.get('service_type'),
                amount=int(data.get('amount', 0)),
                payment_method=data.get('payment_method'),
                bank_name=data.get('bank_name', 'OTHER'),
                transaction_id=data.get('transaction_id', ''),
                transaction_date=data.get('transaction_date'),
                notes=data.get('notes')
            )
            
            # Additional business logic validation
            if validated.service_type == ServiceType.CEK_DASAR and validated.amount > self.AUTO_APPROVE_MAX:
                return False, "CEK_DASAR service limited to maximum Rp 1,000 for auto-approval", None
            
            if validated.amount < self.MIN_PAYMENT:
                return False, f"Minimum payment amount is Rp {self.MIN_PAYMENT}", None
            
            return True, None, validated
            
        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"Validation error: {str(e)}", None
    
    def extract_ocr(self, image_content: bytes) -> OCRResult:
        """Extract text from image using OCR"""
        
        try:
            # Convert to OpenCV format
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Preprocess for better OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Extract text
            custom_config = r'--oem 3 --psm 6 -l eng+ind'
            text = pytesseract.image_to_string(gray, config=custom_config)
            
            # Extract structured data
            extracted_amount = self._extract_amount(text)
            extracted_tx_id = self._extract_transaction_id(text)
            extracted_date = self._extract_date(text)
            extracted_bank = self._extract_bank(text)
            
            # Calculate confidence based on text quality
            confidence = min(1.0, len(text) / 500)  # More text = higher confidence
            
            return OCRResult(
                extracted_text=text,
                extracted_amount=extracted_amount,
                extracted_transaction_id=extracted_tx_id,
                extracted_date=extracted_date,
                extracted_bank=extracted_bank,
                confidence_score=confidence
            )
            
        except Exception as e:
            return OCRResult(
                extracted_text="",
                confidence_score=0.0,
                mismatches=[f"OCR failed: {str(e)}"]
            )
    
    def _extract_amount(self, text: str) -> Optional[int]:
        """Extract amount from OCR text"""
        # Look for patterns like "Rp 1.000.000" or "1.000.000"
        patterns = [
            r'Rp[\s\.]*([\d\.]+)',
            r'IDR[\s\.]*([\d\.]+)',
            r'(\d{1,3}(?:\.\d{3})+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove dots and convert to int
                    amount = int(match.replace('.', ''))
                    if 100 <= amount <= 100_000_000:  # Reasonable range
                        return amount
                except:
                    continue
        return None
    
    def _extract_transaction_id(self, text: str) -> Optional[str]:
        """Extract transaction ID from OCR text"""
        patterns = [
            r'(?:TRX|TXN|REF|No\.\s*Transaksi)[:\s]*([A-Za-z0-9]+)',
            r'(?:Reference|Transaction)\s*(?:ID|Number)[:\s]*([A-Za-z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from OCR text"""
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Dec)[a-z]*\s+\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_bank(self, text: str) -> Optional[str]:
        """Extract bank name from OCR text"""
        banks = ['BCA', 'BRI', 'BNI', 'MANDIRI', 'PERMATA', 'DANAMON', 'CIMB', 'MAYBANK', 'BTN']
        text_upper = text.upper()
        
        for bank in banks:
            if bank in text_upper:
                return bank
        return None
    
    def analyze_image(self, image_content: bytes) -> ImageAnalysisResult:
        """Analyze image for manipulation and authenticity"""
        
        try:
            image = Image.open(io.BytesIO(image_content))
            nparr = np.frombuffer(image_content, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            indicators = []
            manipulation_confidence = 0.0
            
            # 1. Check for ELA (Error Level Analysis) - detects recompression
            ela_result = self._check_ela(img_cv)
            if ela_result['suspicious']:
                indicators.append("Potential image recompression detected")
                manipulation_confidence += ela_result['confidence']
            
            # 2. Check metadata inconsistencies
            metadata_check = self._check_metadata(image)
            if metadata_check['suspicious']:
                indicators.extend(metadata_check['indicators'])
                manipulation_confidence += metadata_check['confidence']
            
            # 3. Check noise pattern consistency
            noise_check = self._check_noise_pattern(img_cv)
            if noise_check['suspicious']:
                indicators.append("Inconsistent noise patterns detected")
                manipulation_confidence += noise_check['confidence']
            
            # 4. Check for copy-move forgery
            copy_move_check = self._check_copy_move(img_cv)
            if copy_move_check['suspicious']:
                indicators.append("Possible copy-move forgery detected")
                manipulation_confidence += copy_move_check['confidence']
            
            # 5. Quality assessment
            quality_score = self._assess_quality(img_cv)
            
            # Determine if screenshot
            is_screenshot = self._is_screenshot(img_cv)
            
            # Calculate final risk level
            if manipulation_confidence >= 0.7:
                risk_level = "CRITICAL"
            elif manipulation_confidence >= 0.5:
                risk_level = "HIGH"
            elif manipulation_confidence >= 0.3:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return ImageAnalysisResult(
                is_manipulated=manipulation_confidence >= 0.5,
                manipulation_confidence=manipulation_confidence,
                manipulation_indicators=indicators,
                is_screenshot=is_screenshot,
                quality_score=quality_score,
                metadata={'width': image.width, 'height': image.height, 'format': image.format},
                risk_level=risk_level
            )
            
        except Exception as e:
            return ImageAnalysisResult(
                is_manipulated=False,
                risk_level="UNKNOWN",
                manipulation_indicators=[f"Analysis failed: {str(e)}"]
            )
    
    def _check_ela(self, img: np.ndarray) -> Dict:
        """Error Level Analysis - detects recompression artifacts"""
        try:
            # Convert to JPEG at 90% quality
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            _, compressed = cv2.imencode('.jpg', img, encode_param)
            decoded = cv2.imdecode(compressed, 1)
            
            # Calculate difference
            diff = cv2.absdiff(img, decoded)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # Check for suspicious patterns
            mean_val = np.mean(diff_gray)
            std_val = np.std(diff_gray)
            
            # High variance in difference might indicate manipulation
            if std_val > 30 and mean_val > 10:
                return {
                    'suspicious': True,
                    'confidence': min(0.5, std_val / 100)
                }
            
            return {'suspicious': False, 'confidence': 0.0}
        except:
            return {'suspicious': False, 'confidence': 0.0}
    
    def _check_metadata(self, image: Image.Image) -> Dict:
        """Check image metadata for inconsistencies"""
        indicators = []
        confidence = 0.0
        
        try:
            info = image.info
            
            # Check for missing EXIF (common in screenshots)
            if 'exif' not in info:
                # Not necessarily suspicious for screenshots
                pass
            
            # Check for software that edited the image
            if 'Software' in info:
                software = info['Software'].lower()
                if any(x in software for x in ['photoshop', 'gimp', 'paint']):
                    indicators.append(f"Edited with: {info['Software']}")
                    confidence += 0.3
            
        except:
            pass
        
        return {
            'suspicious': len(indicators) > 0,
            'indicators': indicators,
            'confidence': confidence
        }
    
    def _check_noise_pattern(self, img: np.ndarray) -> Dict:
        """Check for inconsistent noise patterns"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate local variance
            kernel = np.ones((5, 5), np.float32) / 25
            mean = cv2.filter2D(gray, -1, kernel)
            local_var = cv2.pow(gray - mean, 2)
            
            # Check for abrupt changes in noise pattern
            variance_std = np.std(local_var)
            
            if variance_std > 1000:
                return {
                    'suspicious': True,
                    'confidence': min(0.3, variance_std / 5000)
                }
            
            return {'suspicious': False, 'confidence': 0.0}
        except:
            return {'suspicious': False, 'confidence': 0.0}
    
    def _check_copy_move(self, img: np.ndarray) -> Dict:
        """Check for copy-move forgery using block matching"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Simple block matching (production would use more sophisticated methods)
            block_size = 16
            h, w = gray.shape
            
            if h < block_size * 2 or w < block_size * 2:
                return {'suspicious': False, 'confidence': 0.0}
            
            # This is a simplified check - real implementation would use DCT or other methods
            return {'suspicious': False, 'confidence': 0.0}
            
        except:
            return {'suspicious': False, 'confidence': 0.0}
    
    def _assess_quality(self, img: np.ndarray) -> float:
        """Assess image quality score"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Score based on sharpness and brightness
            sharpness_score = min(1.0, sharpness / 500)
            brightness_score = 1.0 - abs(128 - brightness) / 128
            
            return (sharpness_score + brightness_score) / 2
            
        except:
            return 0.0
    
    def _is_screenshot(self, img: np.ndarray) -> bool:
        """Detect if image is likely a screenshot"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Screenshots often have:
            # 1. Sharp edges (text, UI elements)
            # 2. Limited color palette
            # 3. Specific aspect ratios
            
            # Check edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Check color diversity
            unique_colors = len(np.unique(gray))
            color_ratio = unique_colors / 256
            
            # Screenshot indicators
            is_screenshot = edge_density > 0.05 and color_ratio < 0.8
            
            return is_screenshot
            
        except:
            return True  # Assume screenshot by default
    
    def verify_ocr_matches_form(self, ocr_result: OCRResult, form_data: PaymentProofCreate) -> bool:
        """Verify OCR extracted data matches form data"""
        mismatches = []
        
        # Check amount match (allow 0 tolerance for exact match)
        if ocr_result.extracted_amount and form_data.amount:
            amount_diff = abs(ocr_result.extracted_amount - form_data.amount)
            if amount_diff > 0:  # Exact match required
                mismatches.append(f"Amount mismatch: Form says Rp {form_data.amount}, Image shows Rp {ocr_result.extracted_amount}")
        
        # Check transaction ID match
        if ocr_result.extracted_transaction_id and form_data.transaction_id:
            if ocr_result.extracted_transaction_id.upper() != form_data.transaction_id.upper():
                mismatches.append(f"Transaction ID mismatch: Form says {form_data.transaction_id}, Image shows {ocr_result.extracted_transaction_id}")
        
        # Check bank match
        if ocr_result.extracted_bank and form_data.bank_name:
            if ocr_result.extracted_bank.upper() != form_data.bank_name.value:
                mismatches.append(f"Bank mismatch: Form says {form_data.bank_name.value}, Image shows {ocr_result.extracted_bank}")
        
        ocr_result.mismatches = mismatches
        ocr_result.matches_form = len(mismatches) == 0
        
        return len(mismatches) == 0
    
    def calculate_image_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two image hashes"""
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            
            # Calculate Hamming distance
            distance = h1 - h2
            max_distance = len(h1.hex) * 4
            
            # Convert to similarity score (0-1)
            similarity = 1 - (distance / max_distance)
            return max(0, min(1, similarity))
        except:
            return 0.0

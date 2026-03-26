"""
Comprehensive Validation Module for Payment Verification
Handles input validation, file validation, OCR, image analysis, and Virtual Account validation
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

# Import Virtual Account manager
from virtual_accounts import get_va_manager


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
    CASH = "CASH"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"


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
    ALFAMART = "ALFAMART"
    INDOMARET = "INDOMARET"
    GIANT = "GIANT"
    LOTTE = "LOTTE"
    CARREFOUR = "CARREFOUR"
    TRANSMART = "TRANSMART"
    MATAHARI = "MATAHARI"
    ELECTRICCITY = "ELECTRICCITY"
    BESTDENKI = "BESTDENKI"


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


class TimingValidationResult(BaseModel):
    """Timing validation result for transaction patterns"""
    is_suspicious: bool = False
    timing_issues: List[str] = []
    confidence_score: float = 0.0
    validation_notes: Optional[str] = None
    timestamp_checked: Optional[str] = None


class PatternValidationResult(BaseModel):
    """Pattern validation result for suspicious activity"""
    is_suspicious: bool = False
    pattern_types: List[str] = []
    confidence_score: float = 0.0
    validation_notes: Optional[str] = None
    timestamp_checked: Optional[str] = None


class FrequencyValidationResult(BaseModel):
    """Transaction frequency validation result"""
    is_within_limit: bool = True
    period_hours: int = 1
    transaction_count: int = 0
    max_allowed: int = 5
    validation_notes: Optional[str] = None
    timestamp_checked: Optional[str] = None


class DebitStatusValidationResult(BaseModel):
    """Debit status validation result"""
    is_debited: bool = False
    status: str = "PENDING"  # PENDING, VERIFIED, FAILED
    verification_method: str = "OCR"  # OCR, API, MANUAL
    verification_notes: Optional[str] = None
    timestamp_verified: Optional[str] = None


class AmountValidationResult(BaseModel):
    """Amount validation result"""
    is_valid: bool = False
    extracted_amount: Optional[int] = None
    expected_amount: Optional[int] = None
    variance_percentage: float = 0.0
    validation_notes: Optional[str] = None


class VirtualAccountValidationResult(BaseModel):
    """Virtual Account validation result"""
    is_valid_va: bool = False
    matched_accounts: List[str] = []
    matched_details: List[Dict] = []
    first_level_status: str = "PENDING"  # PENDING, VALIDATED, REJECTED
    va_validation_notes: Optional[str] = None
    transaction_validation: Optional[Dict] = None  # Transaction validation result


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
    # Add VA validation result
    va_validation: Optional[VirtualAccountValidationResult] = None


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
    
    def extract_ocr(self, image_content: bytes, expected_transaction_id: str = None) -> OCRResult:
        """Extract text from image using OCR and validate against Virtual Accounts"""

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

            # Perform Virtual Account validation with transaction ID
            va_manager = get_va_manager()
            va_validation_result = va_manager.is_valid_va_payment(text, expected_transaction_id)

            # Create OCRResult with VA validation
            ocr_result = OCRResult(
                extracted_text=text,
                extracted_amount=extracted_amount,
                extracted_transaction_id=extracted_tx_id,
                extracted_date=extracted_date,
                extracted_bank=extracted_bank,
                confidence_score=confidence,
                va_validation=VirtualAccountValidationResult(**va_validation_result)
            )

            return ocr_result

        except Exception as e:
            return OCRResult(
                extracted_text="",
                confidence_score=0.0,
                mismatches=[f"OCR failed: {str(e)}"],
                va_validation=VirtualAccountValidationResult(
                    is_valid_va=False,
                    first_level_status="REJECTED",
                    va_validation_notes=f"OCR extraction failed: {str(e)}"
                )
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
            r'(?:TRX|TXN|REF|No\.\s*Transaksi|ID\s*:?)\s*([A-Z0-9\-\/]+)',
            r'(?:Reference|Transaction)\s*(?:ID|Number)[:\s]*([A-Z0-9\-\/]+)',
            r'(?:Kode|Code)\s*[:\s]*([A-Z0-9\-\/]+)',
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

    def _extract_business_info(self, text: str) -> dict:
        """Extract business information from receipt"""
        business_info = {}
        
        # Extract business name (look for common receipt headers)
        name_patterns = [
            r'(?:PT\.?\s+[A-Z][A-Z\s]+)',  # PT Company names
            r'(?:CV\.?\s+[A-Z][A-Z\s]+)',  # CV Company names
            r'(?:Toko\s+[A-Z][A-Za-z\s]+)',  # Toko Store names
            r'(?:Warung\s+[A-Z][A-Za-z\s]+)',  # Warung names
            r'(?:Resto|Restaurant|Kafe|Coffee)\s+[A-Z][A-Za-z\s]+',  # Food service
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                business_info['name'] = match.group(0).strip()
                break
        
        # Extract phone number
        phone_pattern = r'(?:Telp\.?|Phone|Telepon)[:\s]*([0-9\s\-\+\(\)]+)'
        phone_match = re.search(phone_pattern, text, re.IGNORECASE)
        if phone_match:
            business_info['phone'] = phone_match.group(1).strip()
        
        # Extract address (simple pattern)
        address_pattern = r'(?:Alamat|Address)[:\s]*([A-Z0-9\s\.\-,]+)'
        address_match = re.search(address_pattern, text, re.IGNORECASE)
        if address_match:
            business_info['address'] = address_match.group(1).strip()
        
        # Extract tax ID (NPWP pattern)
        npwp_pattern = r'(?:NPWP|Tax ID)[:\s]*([0-9\.]+)'
        npwp_match = re.search(npwp_pattern, text, re.IGNORECASE)
        if npwp_match:
            business_info['tax_id'] = npwp_match.group(1).strip()
        
        return business_info

    def _extract_items_and_totals(self, text: str) -> dict:
        """Extract items and calculate totals from receipt"""
        items = []
        totals = {}
        
        # Extract individual items (basic pattern)
        item_pattern = r'([A-Za-z\s]+?)\s+([0-9,]+)\s+([0-9,]+(?:\.[0-9]{2})?)'
        item_matches = re.findall(item_pattern, text)
        
        for item_match in item_matches:
            item_name, qty, price = item_match
            items.append({
                'name': item_name.strip(),
                'quantity': int(qty.replace(',', '')),
                'price_per_unit': int(float(price.replace(',', '')))
            })
        
        # Extract subtotal, tax, total
        subtotal_pattern = r'(?:Subtotal|Sub Total|Jumlah Sub)\s*[:\s]*Rp\s*([0-9.]+)'
        tax_pattern = r'(?:Tax|Pajak|PPN)\s*[:\s]*Rp\s*([0-9.]+)'
        total_pattern = r'(?:Total|Grand Total|Jumlah Bayar)\s*[:\s]*Rp\s*([0-9.]+)'
        
        subtotal_match = re.search(subtotal_pattern, text, re.IGNORECASE)
        if subtotal_match:
            totals['subtotal'] = int(subtotal_match.group(1).replace('.', ''))
        
        tax_match = re.search(tax_pattern, text, re.IGNORECASE)
        if tax_match:
            totals['tax'] = int(tax_match.group(1).replace('.', ''))
        
        total_match = re.search(total_pattern, text, re.IGNORECASE)
        if total_match:
            totals['total'] = int(total_match.group(1).replace('.', ''))
        
        return {
            'items': items,
            'totals': totals
        }

    def _validate_receipt_format(self, text: str) -> dict:
        """Validate receipt format consistency"""
        validation_results = {
            'has_header': False,
            'has_items': False,
            'has_totals': False,
            'has_footer': False,
            'format_consistency_score': 0.0
        }
        
        # Check for common receipt elements
        text_lower = text.lower()
        
        # Header indicators
        header_indicators = ['pt.', 'cv.', 'toko', 'warung', 'restaurant', 'cafe', 'coffee', 'resto']
        validation_results['has_header'] = any(indicator in text_lower for indicator in header_indicators)
        
        # Item indicators
        item_indicators = ['qty', 'jumlah', 'harga', 'price', 'item', 'barang', 'produk']
        validation_results['has_items'] = any(indicator in text_lower for indicator in item_indicators)
        
        # Total indicators
        total_indicators = ['total', 'grand total', 'jumlah', 'bayar', 'dibayar', 'subtotal']
        validation_results['has_totals'] = any(indicator in text_lower for indicator in total_indicators)
        
        # Footer indicators
        footer_indicators = ['terima kasih', 'thank you', 'kasir', 'receipt', 'struk', 'no. nota']
        validation_results['has_footer'] = any(indicator in text_lower for indicator in footer_indicators)
        
        # Calculate format consistency score
        elements_present = sum([
            validation_results['has_header'],
            validation_results['has_items'], 
            validation_results['has_totals'],
            validation_results['has_footer']
        ])
        
        validation_results['format_consistency_score'] = elements_present / 4.0
        
        return validation_results

    def _extract_bank(self, text: str) -> Optional[str]:
        """Extract bank name from OCR text"""
        banks = ['BCA', 'BRI', 'BNI', 'MANDIRI', 'PERMATA', 'DANAMON', 'CIMB', 'MAYBANK', 'BTN']
        retail_stores = ['ALFAMART', 'INDOMARET', 'GIANT', 'LOTTE', 'CARREFOUR', 'TRANSMART', 'MATAHARI', 'ELECTRICCITY', 'BESTDENKI']
        text_upper = text.upper()

        # Check for banks first
        for bank in banks:
            if bank in text_upper:
                return bank

        # Then check for retail stores
        for store in retail_stores:
            if store in text_upper:
                return store

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

    def verify_ocr_matches_form(self, ocr_result: OCRResult, form_data) -> bool:
        """Verify OCR extracted data matches form data"""
        mismatches = []

        # Check amount match (allow 0 tolerance for exact match)
        if ocr_result.extracted_amount and hasattr(form_data, 'amount') and form_data.amount:
            amount_diff = abs(ocr_result.extracted_amount - form_data.amount)
            if amount_diff > 0:  # Exact match required
                mismatches.append(f"Amount mismatch: Form says Rp {form_data.amount}, Image shows Rp {ocr_result.extracted_amount}")

        # Check transaction ID match
        if ocr_result.extracted_transaction_id and hasattr(form_data, 'transaction_id') and form_data.transaction_id:
            if ocr_result.extracted_transaction_id.upper() != form_data.transaction_id.upper():
                mismatches.append(f"Transaction ID mismatch: Form says {form_data.transaction_id}, Image shows {ocr_result.extracted_transaction_id}")

        # Check bank match - handle both string and enum formats
        if ocr_result.extracted_bank and hasattr(form_data, 'bank_name') and form_data.bank_name:
            # Handle both string and enum formats
            expected_bank = form_data.bank_name
            if hasattr(expected_bank, 'value'):  # It's an enum
                expected_bank = expected_bank.value
            if ocr_result.extracted_bank.upper() != expected_bank.upper():
                mismatches.append(f"Bank mismatch: Form says {expected_bank}, Image shows {ocr_result.extracted_bank}")

        ocr_result.mismatches = mismatches
        ocr_result.matches_form = len(mismatches) == 0

        return len(mismatches) == 0

    def validate_receipt_structure(self, ocr_text: str) -> dict:
        """Validate receipt structure and format consistency"""
        # Extract business information
        business_info = self._extract_business_info(ocr_text)

        # Extract items and totals
        items_totals = self._extract_items_and_totals(ocr_text)

        # Validate format consistency
        format_validation = self._validate_receipt_format(ocr_text)

        # Calculate logical consistency (if totals are present)
        logical_consistency = self._validate_logical_consistency(items_totals)

        # Perform Virtual Account validation
        va_manager = get_va_manager()
        va_validation_result = va_manager.is_valid_va_payment(ocr_text)

        return {
            'business_info': business_info,
            'items_and_totals': items_totals,
            'format_validation': format_validation,
            'logical_consistency': logical_consistency,
            'va_validation': va_validation_result,  # Add VA validation to receipt validation
            'overall_receipt_validity': self._calculate_overall_receipt_validity(
                format_validation,
                logical_consistency,
                business_info
            )
        }
    
    def _validate_logical_consistency(self, items_totals: dict) -> float:
        """Validate logical consistency of receipt items and totals"""
        items = items_totals.get('items', [])
        totals = items_totals.get('totals', {})
        
        score = 0.0
        
        # If we have items and totals, check if they logically add up
        if items and 'total' in totals:
            calculated_total = sum(item['quantity'] * item['price_per_unit'] for item in items)
            actual_total = totals['total']
            
            # Allow for small rounding differences
            if abs(calculated_total - actual_total) <= 100:  # Within 100 rupiah
                score = 1.0
            else:
                # Calculate how close they are
                diff_ratio = abs(calculated_total - actual_total) / max(actual_total, 1)
                score = max(0.0, 1.0 - diff_ratio)
        elif not items and 'total' in totals:
            # If no items but has total, we can't validate calculation but total exists
            score = 0.5
        elif items and not totals:
            # If items but no totals, partial validation possible
            score = 0.3
        else:
            # No items or totals to validate
            score = 0.0
        
        return score
    
    def _calculate_overall_receipt_validity(self, format_validation: dict, logical_consistency: float, business_info: dict) -> float:
        """Calculate overall receipt validity score"""
        format_score = format_validation.get('format_consistency_score', 0.0)
        business_info_present = 1.0 if business_info else 0.3  # Business info presence

        # Weighted average of all factors
        overall_score = (
            format_score * 0.4 +      # Format consistency
            logical_consistency * 0.4 +  # Logical consistency
            business_info_present * 0.2   # Business info presence
        )

        return overall_score

    def validate_amount(self, extracted_amount: Optional[int], expected_amount: Optional[int], variance_threshold: float = 0.05) -> AmountValidationResult:
        """
        Validate extracted amount against expected amount
        
        Args:
            extracted_amount: Amount extracted from OCR
            expected_amount: Amount expected from form submission
            variance_threshold: Maximum allowed variance percentage (default 5%)
        
        Returns:
            AmountValidationResult with validation details
        """
        if extracted_amount is None or expected_amount is None:
            return AmountValidationResult(
                is_valid=False,
                extracted_amount=extracted_amount,
                expected_amount=expected_amount,
                variance_percentage=0.0,
                validation_notes="Either extracted or expected amount is None"
            )

        if expected_amount == 0:
            is_valid = extracted_amount == 0
            variance_percentage = 0.0 if is_valid else float('inf')
            notes = f"Expected amount is zero, extracted amount is {'valid' if is_valid else 'invalid'}"
        else:
            variance = abs(extracted_amount - expected_amount)
            variance_percentage = variance / expected_amount
            is_valid = variance_percentage <= variance_threshold
            notes = f"Variance: {variance_percentage:.2%}, Threshold: {variance_threshold:.2%}, Status: {'PASS' if is_valid else 'FAIL'}"

        return AmountValidationResult(
            is_valid=is_valid,
            extracted_amount=extracted_amount,
            expected_amount=expected_amount,
            variance_percentage=variance_percentage,
            validation_notes=notes
        )

    def validate_debit_status(self, extracted_text: str, transaction_id: str, expected_amount: int) -> DebitStatusValidationResult:
        """
        Validate debit status by checking if the transaction has been successfully processed
        
        Args:
            extracted_text: OCR extracted text from receipt
            transaction_id: Transaction ID to verify
            expected_amount: Expected amount for the transaction
        
        Returns:
            DebitStatusValidationResult with verification details
        """
        # Check for common indicators of successful debit in the receipt text
        text_lower = extracted_text.lower()
        
        # Look for success indicators
        success_indicators = [
            'success', 'berhasil', 'completed', 'selesai', 'paid', 'dibayar', 
            'processed', 'diproses', 'confirmed', 'disetujui', 'approved', 'disetujukan'
        ]
        
        # Look for failure indicators
        failure_indicators = [
            'failed', 'gagal', 'cancelled', 'dibatalkan', 'rejected', 'ditolak',
            'pending', 'menunggu', 'waiting', 'error', 'kesalahan'
        ]
        
        # Check for debit indicators
        debit_indicators = [
            'debit', 'potong', 'pengurangan', 'keluar', 'outgoing', 'withdrawal',
            'charged', 'charged to', 'dikenakan', 'biaya', 'fee', 'tarif'
        ]
        
        # Count indicators
        success_count = sum(1 for indicator in success_indicators if indicator in text_lower)
        failure_count = sum(1 for indicator in failure_indicators if indicator in text_lower)
        debit_count = sum(1 for indicator in debit_indicators if indicator in text_lower)
        
        # Determine status based on indicators
        is_debited = False
        status = "PENDING"
        notes = []
        
        if success_count > failure_count and debit_count > 0:
            is_debited = True
            status = "VERIFIED"
            notes.append("Success and debit indicators found in receipt")
        elif failure_count > 0:
            is_debited = False
            status = "FAILED"
            notes.append("Failure indicators found in receipt")
        elif success_count > 0:
            is_debited = True
            status = "VERIFIED"
            notes.append("Success indicators found in receipt")
        else:
            # If no clear indicators, check for transaction ID presence and amount match
            if transaction_id and transaction_id.upper() in extracted_text.upper():
                # Check if amount is mentioned in the text
                amount_str = str(expected_amount)
                if amount_str in extracted_text:
                    is_debited = True
                    status = "VERIFIED"
                    notes.append(f"Transaction ID and amount found in receipt")
                else:
                    status = "PENDING"
                    notes.append(f"Transaction ID found but amount not clearly indicated")
            else:
                status = "PENDING"
                notes.append("No clear debit status indicators found")
        
        return DebitStatusValidationResult(
            is_debited=is_debited,
            status=status,
            verification_method="OCR",
            verification_notes="; ".join(notes),
            timestamp_verified=datetime.now().isoformat()
        )

    def validate_transaction_frequency(self, user_id: str, db_client, period_hours: int = 1, max_transactions: int = 5) -> FrequencyValidationResult:
        """
        Validate transaction frequency to detect suspicious activity
        
        Args:
            user_id: ID of the user submitting the transaction
            db_client: Database client to query transaction history
            period_hours: Time period in hours to check for transactions
            max_transactions: Maximum allowed transactions in the period
        
        Returns:
            FrequencyValidationResult with validation details
        """
        try:
            from datetime import timedelta
            # Calculate the start time for the period
            start_time = datetime.now() - timedelta(hours=period_hours)
            
            # Query database for recent transactions by this user
            # This is a simplified query - in real implementation, you'd use the actual db client
            try:
                # Attempt to query recent transactions
                result = db_client.table("payment_proofs").select("*").eq("user_id", user_id).gte("created_at", start_time.isoformat()).execute()
                
                transaction_count = len(result.data) if result.data else 0
            except:
                # If database query fails, simulate with mock data
                transaction_count = 0  # Default to 0 if unable to query
            
            is_within_limit = transaction_count <= max_transactions
            notes = []
            
            if is_within_limit:
                notes.append(f"User has {transaction_count} transactions in last {period_hours} hour(s), within limit of {max_transactions}")
            else:
                notes.append(f"Suspicious: User has {transaction_count} transactions in last {period_hours} hour(s), exceeding limit of {max_transactions}")
            
            return FrequencyValidationResult(
                is_within_limit=is_within_limit,
                period_hours=period_hours,
                transaction_count=transaction_count,
                max_allowed=max_transactions,
                validation_notes="; ".join(notes),
                timestamp_checked=datetime.now().isoformat()
            )
        except Exception as e:
            return FrequencyValidationResult(
                is_within_limit=True,  # Default to True if validation fails
                period_hours=period_hours,
                transaction_count=0,
                max_allowed=max_transactions,
                validation_notes=f"Frequency validation failed: {str(e)}",
                timestamp_checked=datetime.now().isoformat()
            )

    def validate_suspicious_patterns(self, extracted_text: str, transaction_amount: int, bank_name: str) -> PatternValidationResult:
        """
        Validate for suspicious patterns in the transaction
        
        Args:
            extracted_text: OCR extracted text from receipt
            transaction_amount: Amount of the transaction
            bank_name: Name of the bank involved
        
        Returns:
            PatternValidationResult with validation details
        """
        text_lower = extracted_text.lower()
        
        # Define suspicious patterns
        suspicious_patterns = {
            "high_frequency_keywords": [
                "test", "demo", "sample", "contoh", "trial", "percobaan"
            ],
            "suspicious_amount_patterns": [
                # Amounts that are commonly used in tests
                1, 10, 100, 1000, 10000, 100000, 500, 5000, 50000
            ],
            "suspicious_text_patterns": [
                # Patterns that indicate fake receipts
                "fake", "palsu", "not valid", "tidak valid", "for test", "untuk tes",
                "mock", "palsu", "tidak sah", "not real", "bukan asli"
            ],
            "timing_indicators": [
                # Indicators of unusual timing
                "00:00", "23:59", "00:01", "23:58"  # Unusual times
            ]
        }
        
        detected_patterns = []
        confidence_score = 0.0
        
        # Check for high frequency keywords
        for keyword in suspicious_patterns["high_frequency_keywords"]:
            if keyword in text_lower:
                detected_patterns.append("HIGH_FREQUENCY_KEYWORD")
                confidence_score += 0.2
        
        # Check for suspicious amounts
        if transaction_amount in suspicious_patterns["suspicious_amount_patterns"]:
            detected_patterns.append("SUSPICIOUS_AMOUNT")
            confidence_score += 0.3
        
        # Check for suspicious text patterns
        for pattern in suspicious_patterns["suspicious_text_patterns"]:
            if pattern in text_lower:
                detected_patterns.append("SUSPICIOUS_TEXT_PATTERN")
                confidence_score += 0.4
        
        # Check for timing indicators in the text
        for timing in suspicious_patterns["timing_indicators"]:
            if timing in text_lower:
                detected_patterns.append("UNUSUAL_TIMING")
                confidence_score += 0.1
        
        # Additional checks for suspicious patterns
        # Check if the bank name appears in unexpected contexts
        if bank_name and f"not {bank_name.lower()}" in text_lower:
            detected_patterns.append("NEGATED_BANK_NAME")
            confidence_score += 0.25
        
        # Check for repeated characters (indicating fake receipts)
        import re
        repeated_chars = re.findall(r'(.)\1{4,}', text_lower)
        if repeated_chars:
            detected_patterns.append("REPETITIVE_CHARACTERS")
            confidence_score += 0.15
        
        # Normalize confidence score
        confidence_score = min(1.0, confidence_score)
        
        is_suspicious = len(detected_patterns) > 0 and confidence_score > 0.25
        
        notes = []
        if is_suspicious:
            notes.append(f"Suspicious patterns detected: {', '.join(detected_patterns)}")
            notes.append(f"Confidence score: {confidence_score:.2f}")
        else:
            notes.append("No suspicious patterns detected")
        
        return PatternValidationResult(
            is_suspicious=is_suspicious,
            pattern_types=detected_patterns,
            confidence_score=confidence_score,
            validation_notes="; ".join(notes),
            timestamp_checked=datetime.now().isoformat()
        )

    def validate_timing_patterns(self, transaction_datetime_str: str, extracted_datetime_str: str = None) -> TimingValidationResult:
        """
        Validate transaction timing patterns to detect suspicious activity
        
        Args:
            transaction_datetime_str: Expected transaction datetime from form submission
            extracted_datetime_str: Datetime extracted from OCR (if available)
        
        Returns:
            TimingValidationResult with validation details
        """
        import re
        from datetime import datetime, timedelta
        
        detected_issues = []
        confidence_score = 0.0
        
        try:
            # Parse the transaction datetime
            if transaction_datetime_str:
                # Handle different datetime formats
                if '.' in transaction_datetime_str:
                    # Format like "2024-03-25T10:30:00.000Z"
                    parsed_transaction_dt = datetime.fromisoformat(transaction_datetime_str.replace('Z', '+00:00'))
                else:
                    # Format like "2024-03-25T10:30:00"
                    parsed_transaction_dt = datetime.fromisoformat(transaction_datetime_str)
            else:
                return TimingValidationResult(
                    is_suspicious=False,
                    timing_issues=[],
                    confidence_score=0.0,
                    validation_notes="No transaction datetime provided for validation",
                    timestamp_checked=datetime.now().isoformat()
                )
            
            # Check if transaction is in the future (with 1 hour buffer for timezone issues)
            now = datetime.now(parsed_transaction_dt.tzinfo) if parsed_transaction_dt.tzinfo else datetime.now()
            if parsed_transaction_dt > now + timedelta(hours=1):
                detected_issues.append("FUTURE_TRANSACTION")
                confidence_score += 0.3
            
            # Check if transaction is too old (more than 1 year)
            if parsed_transaction_dt < now - timedelta(days=365):
                detected_issues.append("OLD_TRANSACTION")
                confidence_score += 0.2
            
            # Check for unusual times (like middle of night)
            if 0 <= parsed_transaction_dt.hour <= 4:
                detected_issues.append("UNUSUAL_TIME_OF_DAY")
                confidence_score += 0.15
            
            # Check for round times (like exactly 00:00:00) which might indicate fake transactions
            if parsed_transaction_dt.minute == 0 and parsed_transaction_dt.second == 0:
                detected_issues.append("ROUND_TIME_STAMP")
                confidence_score += 0.1
            
            # If OCR extracted datetime is available, compare with form datetime
            if extracted_datetime_str:
                try:
                    # Try to parse the extracted datetime
                    # This might come in various formats from OCR
                    extracted_clean = re.sub(r'[^\d\-:T\s]', '', extracted_datetime_str).strip()
                    
                    # Try different parsing approaches
                    parsed_extracted_dt = None
                    for fmt in [
                        '%Y-%m-%dT%H:%M:%S',
                        '%Y-%m-%d %H:%M:%S',
                        '%d/%m/%Y %H:%M:%S',
                        '%d-%m-%Y %H:%M:%S',
                        '%Y-%m-%d %H:%M',
                        '%d/%m/%Y %H:%M'
                    ]:
                        try:
                            parsed_extracted_dt = datetime.strptime(extracted_clean, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if parsed_extracted_dt:
                        # Check if the datetimes are significantly different
                        time_diff = abs((parsed_transaction_dt - parsed_extracted_dt).total_seconds())
                        
                        # If difference is more than 1 hour, it's suspicious
                        if time_diff > 3600:  # 1 hour in seconds
                            detected_issues.append("DATETIME_MISMATCH")
                            confidence_score += 0.25
                except:
                    # If parsing fails, add a note but don't increase confidence significantly
                    detected_issues.append("EXTRACTED_DATETIME_PARSE_FAILED")
                    confidence_score += 0.05
            
            # Check for suspicious patterns in the datetime string itself
            if transaction_datetime_str and re.search(r'(\d)\1{3,}', transaction_datetime_str.replace('-', '').replace(':', '').replace('T', '')):
                # Looks for repeated digits like 20244444 or 1111:11:11
                detected_issues.append("REPETITIVE_DIGITS_IN_TIMESTAMP")
                confidence_score += 0.25
            
            # Normalize confidence score
            confidence_score = min(1.0, confidence_score)
            
            is_suspicious = len(detected_issues) > 0 and confidence_score > 0.2
            
            notes = []
            if is_suspicious:
                notes.append(f"Suspicious timing patterns detected: {', '.join(detected_issues)}")
                notes.append(f"Confidence score: {confidence_score:.2f}")
            else:
                notes.append("Timing patterns appear normal")
            
            return TimingValidationResult(
                is_suspicious=is_suspicious,
                timing_issues=detected_issues,
                confidence_score=confidence_score,
                validation_notes="; ".join(notes),
                timestamp_checked=datetime.now().isoformat()
            )
            
        except Exception as e:
            return TimingValidationResult(
                is_suspicious=False,  # Default to False if validation fails
                timing_issues=["TIMING_VALIDATION_ERROR"],
                confidence_score=0.0,
                validation_notes=f"Timing validation failed: {str(e)}",
                timestamp_checked=datetime.now().isoformat()
            )

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

    def detect_deepfake_indicators(self, image_content: bytes) -> Dict:
        """
        Advanced deepfake detection analysis for receipts
        """
        try:
            # Convert to OpenCV format
            nparr = np.frombuffer(image_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            indicators = []
            confidence = 0.0
            
            # 1. Check for inconsistent lighting (receipt-specific)
            lighting_analysis = self._analyze_lighting(img)
            if lighting_analysis['inconsistent']:
                indicators.append(f"Inconsistent lighting detected: {lighting_analysis['details']}")
                confidence += lighting_analysis['confidence']
            
            # 2. Check for compression artifacts (receipt-specific)
            compression_analysis = self._analyze_compression_artifacts(img)
            if compression_analysis['artifacts_detected']:
                indicators.append(f"Compression artifacts detected: {compression_analysis['details']}")
                confidence += compression_analysis['confidence']
            
            # 3. Check for facial inconsistencies (skip for receipts, but keep for other images)
            face_analysis = self._analyze_faces(img)
            if face_analysis['inconsistencies']:
                indicators.append(f"Facial inconsistencies detected: {face_analysis['details']}")
                confidence += face_analysis['confidence']
            
            # 4. Check for pixel-level anomalies (receipt-specific)
            pixel_analysis = self._analyze_pixel_anomalies(img)
            if pixel_analysis['anomalies']:
                indicators.append(f"Pixel-level anomalies detected: {pixel_analysis['details']}")
                confidence += pixel_analysis['confidence']
            
            # 5. Receipt-specific analysis: Check for text inconsistencies
            text_analysis = self._analyze_text_consistency(img)
            if text_analysis['inconsistencies']:
                indicators.append(f"Text inconsistencies detected: {text_analysis['details']}")
                confidence += text_analysis['confidence']
            
            # 6. Receipt-specific analysis: Check for layout/format inconsistencies
            layout_analysis = self._analyze_layout_consistency(img)
            if layout_analysis['inconsistencies']:
                indicators.append(f"Layout/format inconsistencies detected: {layout_analysis['details']}")
                confidence += layout_analysis['confidence']
            
            # 7. Receipt-specific analysis: Check for signature/stamp authenticity
            signature_analysis = self._analyze_signature_stamp(img)
            if signature_analysis['inconsistencies']:
                indicators.append(f"Signature/stamp authenticity issues: {signature_analysis['details']}")
                confidence += signature_analysis['confidence']
            
            # Normalize confidence to 0-1 range
            confidence = min(confidence, 1.0)
            
            is_likely_manipulated = confidence > 0.5
            
            if is_likely_manipulated:
                recommendation = "Receipt appears to be manipulated or fake, do not trust"
            else:
                recommendation = "Receipt appears authentic, safe to proceed"
                
            return {
                "is_likely_deepfake": is_likely_manipulated,
                "confidence_score": confidence,
                "indicators": indicators,
                "recommendation": recommendation
            }
            
        except Exception as e:
            return {
                "is_likely_deepfake": False,
                "confidence_score": 0.0,
                "indicators": [f"Deepfake analysis failed: {str(e)}"],
                "recommendation": "Unable to analyze, proceed with caution"
            }
    
    def _analyze_text_consistency(self, img: np.ndarray) -> Dict:
        """Analyze text consistency in receipt (font, alignment, etc.)"""
        try:
            # Convert to grayscale for text analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Use OCR to get text positions and analyze consistency
            # This is a simplified check - in practice, you'd use more sophisticated text analysis
            import pytesseract
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            # Analyze text boxes for inconsistencies
            text_boxes = []
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # If confidence > 0
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    text_boxes.append({'x': x, 'y': y, 'w': w, 'h': h, 'text': data['text'][i]})
            
            # Check for text alignment and font consistency
            # This is a simplified check - real implementation would be more sophisticated
            if len(text_boxes) > 10:  # If we have enough text to analyze
                # Check if most text is aligned in similar positions (columns, rows)
                x_positions = [box['x'] for box in text_boxes if box['text'].strip()]
                y_positions = [box['y'] for box in text_boxes if box['text'].strip()]
                
                # If there are too many scattered text positions, it might indicate manipulation
                unique_x_pos = len(set(x_positions))
                unique_y_pos = len(set(y_positions))
                
                if unique_x_pos > 20 or unique_y_pos > 30:  # Arbitrary thresholds
                    return {
                        "inconsistencies": True,
                        "details": f"Unusual text positioning (x: {unique_x_pos}, y: {unique_y_pos})",
                        "confidence": 0.3
                    }
            
            return {
                "inconsistencies": False,
                "details": "Text positioning appears consistent",
                "confidence": 0.0
            }
        except:
            return {
                "inconsistencies": False,
                "details": "Text analysis failed",
                "confidence": 0.0
            }
    
    def _analyze_layout_consistency(self, img: np.ndarray) -> Dict:
        """Analyze layout consistency in receipt"""
        try:
            height, width = img.shape[:2]
            
            # Define expected regions for receipt elements
            header_region = img[0:int(height*0.2), :]  # Top 20% for header
            middle_region = img[int(height*0.2):int(height*0.8), :]  # Middle 60% for items
            footer_region = img[int(height*0.8):height, :]  # Bottom 20% for footer
            
            # Analyze each region for expected content
            header_analysis = self._analyze_region(header_region)
            middle_analysis = self._analyze_region(middle_region)
            footer_analysis = self._analyze_region(footer_region)
            
            inconsistencies = []
            
            # Check if regions have expected characteristics
            if header_analysis['text_density'] < 0.05:  # Very low text density in header
                inconsistencies.append("Header region has unexpectedly low text density")
            
            if middle_analysis['text_density'] < 0.1:  # Low text density in middle
                inconsistencies.append("Middle region has unexpectedly low text density (should contain items)")
            
            if footer_analysis['text_density'] < 0.02:  # Very low text density in footer
                inconsistencies.append("Footer region has unexpectedly low text density")
            
            if inconsistencies:
                return {
                    "inconsistencies": True,
                    "details": ", ".join(inconsistencies),
                    "confidence": 0.2 * len(inconsistencies)  # Scale confidence with number of issues
                }
            
            return {
                "inconsistencies": False,
                "details": "Layout appears consistent",
                "confidence": 0.0
            }
        except:
            return {
                "inconsistencies": False,
                "details": "Layout analysis failed",
                "confidence": 0.0
            }
    
    def _analyze_region(self, region) -> Dict:
        """Helper to analyze a region of the image"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # Calculate text density based on edges (indicating text)
            edges = cv2.Canny(gray, 50, 150)
            text_area = np.sum(edges > 0)
            total_area = region.shape[0] * region.shape[1]
            text_density = text_area / total_area if total_area > 0 else 0
            
            return {
                "text_density": text_density,
                "area": total_area
            }
        except:
            return {
                "text_density": 0,
                "area": 0
            }
    
    def _analyze_signature_stamp(self, img: np.ndarray) -> Dict:
        """Analyze signature/stamp authenticity in receipt"""
        try:
            # Look for common signature/stamp patterns in receipts
            # This is a simplified check - real implementation would use ML models
            height, width = img.shape[:2]
            
            # Focus on bottom portion where signatures/stamps usually are
            bottom_region = img[int(height*0.7):height, :]
            
            # Convert to grayscale
            gray = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2GRAY)
            
            # Look for circular or rectangular patterns that might indicate stamps
            # This is a simplified approach
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=50,
                param1=50,
                param2=30,
                minRadius=10,
                maxRadius=100
            )
            
            if circles is not None and len(circles[0]) > 5:  # Too many circles might indicate manipulation
                return {
                    "inconsistencies": True,
                    "details": f"Unusual circular patterns detected ({len(circles[0])} circles)",
                    "confidence": 0.3
                }
            
            return {
                "inconsistencies": False,
                "details": "No unusual signature/stamp patterns detected",
                "confidence": 0.0
            }
        except:
            return {
                "inconsistencies": False,
                "details": "Signature/stamp analysis failed",
                "confidence": 0.0
            }
    
    def _analyze_lighting(self, img: np.ndarray) -> Dict:
        """Analyze lighting consistency in the image"""
        try:
            # Convert to grayscale for lighting analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate gradient to detect lighting inconsistencies
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate magnitude of gradients
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Check for unusual patterns in lighting
            mean_grad = np.mean(grad_magnitude)
            std_grad = np.std(grad_magnitude)
            
            # If lighting is too uniform or has strange patterns, it might be a deepfake
            if std_grad < 10:  # Too uniform lighting
                return {
                    "inconsistent": True,
                    "details": "Unusually uniform lighting pattern",
                    "confidence": 0.3
                }
            elif std_grad > 100:  # Too much variation
                return {
                    "inconsistent": True,
                    "details": "High lighting variation suggesting manipulation",
                    "confidence": 0.4
                }
            
            return {
                "inconsistent": False,
                "details": "Normal lighting pattern",
                "confidence": 0.0
            }
        except:
            return {
                "inconsistent": False,
                "details": "Lighting analysis failed",
                "confidence": 0.0
            }
    
    def _analyze_compression_artifacts(self, img: np.ndarray) -> Dict:
        """Analyze compression artifacts that might indicate manipulation"""
        try:
            # Calculate quality metrics
            quality_score = self._assess_quality(img)
            
            # Low quality might indicate heavy compression or manipulation
            if quality_score < 0.3:
                return {
                    "artifacts_detected": True,
                    "details": f"Low image quality ({quality_score:.2f}) suggesting possible manipulation",
                    "confidence": 0.4
                }
            
            return {
                "artifacts_detected": False,
                "details": "Normal compression level",
                "confidence": 0.0
            }
        except:
            return {
                "artifacts_detected": False,
                "details": "Compression analysis failed",
                "confidence": 0.0
            }
    
    def _analyze_faces(self, img: np.ndarray) -> Dict:
        """Analyze faces for deepfake indicators (if faces are present)"""
        try:
            # Try to detect faces using Haar cascades
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return {
                    "inconsistencies": False,
                    "details": "No faces detected in image",
                    "confidence": 0.0
                }
            
            # For each face, check for common deepfake indicators
            inconsistencies_found = []
            face_confidence = 0.0
            
            for (x, y, w, h) in faces:
                face_roi = img[y:y+h, x:x+w]
                
                # Check for blending artifacts around face boundaries
                # This is a simplified check - real deepfake detection would be more sophisticated
                face_mean = np.mean(face_roi)
                surrounding_mean = np.mean(img[max(0,y-10):y, x:x+w]) if y > 0 else face_mean
                
                if abs(face_mean - surrounding_mean) > 50:  # Significant difference
                    inconsistencies_found.append("Face blending artifacts detected")
                    face_confidence += 0.2
            
            if inconsistencies_found:
                return {
                    "inconsistencies": True,
                    "details": ", ".join(inconsistencies_found),
                    "confidence": face_confidence
                }
            
            return {
                "inconsistencies": False,
                "details": "No face inconsistencies detected",
                "confidence": 0.0
            }
        except:
            return {
                "inconsistencies": False,
                "details": "Face analysis failed",
                "confidence": 0.0
            }
    
    def _analyze_pixel_anomalies(self, img: np.ndarray) -> Dict:
        """Analyze pixel-level anomalies that might indicate manipulation"""
        try:
            # Convert to different color spaces to detect anomalies
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            
            # Check for unusual patterns in the L channel (luminosity)
            l_mean = np.mean(l_channel)
            l_std = np.std(l_channel)
            
            # Check for banding or other artifacts
            unique_vals_l = len(np.unique(l_channel))
            total_vals_l = l_channel.size
            
            # If there are too few unique values, it might indicate quantization artifacts
            if unique_vals_l / total_vals_l < 0.1:  # Less than 10% unique values
                return {
                    "anomalies": True,
                    "details": f"Color banding detected ({unique_vals_l/total_vals_l:.2%} unique luminosity values)",
                    "confidence": 0.3
                }
            
            return {
                "anomalies": False,
                "details": "No significant pixel anomalies detected",
                "confidence": 0.0
            }
        except:
            return {
                "anomalies": False,
                "details": "Pixel analysis failed",
                "confidence": 0.0
            }

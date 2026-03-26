"""
Second Level Validation Module for Aman ga? Payment Verification System
Implements custom validation rules for receipts that pass the first level VA validation
"""

from typing import Dict, Any, List
from datetime import datetime
from validators import OCRResult, ImageAnalysisResult, VirtualAccountValidationResult, AmountValidationResult, DebitStatusValidationResult


class SecondLevelValidator:
    """Implements second level validation for receipts that passed first level VA validation"""
    
    def __init__(self):
        # Define validation thresholds and rules
        self.validation_rules = {
            'min_ocr_confidence': 0.6,  # Minimum OCR confidence for second level validation
            'max_image_risk_level': 'MEDIUM',  # Maximum acceptable image risk level
            'required_fields': ['amount', 'transaction_id', 'date'],  # Required fields for validation
            'amount_variance_threshold': 0.05,  # 5% variance allowed between OCR and form
            'date_tolerance_days': 1,  # Number of days tolerance for date validation
        }
    
    def validate_second_level(
        self, 
        ocr_result: OCRResult, 
        image_analysis: ImageAnalysisResult, 
        form_data: Dict[str, Any],
        validator_instance=None  # Pass the validator instance for additional checks
    ) -> Dict[str, Any]:
        """
        Perform second level validation on receipt data
        
        Args:
            ocr_result: OCR extraction results with VA validation
            image_analysis: Image analysis results
            form_data: Original form data submitted by user
            validator_instance: Instance of PaymentValidator for additional validation
            
        Returns:
            Dict containing validation results and recommendations
        """
        
        # Initialize validation result
        validation_result = {
            'passed': True,
            'issues': [],
            'warnings': [],
            'confidence_score': 0.0,
            'recommendation': 'PROCEED',
            'validation_details': {},
            'amount_validation': None,
            'debit_status_validation': None
        }
        
        # Check if first level validation passed
        if not ocr_result.va_validation or ocr_result.va_validation.first_level_status != 'VALIDATED':
            validation_result['passed'] = False
            validation_result['issues'].append('First level VA validation failed')
            validation_result['recommendation'] = 'REJECT'
            return validation_result
        
        # Validate OCR confidence
        ocr_confidence_ok = self._validate_ocr_confidence(ocr_result.confidence_score)
        if not ocr_confidence_ok:
            validation_result['passed'] = False
            validation_result['issues'].append(f'OCR confidence too low: {ocr_result.confidence_score:.2f}')
            validation_result['recommendation'] = 'REJECT'
        
        # Validate image risk level
        image_risk_ok = self._validate_image_risk(image_analysis.risk_level)
        if not image_risk_ok:
            validation_result['passed'] = False
            validation_result['issues'].append(f'Image risk level too high: {image_analysis.risk_level}')
            validation_result['recommendation'] = 'MANUAL_REVIEW'
        
        # Validate extracted data against form data
        data_consistency_ok = self._validate_data_consistency(ocr_result, form_data)
        if not data_consistency_ok:
            validation_result['passed'] = False
            validation_result['issues'].extend(data_consistency_ok['issues'])
            if validation_result['recommendation'] != 'REJECT':
                validation_result['recommendation'] = 'MANUAL_REVIEW'
        
        # Perform additional validations if validator instance is provided
        amount_validation_result = None
        debit_status_validation_result = None
        
        if validator_instance:
            # Validate amount
            expected_amount = form_data.get('amount')
            extracted_amount = ocr_result.extracted_amount
            amount_validation_result = validator_instance.validate_amount(extracted_amount, expected_amount)
            validation_result['amount_validation'] = amount_validation_result.model_dump()
            
            # Validate debit status
            transaction_id = form_data.get('transaction_id')
            debit_status_validation_result = validator_instance.validate_debit_status(
                ocr_result.extracted_text, 
                transaction_id, 
                expected_amount
            )
            validation_result['debit_status_validation'] = debit_status_validation_result.model_dump()
            
            # Update validation result based on additional checks
            if not amount_validation_result.is_valid:
                validation_result['issues'].append(f"Amount validation failed: {amount_validation_result.validation_notes}")
                if validation_result['recommendation'] != 'REJECT':
                    validation_result['recommendation'] = 'MANUAL_REVIEW'
            
            if debit_status_validation_result.status == 'FAILED':
                validation_result['issues'].append(f"Debit status validation failed: {debit_status_validation_result.verification_notes}")
                validation_result['recommendation'] = 'REJECT'
            elif debit_status_validation_result.status == 'PENDING':
                validation_result['warnings'].append(f"Debit status pending verification: {debit_status_validation_result.verification_notes}")
                if validation_result['recommendation'] == 'PROCEED':
                    validation_result['recommendation'] = 'CAUTION'
        
        # Validate receipt format and structure
        format_ok = self._validate_receipt_format(ocr_result.extracted_text)
        if not format_ok['valid']:
            validation_result['warnings'].extend(format_ok['warnings'])
            if validation_result['recommendation'] == 'PROCEED':
                validation_result['recommendation'] = 'CAUTION'
        
        # Calculate overall confidence score
        validation_result['confidence_score'] = self._calculate_confidence_score(
            ocr_result.confidence_score,
            image_analysis.quality_score,
            ocr_confidence_ok,
            image_risk_ok,
            data_consistency_ok['consistent'],
            amount_validation_result.is_valid if amount_validation_result else True
        )
        
        # Determine final recommendation based on all validations
        validation_result['recommendation'] = self._determine_final_recommendation(validation_result)
        
        # Add validation details
        validation_result['validation_details'] = {
            'ocr_confidence_valid': ocr_confidence_ok,
            'image_risk_valid': image_risk_ok,
            'data_consistency_valid': data_consistency_ok['consistent'],
            'format_valid': format_ok['valid'],
            'va_validation_passed': ocr_result.va_validation.is_valid_va if ocr_result.va_validation else False,
            'amount_validation_passed': amount_validation_result.is_valid if amount_validation_result else True,
            'debit_status_validation_status': debit_status_validation_result.status if debit_status_validation_result else 'UNKNOWN'
        }
        
        return validation_result
    
    def _validate_ocr_confidence(self, confidence_score: float) -> bool:
        """Validate OCR confidence score meets minimum threshold"""
        return confidence_score >= self.validation_rules['min_ocr_confidence']
    
    def _validate_image_risk(self, risk_level: str) -> bool:
        """Validate image risk level is acceptable"""
        risk_levels = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3, 'UNKNOWN': 4}
        max_level_idx = risk_levels[self.validation_rules['max_image_risk_level']]
        current_level_idx = risk_levels.get(risk_level, 4)  # UNKNOWN by default
        
        return current_level_idx <= max_level_idx
    
    def _validate_data_consistency(self, ocr_result: OCRResult, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency between OCR-extracted data and form data"""
        issues = []
        consistent = True
        
        # Check amount consistency
        if 'amount' in self.validation_rules['required_fields'] and ocr_result.extracted_amount and form_data.get('amount'):
            amount_diff = abs(ocr_result.extracted_amount - form_data['amount'])
            max_allowed_diff = form_data['amount'] * self.validation_rules['amount_variance_threshold']
            
            if amount_diff > max_allowed_diff:
                issues.append(f'Amount mismatch: Form={form_data["amount"]}, OCR={ocr_result.extracted_amount}')
                consistent = False
        
        # Check transaction ID consistency
        if 'transaction_id' in self.validation_rules['required_fields'] and ocr_result.extracted_transaction_id and form_data.get('transaction_id'):
            if ocr_result.extracted_transaction_id.upper() != form_data['transaction_id'].upper():
                issues.append(f'Transaction ID mismatch: Form={form_data["transaction_id"]}, OCR={ocr_result.extracted_transaction_id}')
                consistent = False
        
        # Check date consistency
        if 'date' in self.validation_rules['required_fields'] and ocr_result.extracted_date and form_data.get('transaction_date'):
            try:
                # Parse dates for comparison
                ocr_date_str = ocr_result.extracted_date
                form_date_str = form_data['transaction_date'].split('T')[0]  # Extract date part
                
                ocr_date = datetime.strptime(ocr_date_str.replace('/', '-'), '%d-%m-%Y') if '-' in ocr_date_str else datetime.strptime(ocr_date_str, '%Y-%m-%d')
                form_date = datetime.strptime(form_date_str, '%Y-%m-%d')
                
                date_diff = abs((ocr_date - form_date).days)
                
                if date_diff > self.validation_rules['date_tolerance_days']:
                    issues.append(f'Date mismatch: Form={form_date_str}, OCR={ocr_date_str} (diff: {date_diff} days)')
                    consistent = False
            except ValueError:
                issues.append('Could not parse dates for comparison')
                consistent = False
        
        return {
            'consistent': consistent,
            'issues': issues
        }
    
    def _validate_receipt_format(self, ocr_text: str) -> Dict[str, Any]:
        """Validate receipt format and structure"""
        warnings = []
        valid = True
        
        # Check for common receipt elements
        text_lower = ocr_text.lower()
        
        # Check for currency indicators
        currency_indicators = ['rp', 'idr', 'rupiah', '$', ' IDR ', ' RP ']
        has_currency = any(indicator in text_lower for indicator in currency_indicators)
        
        if not has_currency:
            warnings.append('No currency indicators found in receipt')
            valid = False
        
        # Check for time indicators
        time_indicators = [':00', ':15', ':30', ':45', 'am', 'pm', 'wib', 'wita', 'wit']
        has_time = any(indicator in text_lower for indicator in time_indicators)
        
        if not has_time:
            warnings.append('No time indicators found in receipt')
        
        # Check for business indicators
        business_indicators = ['pt', 'cv', 'toko', 'warung', 'restaurant', 'cafe', 'receipt', 'struk', 'nota']
        has_business = any(indicator in text_lower for indicator in business_indicators)
        
        if not has_business:
            warnings.append('No business indicators found in receipt')
            valid = False
        
        return {
            'valid': valid,
            'warnings': warnings
        }
    
    def _calculate_confidence_score(
        self, 
        ocr_confidence: float, 
        image_quality: float, 
        ocr_valid: bool, 
        image_valid: bool, 
        data_consistent: bool,
        amount_valid: bool = True
    ) -> float:
        """Calculate overall confidence score based on all validation factors"""
        score = 0.0
        
        # Base score from OCR confidence
        score += ocr_confidence * 0.25  # Reduced weight to accommodate new factors
        
        # Image quality contribution
        score += image_quality * 0.15   # Reduced weight to accommodate new factors
        
        # Validation status contributions
        score += (1.0 if ocr_valid else 0.0) * 0.12
        score += (1.0 if image_valid else 0.0) * 0.12
        score += (1.0 if data_consistent else 0.0) * 0.15
        score += (1.0 if amount_valid else 0.0) * 0.21  # Added amount validation weight
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _determine_final_recommendation(self, validation_result: Dict[str, Any]) -> str:
        """Determine final recommendation based on validation results"""
        if not validation_result['passed']:
            if 'REJECT' in validation_result['recommendation']:
                return 'REJECT'
            else:
                return 'MANUAL_REVIEW'
        
        # If all validations passed, determine recommendation based on confidence
        if validation_result['confidence_score'] >= 0.8:
            return 'STRONGLY_ACCEPT'
        elif validation_result['confidence_score'] >= 0.6:
            return 'ACCEPT_WITH_CAUTION'
        elif validation_result['confidence_score'] >= 0.4:
            return 'MANUAL_REVIEW'
        else:
            return 'REJECT'
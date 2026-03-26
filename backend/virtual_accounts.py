"""
Virtual Account Configuration for Aman ga? Payment Verification System
Defines the 5 Virtual Accounts used for first-level validation
"""

from typing import Dict, List
from dataclasses import dataclass
import re


@dataclass
class VirtualAccount:
    """Represents a Virtual Account for payment validation"""
    id: str
    name: str
    bank_code: str
    account_number: str
    description: str
    pattern: str  # Regex pattern to match in OCR text
    transaction_prefixes: List[str] = None  # Valid transaction ID prefixes for this VA
    
    def __post_init__(self):
        if self.transaction_prefixes is None:
            self.transaction_prefixes = []


class VirtualAccountManager:
    """Manages the 5 Virtual Accounts for the system"""
    
    def __init__(self):
        self.virtual_accounts = [
            VirtualAccount(
                id="va_bca",
                name="BCA Virtual Account",
                bank_code="BCA",
                account_number="8888",  # Last 4 digits for example
                description="BCA Virtual Account for payment verification",
                pattern=r"(?i)(?:8888\d{8}|BCA.*8888|\b8888\d{8}\b)",  # Pattern to match BCA VA
                transaction_prefixes=["BCA", "TRXBCA", "BCATRX"]
            ),
            VirtualAccount(
                id="va_bri",
                name="BRI Virtual Account",
                bank_code="BRI",
                account_number="9999",  # Last 4 digits for example
                description="BRI Virtual Account for payment verification",
                pattern=r"(?i)(?:9999\d{7}|BRI.*9999|\b9999\d{7}\b)",  # Pattern to match BRI VA
                transaction_prefixes=["BRI", "TRXBRI", "BRITRX"]
            ),
            VirtualAccount(
                id="va_mandiri",
                name="Mandiri Virtual Account",
                bank_code="MANDIRI",
                account_number="7777",  # Last 4 digits for example
                description="Mandiri Virtual Account for payment verification",
                pattern=r"(?i)(?:7777\d{8}|MANDIRI.*7777|\b7777\d{8}\b)",  # Pattern to match Mandiri VA
                transaction_prefixes=["MANDIRI", "TRXMDR", "MDRTRX"]
            ),
            VirtualAccount(
                id="va_bni",
                name="BNI Virtual Account",
                bank_code="BNI",
                account_number="6666",  # Last 4 digits for example
                description="BNI Virtual Account for payment verification",
                pattern=r"(?i)(?:6666\d{8}|BNI.*6666|\b6666\d{8}\b)",  # Pattern to match BNI VA
                transaction_prefixes=["BNI", "TRXBNI", "BNITRX"]
            ),
            VirtualAccount(
                id="va_permata",
                name="Permata Virtual Account",
                bank_code="PERMATA",
                account_number="5555",  # Last 4 digits for example
                description="Permata Virtual Account for payment verification",
                pattern=r"(?i)(?:5555\d{8}|PERMATA.*5555|\b5555\d{8}\b)",  # Pattern to match Permata VA
                transaction_prefixes=["PERMATA", "TRXPTM", "PTMTRX"]
            )
        ]
    
    def get_all_virtual_accounts(self) -> List[VirtualAccount]:
        """Return all configured virtual accounts"""
        return self.virtual_accounts
    
    def find_matching_va(self, ocr_text: str) -> List[VirtualAccount]:
        """Find virtual accounts that match the OCR text"""
        matches = []
        
        for va in self.virtual_accounts:
            if re.search(va.pattern, ocr_text):
                matches.append(va)
        
        return matches
    
    def is_valid_va_payment(self, ocr_text: str, transaction_id: str = None) -> Dict:
        """Check if the OCR text contains a valid VA payment and return validation result"""
        matches = self.find_matching_va(ocr_text)
        
        if matches:
            # Validate transaction ID if provided
            transaction_validation = self.validate_transaction_id(matches[0], transaction_id) if transaction_id else {
                "valid": True,
                "reason": "No transaction ID provided for validation"
            }
            
            return {
                "is_valid_va": True,
                "matched_accounts": [va.id for va in matches],
                "matched_details": [
                    {
                        "id": va.id,
                        "name": va.name,
                        "bank_code": va.bank_code,
                        "account_number": va.account_number,
                        "transaction_validation": transaction_validation
                    } for va in matches
                ],
                "first_level_status": "VALIDATED" if transaction_validation["valid"] else "REJECTED",  # First level validation passed
                "transaction_validation": transaction_validation
            }
        else:
            return {
                "is_valid_va": False,
                "matched_accounts": [],
                "matched_details": [],
                "first_level_status": "REJECTED",  # First level validation failed
                "transaction_validation": {
                    "valid": False,
                    "reason": "No matching virtual account found"
                }
            }
    
    def validate_transaction_id(self, virtual_account: VirtualAccount, transaction_id: str) -> Dict:
        """Validate transaction ID against the virtual account's allowed prefixes"""
        if not transaction_id:
            return {
                "valid": False,
                "reason": "No transaction ID provided"
            }
        
        # Check if transaction ID starts with any of the allowed prefixes
        for prefix in virtual_account.transaction_prefixes:
            if transaction_id.upper().startswith(prefix.upper()):
                return {
                    "valid": True,
                    "reason": f"Transaction ID matches allowed prefix: {prefix}"
                }
        
        return {
            "valid": False,
            "reason": f"Transaction ID '{transaction_id}' does not match any allowed prefixes: {virtual_account.transaction_prefixes}"
        }


# Singleton instance
va_manager = VirtualAccountManager()


def get_va_manager() -> VirtualAccountManager:
    """Get the singleton instance of VirtualAccountManager"""
    return va_manager
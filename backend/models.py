from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    FINANCE = "FINANCE"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    BANNED = "BANNED"

class ServiceType(str, Enum):
    CEK_DASAR = "CEK_DASAR"
    CEK_DEEP = "CEK_DEEP"
    CEK_PLUS = "CEK_PLUS"
    WALLET_TOPUP = "WALLET_TOPUP"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    AUTO_APPROVED = "AUTO_APPROVED"
    FLAGGED = "FLAGGED"

class User(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole
    status: UserStatus

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class PaymentProof(BaseModel):
    id: str
    user_id: str
    service_type: ServiceType
    amount: int
    payment_method: str
    bank_name: Optional[str] = None
    transaction_id: str
    transaction_date: datetime
    proof_image_url: str
    status: PaymentStatus
    created_at: datetime

class PaymentProofCreate(BaseModel):
    service_type: ServiceType
    amount: int
    payment_method: str
    bank_name: Optional[str] = None
    transaction_id: str
    transaction_date: datetime
    proof_image_url: str

class ServiceCredit(BaseModel):
    id: str
    user_id: str
    service_type: ServiceType
    quantity: int
    used_quantity: int
    status: str
    expires_at: datetime

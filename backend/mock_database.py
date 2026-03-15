"""
Mock Database Service for Testing Without Supabase
This allows you to test the full application without any external dependencies.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# In-memory storage (resets on restart)
mock_db = {
    "users": [],
    "payment_proofs": [],
    "service_credits": [],
    "fraud_flags": [],
    "admin_audit_log": []
}

# Pre-seed admin user
admin_user = {
    "id": "admin-001",
    "email": "admin@amanga.id",
    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu",  # admin123
    "full_name": "System Administrator",
    "phone": "081234567890",
    "role": "ADMIN",
    "status": "ACTIVE",
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat()
}

finance_user = {
    "id": "finance-001",
    "email": "finance@amanga.id",
    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu",  # admin123
    "full_name": "Finance Team",
    "phone": "081234567891",
    "role": "FINANCE",
    "status": "ACTIVE",
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat()
}

mock_db["users"].extend([admin_user, finance_user])

class MockTable:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.data = mock_db[table_name]
    
    def insert(self, record: Dict):
        """Insert a record"""
        if "id" not in record:
            record["id"] = f"{self.table_name}-{len(self.data) + 1:03d}"
        if "created_at" not in record:
            record["created_at"] = datetime.now().isoformat()
        if "updated_at" not in record:
            record["updated_at"] = datetime.now().isoformat()
        self.data.append(record)
        return MockResponse([record])
    
    def select(self, columns: str = "*", count: str = None):
        """Select records"""
        self._query_result = self.data.copy()
        return self
    
    def eq(self, field: str, value: Any):
        """Filter by equality"""
        self._query_result = [r for r in self._query_result if r.get(field) == value]
        return self
    
    def neq(self, field: str, value: Any):
        """Filter by not equal"""
        self._query_result = [r for r in self._query_result if r.get(field) != value]
        return self
    
    def gt(self, field: str, value: Any):
        """Filter by greater than"""
        self._query_result = [r for r in self._query_result if r.get(field, 0) > value]
        return self
    
    def gte(self, field: str, value: Any):
        """Filter by greater than or equal"""
        self._query_result = [r for r in self._query_result if r.get(field, 0) >= value]
        return self
    
    def lt(self, field: str, value: Any):
        """Filter by less than"""
        self._query_result = [r for r in self._query_result if r.get(field, 0) < value]
        return self
    
    def lte(self, field: str, value: Any):
        """Filter by less than or equal"""
        self._query_result = [r for r in self._query_result if r.get(field, 0) <= value]
        return self
    
    def order(self, field: str, desc: bool = False):
        """Order results"""
        self._query_result = sorted(
            self._query_result,
            key=lambda x: x.get(field, ""),
            reverse=desc
        )
        return self
    
    def limit(self, count: int):
        """Limit results"""
        self._query_result = self._query_result[:count]
        return self
    
    def execute(self):
        """Execute query and return results"""
        return MockResponse(self._query_result)
    
    def update(self, updates: Dict):
        """Update records"""
        updates["updated_at"] = datetime.now().isoformat()
        for record in self._query_result:
            record.update(updates)
        return MockResponse(self._query_result)
    
    def delete(self):
        """Delete records"""
        for record in self._query_result:
            if record in self.data:
                self.data.remove(record)
        return MockResponse(self._query_result)


class MockResponse:
    def __init__(self, data: List):
        self.data = data
        self.count = len(data)


class MockSupabase:
    """Mock Supabase client for testing without external dependencies"""
    
    def __init__(self):
        print("🎯 MOCK MODE: Using in-memory database for testing")
        print("   Note: Data will reset when server restarts")
        print("   Demo accounts:")
        print("   - Admin: admin@amanga.id / admin123")
        print("   - Finance: finance@amanga.id / admin123")
    
    def table(self, table_name: str):
        """Get table reference"""
        return MockTable(table_name)
    
    def auth(self):
        """Mock auth endpoint"""
        return self


# Create mock supabase instance
mock_supabase = MockSupabase()

def get_mock_db():
    """Get mock database instance"""
    return mock_supabase

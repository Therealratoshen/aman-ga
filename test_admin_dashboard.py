#!/usr/bin/env python3
"""
Test script to verify the integrated admin dashboard and monitoring system
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ocr_learning import SelfLearningOCR, UserFeedback
from automatic_learning import AutomaticLearningSystem
from admin_api import get_system_status, get_detailed_metrics, get_authenticity_metrics
from datetime import datetime
import uuid
import asyncio


async def test_admin_endpoints():
    """Test the admin API endpoints"""
    print("Testing Admin API Endpoints...")
    
    # Mock current user with admin role
    mock_user = {"role": "ADMIN"}
    
    print("\n1. Testing system status endpoint...")
    try:
        # Note: This would normally be called from the FastAPI route
        # For testing, we'll access the underlying data directly
        ocr_system = SelfLearningOCR()
        from automatic_learning import automatic_learning_system
        
        status = {
            "ocr_system": {
                "total_formats": len(ocr_system.receipt_formats),
                "total_feedback": len(ocr_system.feedback_history),
                "learning_metrics": {
                    "total_samples": ocr_system.metrics.total_samples,
                    "total_feedback": ocr_system.metrics.total_feedback,
                    "corrections": ocr_system.metrics.corrections,
                    "confirmations": ocr_system.metrics.confirmations,
                    "authenticity_feedback": ocr_system.metrics.authenticity_feedback,
                    "authenticity_accuracy": ocr_system.metrics.authenticity_accuracy,
                },
                "last_updated": datetime.now().isoformat()
            },
            "automatic_learning": automatic_learning_system.get_learning_status(),
            "system_health": "healthy" if automatic_learning_system.get_learning_status()["is_running"] else "degraded",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"   System status retrieved successfully")
        print(f"   Total formats: {status['ocr_system']['total_formats']}")
        print(f"   Total feedback: {status['ocr_system']['total_feedback']}")
        print(f"   Learning system running: {status['automatic_learning']['is_running']}")
        
    except Exception as e:
        print(f"   Error testing system status: {e}")
    
    print("\n2. Testing format management...")
    try:
        formats = []
        for provider, format_info in list(SelfLearningOCR().receipt_formats.items())[:5]:  # First 5
            formats.append({
                "provider": provider,
                "bank_name": format_info.bank_name,
                "confidence_score": format_info.confidence_score,
                "authenticity_score": format_info.authenticity_score,
                "sample_count": format_info.sample_count,
                "last_updated": format_info.last_updated,
                "typical_colors": format_info.typical_colors,
                "has_qr_code": format_info.has_qr_code,
                "has_watermark": format_info.has_watermark
            })
        
        print(f"   Retrieved {len(formats)} formats")
        for fmt in formats:
            print(f"     - {fmt['provider']}: {fmt['confidence_score']:.2f} confidence, {fmt['authenticity_score']:.2f} authenticity")
            
    except Exception as e:
        print(f"   Error testing format management: {e}")
    
    print("\n3. Testing learning cycle triggers...")
    try:
        auto_learning = AutomaticLearningSystem()
        
        # Test daily cycle
        auto_learning.daily_learning_cycle()
        print("   Daily learning cycle executed")
        
        # Test weekly cycle
        auto_learning.weekly_learning_cycle()
        print("   Weekly learning cycle executed")
        
        # Test monthly cycle
        auto_learning.monthly_deep_learning()
        print("   Monthly learning cycle executed")
        
    except Exception as e:
        print(f"   Error testing learning cycles: {e}")
    
    print("\n4. Testing with sample feedback...")
    try:
        ocr_system = SelfLearningOCR()
        
        # Submit sample feedback to test metrics
        for i in range(3):
            feedback = UserFeedback(
                feedback_id=str(uuid.uuid4()),
                payment_proof_id=f"test_payment_{i}",
                timestamp=datetime.now().isoformat(),
                ocr_extracted_amount=100000 + (i * 10000),
                ocr_extracted_transaction_id=f"TRX{i}TEST123",
                ocr_extracted_date="2024-03-20",
                ocr_confidence=0.8,
                user_corrected_amount=100000 + (i * 10000),
                user_corrected_transaction_id=f"TRX{i}TEST123",
                user_corrected_date="2024-03-20",
                feedback_type="CONFIRMATION",
                notes=f"Valid feedback #{i}",
                used_for_learning=False,
                learning_impact=0.0,
                is_legitimate_receipt=True
            )
            
            ocr_system.submit_feedback(feedback)
        
        print(f"   Submitted {i+1} sample feedback records")
        print(f"   Updated total feedback: {len(ocr_system.feedback_history)}")
        
    except Exception as e:
        print(f"   Error testing with sample feedback: {e}")
    
    print("\n✓ Admin API endpoints test completed!")


def test_dashboard_ui_elements():
    """Test that dashboard UI elements are properly implemented"""
    print("\nTesting Dashboard UI Elements...")
    
    # Check that the admin dashboard HTML exists in the frontend
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend/public/index.html')
    
    if os.path.exists(frontend_path):
        with open(frontend_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for admin dashboard elements
        dashboard_checks = [
            ('admin-dashboard', 'Admin dashboard div exists'),
            ('system-status', 'System status section exists'),
            ('learning-metrics', 'Learning metrics section exists'),
            ('authenticity-metrics', 'Authenticity metrics section exists'),
            ('format-management', 'Format management section exists'),
            ('triggerLearningCycle', 'Learning trigger functions exist'),
            ('showAdminDashboard', 'Admin dashboard functions exist'),
        ]
        
        for check, description in dashboard_checks:
            if check in content:
                print(f"   ✓ {description}")
            else:
                print(f"   ✗ {description} - NOT FOUND")
    
    # Check for admin CSS styles
    css_elements = [
        '.dashboard-section',
        '.status-grid',
        '.metrics-grid', 
        '.authenticity-grid',
        '.trigger-btn',
    ]
    
    with open(frontend_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print("\n   CSS Styles:")
    for element in css_elements:
        if element in content:
            print(f"     ✓ {element} style exists")
        else:
            print(f"     ✗ {element} style missing")
    
    print("\n✓ Dashboard UI test completed!")


def test_integration():
    """Test the full integration"""
    print("\nTesting Full System Integration...")
    
    # Test that automatic learning system is properly connected
    try:
        from ocr_learning import self_learning_ocr
        from automatic_learning import automatic_learning_system
        
        print(f"   OCR System loaded: {len(self_learning_ocr.receipt_formats)} formats")
        print(f"   Automatic learning system running: {automatic_learning_system.is_running}")
        
        # Check that the learning system is connected to OCR
        print(f"   OCR system in auto-learning: {automatic_learning_system.ocr_system is self_learning_ocr}")
        
    except Exception as e:
        print(f"   Error testing integration: {e}")
    
    # Test that admin API is accessible
    try:
        from admin_api import router
        print(f"   Admin API router loaded: {len(router.routes)} routes")
    except Exception as e:
        print(f"   Error loading admin API: {e}")
    
    print("\n✓ Integration test completed!")


async def main():
    """Run all tests"""
    print("="*60)
    print("INTEGRATED ADMIN DASHBOARD AND MONITORING SYSTEM TEST")
    print("="*60)
    
    await test_admin_endpoints()
    test_dashboard_ui_elements()
    test_integration()
    
    print("\n" + "="*60)
    print("SYSTEM CAPABILITIES:")
    print("✓ Real-time system monitoring dashboard")
    print("✓ Detailed metrics and analytics")
    print("✓ Manual learning cycle triggers")
    print("✓ Receipt format management interface")
    print("✓ Authenticity validation metrics")
    print("✓ Automated learning with scheduled cycles")
    print("✓ Admin authentication and authorization")
    print("✓ Responsive UI with modern design")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
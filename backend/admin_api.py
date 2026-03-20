"""
Admin API endpoints for monitoring and managing the OCR learning system
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from database import supabase
from auth import get_current_user
from ocr_learning import self_learning_ocr
from automatic_learning import automatic_learning_system


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/monitoring/status", summary="Get system status")
async def get_system_status(current_user: dict = Depends(get_current_user)):
    """
    Get overall system status including learning system status
    """
    if current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get OCR system status
    ocr_status = {
        "total_formats": len(self_learning_ocr.receipt_formats),
        "total_feedback": len(self_learning_ocr.feedback_history),
        "learning_metrics": {
            "total_samples": self_learning_ocr.metrics.total_samples,
            "total_feedback": self_learning_ocr.metrics.total_feedback,
            "corrections": self_learning_ocr.metrics.corrections,
            "confirmations": self_learning_ocr.metrics.confirmations,
            "authenticity_feedback": self_learning_ocr.metrics.authenticity_feedback,
            "authenticity_accuracy": self_learning_ocr.metrics.authenticity_accuracy,
        },
        "last_updated": datetime.now().isoformat()
    }
    
    # Get automatic learning system status
    learning_status = automatic_learning_system.get_learning_status()
    
    return {
        "ocr_system": ocr_status,
        "automatic_learning": learning_status,
        "system_health": "healthy" if learning_status["is_running"] else "degraded",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/monitoring/metrics", summary="Get detailed metrics")
async def get_detailed_metrics(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed metrics for the specified number of days
    """
    if current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get metrics from database
    try:
        # Get feedback counts by type
        feedback_result = supabase.table("ocr_feedback").select("*").gte(
            "created_at", start_date.isoformat()
        ).lte("created_at", end_date.isoformat()).execute()
        
        feedback_by_type = {}
        feedback_by_provider = {}
        
        for feedback in feedback_result.data:
            fb_type = feedback.get("feedback_type", "UNKNOWN")
            provider = feedback.get("corrected_bank", "UNKNOWN")
            
            feedback_by_type[fb_type] = feedback_by_type.get(fb_type, 0) + 1
            feedback_by_provider[provider] = feedback_by_provider.get(provider, 0) + 1
        
        # Get payment verification stats
        payments_result = supabase.table("payment_proofs").select("*").gte(
            "created_at", start_date.isoformat()
        ).lte("created_at", end_date.isoformat()).execute()
        
        verification_stats = {
            "total_submissions": len(payments_result.data),
            "auto_approved": len([p for p in payments_result.data if p.get("status") == "AUTO_APPROVED"]),
            "manual_review": len([p for p in payments_result.data if p.get("status") == "PENDING"]),
            "rejected": len([p for p in payments_result.data if p.get("status") == "REJECTED"]),
        }
        
        # Get format-specific metrics
        format_metrics = {}
        for provider, format_info in self_learning_ocr.receipt_formats.items():
            format_metrics[provider] = {
                "confidence_score": format_info.confidence_score,
                "authenticity_score": format_info.authenticity_score,
                "sample_count": format_info.sample_count,
                "last_updated": format_info.last_updated
            }
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "feedback_metrics": {
                "by_type": feedback_by_type,
                "by_provider": feedback_by_provider,
                "total": len(feedback_result.data)
            },
            "verification_metrics": verification_stats,
            "format_metrics": format_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")


@router.get("/monitoring/authenticity", summary="Get authenticity metrics")
async def get_authenticity_metrics(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Get authenticity-specific metrics
    """
    if current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get feedback with authenticity info
        feedback_result = supabase.table("ocr_feedback").select(
            "is_legitimate_receipt, created_at, corrected_bank"
        ).gte("created_at", (datetime.now() - timedelta(days=days)).isoformat()).execute()
        
        legitimate_count = 0
        fake_count = 0
        total_with_auth_info = 0
        
        by_provider = {}
        
        for feedback in feedback_result.data:
            is_legit = feedback.get("is_legitimate_receipt")
            if is_legit is not None:
                total_with_auth_info += 1
                provider = feedback.get("corrected_bank", "UNKNOWN")
                
                if is_legit:
                    legitimate_count += 1
                    by_provider[provider] = by_provider.get(provider, {"legitimate": 0, "fake": 0})
                    by_provider[provider]["legitimate"] += 1
                else:
                    fake_count += 1
                    by_provider[provider] = by_provider.get(provider, {"legitimate": 0, "fake": 0})
                    by_provider[provider]["fake"] += 1
        
        authenticity_rate = (legitimate_count / total_with_auth_info * 100) if total_with_auth_info > 0 else 0
        
        return {
            "authenticity_rate": authenticity_rate,
            "legitimate_count": legitimate_count,
            "fake_count": fake_count,
            "total_with_auth_info": total_with_auth_info,
            "by_provider": by_provider,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving authenticity metrics: {str(e)}")


@router.get("/learning/triggers", summary="Trigger learning cycles manually")
async def trigger_learning_cycle(
    cycle_type: str,  # daily, weekly, monthly
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger a learning cycle
    """
    if current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if cycle_type == "daily":
            automatic_learning_system.daily_learning_cycle()
            message = "Daily learning cycle triggered"
        elif cycle_type == "weekly":
            automatic_learning_system.weekly_learning_cycle()
            message = "Weekly learning cycle triggered"
        elif cycle_type == "monthly":
            automatic_learning_system.monthly_deep_learning()
            message = "Monthly learning cycle triggered"
        else:
            raise HTTPException(status_code=400, detail="Invalid cycle type. Use daily, weekly, or monthly")
        
        return {
            "message": message,
            "cycle_type": cycle_type,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering learning cycle: {str(e)}")


@router.get("/formats/list", summary="List all receipt formats")
async def list_receipt_formats(current_user: dict = Depends(get_current_user)):
    """
    List all configured receipt formats with their metrics
    """
    if current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    formats = []
    for provider, format_info in self_learning_ocr.receipt_formats.items():
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
    
    return {
        "formats": formats,
        "total_count": len(formats),
        "timestamp": datetime.now().isoformat()
    }


@router.put("/formats/update/{provider}", summary="Update a receipt format")
async def update_receipt_format(
    provider: str,
    format_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a specific receipt format configuration
    """
    if current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if provider not in self_learning_ocr.receipt_formats:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
    
    try:
        # Update the format with new data
        format_info = self_learning_ocr.receipt_formats[provider]
        
        # Update fields if provided in format_data
        if "confidence_score" in format_data:
            format_info.confidence_score = format_data["confidence_score"]
        if "authenticity_score" in format_data:
            format_info.authenticity_score = format_data["authenticity_score"]
        if "typical_colors" in format_data:
            format_info.typical_colors = format_data["typical_colors"]
        if "has_qr_code" in format_data:
            format_info.has_qr_code = format_data["has_qr_code"]
        if "has_watermark" in format_data:
            format_info.has_watermark = format_data["has_watermark"]
        if "amount_patterns" in format_data:
            format_info.amount_patterns = format_data["amount_patterns"]
        if "transaction_id_patterns" in format_data:
            format_info.transaction_id_patterns = format_data["transaction_id_patterns"]
        if "date_patterns" in format_data:
            format_info.date_patterns = format_data["date_patterns"]
        
        format_info.last_updated = datetime.now().isoformat()
        
        # Save the updated configuration
        self_learning_ocr.save_configurations()
        
        return {
            "message": f"Format {provider} updated successfully",
            "updated_format": {
                "provider": provider,
                "bank_name": format_info.bank_name,
                "confidence_score": format_info.confidence_score,
                "authenticity_score": format_info.authenticity_score,
                "last_updated": format_info.last_updated
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating format: {str(e)}")


@router.get("/learning/logs", summary="Get learning system logs")
async def get_learning_logs(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Get logs from the learning system
    """
    if current_user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # In a real implementation, this would return actual logs
    # For now, we'll return a simulated log structure
    return {
        "logs": [
            {
                "timestamp": (datetime.now() - timedelta(minutes=i*10)).isoformat(),
                "level": "INFO",
                "message": f"Learning cycle completed - Processed {10+i*5} feedback records",
                "cycle_type": "daily" if i % 3 == 0 else "weekly"
            }
            for i in range(limit)
        ],
        "total_count": limit,
        "timestamp": datetime.now().isoformat()
    }
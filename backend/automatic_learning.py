"""
Automatic Learning System for OCR and Receipt Validation
Implements scheduled learning cycles to continuously improve the system
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import logging
from pathlib import Path
import json
import atexit

from ocr_learning import SelfLearningOCR
# PaymentValidator will be imported locally when needed to avoid dependency issues


class SimpleScheduler:
    """
    Simple scheduler implementation without external dependencies
    """
    def __init__(self):
        self.jobs = []
        self.running = False
        
    def add_job(self, interval_seconds, func, *args, **kwargs):
        """Add a job to run at specified intervals"""
        job = {
            'interval': interval_seconds,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'last_run': datetime.min,
            'enabled': True
        }
        self.jobs.append(job)
        return job
        
    def run_pending(self):
        """Run any pending jobs"""
        now = datetime.now()
        for job in self.jobs:
            if job['enabled'] and (now - job['last_run']).seconds >= job['interval']:
                try:
                    job['func'](*job['args'], **job['kwargs'])
                    job['last_run'] = now
                except Exception as e:
                    print(f"Error running job: {e}")
                    
    def start(self):
        """Start the scheduler in background"""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        
    def _run(self):
        """Internal run method"""
        while self.running:
            self.run_pending()
            time.sleep(1)  # Check every second


class AutomaticLearningSystem:
    """
    Implements scheduled learning cycles to continuously improve OCR and receipt validation
    """
    
    def __init__(self, ocr_system: SelfLearningOCR = None):
        self.ocr_system = ocr_system or SelfLearningOCR()
        self.validator = None  # Will be initialized when needed
        self.learning_scheduler = SimpleScheduler()
        self.is_running = False
        self.background_thread = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Learning parameters
        self.daily_batch_size = 100  # Number of records to process daily
        self.weekly_batch_size = 500  # Number of records to process weekly
        self.learning_threshold = 0.7  # Threshold for considering feedback significant
        
        # Initialize validator if possible
        try:
            from validators import PaymentValidator
            self.validator = PaymentValidator()
        except ImportError:
            self.logger.warning("PaymentValidator not available")
            self.validator = None
        
    def start_scheduled_learning(self):
        """Start the automatic learning scheduler"""
        if self.is_running:
            self.logger.warning("Scheduled learning is already running")
            return
            
        # Schedule daily learning (every 12 hours for testing purposes)
        # In seconds: 12 hours = 12 * 60 * 60 = 43200 seconds
        self.learning_scheduler.add_job(43200, self.daily_learning_cycle)
        
        # Schedule weekly learning (every week for testing - 7 days = 604800 seconds)
        # For testing purposes, we'll use a shorter interval
        self.learning_scheduler.add_job(86400, self.weekly_learning_cycle)  # Daily for testing
        
        # Schedule monthly deep learning (every 30 days = 2592000 seconds)
        # For testing purposes, we'll use a shorter interval
        self.learning_scheduler.add_job(172800, self.monthly_deep_learning)  # Every 2 days for testing
        
        self.is_running = True
        self.learning_scheduler.start()
        
        self.logger.info("Automatic learning scheduler started")
        
    def stop_scheduled_learning(self):
        """Stop the automatic learning scheduler"""
        self.is_running = False
        self.learning_scheduler.stop()
        self.logger.info("Automatic learning scheduler stopped")
        
    def _run_scheduler(self):
        """Run the scheduler in a background thread"""
        # This method is no longer needed since SimpleScheduler handles its own thread
        pass
            
    def daily_learning_cycle(self):
        """Daily learning cycle - process recent feedback and update models"""
        self.logger.info("Starting daily learning cycle")
        
        try:
            # Get recent feedback from the last 24 hours
            recent_feedback = self._get_recent_feedback(hours=24)
            
            if not recent_feedback:
                self.logger.info("No recent feedback to process")
                return
                
            # Process feedback and update OCR system
            processed_count = self._process_feedback_batch(recent_feedback)
            
            # Update format patterns based on recent data
            self._update_format_patterns()
            
            # Save updated configurations
            self.ocr_system.save_configurations()
            
            self.logger.info(f"Daily learning cycle completed. Processed {processed_count} feedback records")
            
        except Exception as e:
            self.logger.error(f"Error in daily learning cycle: {str(e)}")
            
    def weekly_learning_cycle(self):
        """Weekly learning cycle - deeper analysis and pattern updates"""
        self.logger.info("Starting weekly learning cycle")
        
        try:
            # Get feedback from the last week
            weekly_feedback = self._get_recent_feedback(hours=168)  # 7 days
            
            if not weekly_feedback:
                self.logger.info("No weekly feedback to process")
                return
                
            # Perform deeper analysis
            self._perform_deeper_analysis(weekly_feedback)
            
            # Update authenticity scores based on patterns
            self._update_authenticity_patterns(weekly_feedback)
            
            # Identify new pattern variations
            self._identify_new_patterns(weekly_feedback)
            
            # Save updated configurations
            self.ocr_system.save_configurations()
            
            self.logger.info(f"Weekly learning cycle completed. Processed {len(weekly_feedback)} feedback records")
            
        except Exception as e:
            self.logger.error(f"Error in weekly learning cycle: {str(e)}")
            
    def monthly_deep_learning(self):
        """Monthly deep learning cycle - comprehensive system update"""
        self.logger.info("Starting monthly deep learning cycle")
        
        try:
            # Get all feedback from the last month
            monthly_feedback = self._get_recent_feedback(hours=720)  # 30 days
            
            # Perform comprehensive analysis
            self._comprehensive_analysis(monthly_feedback)
            
            # Update all format configurations based on trends
            self._update_all_formats_with_trends(monthly_feedback)
            
            # Generate learning reports
            self._generate_learning_report(monthly_feedback)
            
            # Save updated configurations
            self.ocr_system.save_configurations()
            
            self.logger.info(f"Monthly deep learning cycle completed. Processed {len(monthly_feedback)} feedback records")
            
        except Exception as e:
            self.logger.error(f"Error in monthly deep learning cycle: {str(e)}")
            
    def _get_recent_feedback(self, hours: int = 24) -> List[Dict]:
        """Get recent feedback from database"""
        try:
            # Import database here to avoid circular imports
            from database import supabase
            
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(hours=hours)
            
            # Query feedback table for recent entries
            result = supabase.table("ocr_feedback").select("*").gte(
                "created_at", time_threshold.isoformat()
            ).limit(self.daily_batch_size).execute()
            
            return result.data if result.data else []
            
        except ImportError:
            self.logger.warning("Database module not available, returning empty feedback list")
            return []
        except Exception as e:
            self.logger.error(f"Error getting recent feedback: {str(e)}")
            return []
            
    def _process_feedback_batch(self, feedback_batch: List[Dict]) -> int:
        """Process a batch of feedback and update OCR system"""
        processed_count = 0
        
        for feedback in feedback_batch:
            try:
                # Convert feedback to UserFeedback object format
                from ocr_learning import UserFeedback
                
                user_feedback = UserFeedback(
                    feedback_id=feedback.get("id", ""),
                    payment_proof_id=feedback.get("payment_proof_id", ""),
                    timestamp=feedback.get("created_at", datetime.now().isoformat()),
                    ocr_extracted_amount=feedback.get("corrected_amount"),
                    ocr_extracted_transaction_id=feedback.get("corrected_transaction_id"),
                    ocr_extracted_date=feedback.get("corrected_date"),
                    ocr_confidence=feedback.get("ocr_confidence", 0.5),
                    user_corrected_amount=feedback.get("corrected_amount"),
                    user_corrected_transaction_id=feedback.get("corrected_transaction_id"),
                    user_corrected_date=feedback.get("corrected_date"),
                    feedback_type=feedback.get("feedback_type", "CONFIRMATION"),
                    notes=feedback.get("notes", ""),
                    used_for_learning=False,
                    learning_impact=0.0,
                    is_legitimate_receipt=feedback.get("is_legitimate_receipt")
                )
                
                # Submit feedback to OCR system
                self.ocr_system.submit_feedback(user_feedback)
                processed_count += 1
                
            except Exception as e:
                self.logger.error(f"Error processing feedback: {str(e)}")
                continue
                
        return processed_count
        
    def _update_format_patterns(self):
        """Update format patterns based on recent learning"""
        for provider, format_info in self.ocr_system.receipt_formats.items():
            try:
                # Get recent examples for this provider
                recent_examples = self._get_recent_examples_for_provider(provider)
                
                if recent_examples:
                    # Update format characteristics based on recent data
                    self._update_format_characteristics(format_info, recent_examples)
                    
            except Exception as e:
                self.logger.error(f"Error updating format patterns for {provider}: {str(e)}")
                
    def _get_recent_examples_for_provider(self, provider: str) -> List[Dict]:
        """Get recent examples for a specific provider"""
        try:
            # Import database here to avoid circular imports
            from database import supabase
            
            # Query payment_proofs for recent examples of this provider
            result = supabase.table("payment_proofs").select(
                "ocr_extracted_amount, ocr_extracted_transaction_id, ocr_extracted_date, ocr_confidence"
            ).eq("bank_name", provider).gte(
                "created_at", (datetime.now() - timedelta(days=7)).isoformat()
            ).limit(50).execute()
            
            return result.data if result.data else []
            
        except ImportError:
            self.logger.warning("Database module not available")
            return []
        except Exception as e:
            self.logger.error(f"Error getting examples for {provider}: {str(e)}")
            return []
            
    def _update_format_characteristics(self, format_info, examples: List[Dict]):
        """Update format characteristics based on recent examples"""
        if not examples:
            return
            
        # Update sample count
        format_info.sample_count += len(examples)
        
        # Calculate average confidence from recent examples
        confidences = [ex.get('ocr_confidence', 0.5) for ex in examples if ex.get('ocr_confidence')]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            # Update confidence score with weighted average
            format_info.confidence_score = (format_info.confidence_score + avg_confidence) / 2
            
        # Update last updated timestamp
        format_info.last_updated = datetime.now().isoformat()
        
    def _perform_deeper_analysis(self, feedback_batch: List[Dict]):
        """Perform deeper analysis on feedback batch"""
        # Group feedback by provider
        provider_feedback = {}
        for fb in feedback_batch:
            provider = self._get_provider_from_feedback(fb)
            if provider not in provider_feedback:
                provider_feedback[provider] = []
            provider_feedback[provider].append(fb)
            
        # Analyze each provider separately
        for provider, provider_fb in provider_feedback.items():
            self._analyze_provider_feedback(provider, provider_fb)
            
    def _get_provider_from_feedback(self, feedback: Dict) -> str:
        """Extract provider from feedback record"""
        # Try to get provider from payment proof
        try:
            # Import database here to avoid circular imports
            from database import supabase
            
            payment_id = feedback.get("payment_proof_id")
            if payment_id:
                payment_result = supabase.table("payment_proofs").select("bank_name").eq("id", payment_id).execute()
                if payment_result.data:
                    return payment_result.data[0].get("bank_name", "UNKNOWN")
        except ImportError:
            # If database is not available, try to extract from feedback directly
            try:
                # Attempt to get bank_name from feedback if available
                if 'bank_name' in feedback:
                    return feedback['bank_name']
            except:
                pass
        except Exception:
            pass
            
        return "UNKNOWN"
        
    def _analyze_provider_feedback(self, provider: str, feedback_list: List[Dict]):
        """Analyze feedback for a specific provider"""
        if provider == "UNKNOWN":
            return
            
        # Calculate correction rate for this provider
        correction_count = sum(1 for fb in feedback_list if fb.get("feedback_type") == "CORRECTION")
        total_count = len(feedback_list)
        
        if total_count > 0:
            correction_rate = correction_count / total_count
            
            # Update format's authenticity score based on correction rate
            if provider in self.ocr_system.receipt_formats:
                format_info = self.ocr_system.receipt_formats[provider]
                
                # Lower correction rate means higher authenticity
                authenticity_adjustment = (1 - correction_rate) * 0.1
                format_info.authenticity_score = min(1.0, max(0.0, 
                    format_info.authenticity_score + authenticity_adjustment))
                    
    def _update_authenticity_patterns(self, feedback_batch: List[Dict]):
        """Update authenticity patterns based on feedback"""
        # Count legitimate vs fake receipts by provider
        provider_legitimate_counts = {}
        provider_total_counts = {}
        
        for fb in feedback_batch:
            provider = self._get_provider_from_feedback(fb)
            is_legitimate = fb.get("is_legitimate_receipt")
            
            if provider not in provider_legitimate_counts:
                provider_legitimate_counts[provider] = 0
                provider_total_counts[provider] = 0
                
            provider_total_counts[provider] += 1
            if is_legitimate:
                provider_legitimate_counts[provider] += 1
                
        # Update authenticity scores for each provider
        for provider in provider_legitimate_counts:
            if provider_total_counts[provider] > 0 and provider in self.ocr_system.receipt_formats:
                legit_rate = provider_legitimate_counts[provider] / provider_total_counts[provider]
                format_info = self.ocr_system.receipt_formats[provider]
                
                # Weighted update of authenticity score
                format_info.authenticity_score = (format_info.authenticity_score * 0.7) + (legit_rate * 0.3)
                
    def _identify_new_patterns(self, feedback_batch: List[Dict]):
        """Identify new patterns from feedback data"""
        # This would typically involve more complex pattern recognition
        # For now, we'll just look for common corrections
        for fb in feedback_batch:
            # Look for common correction patterns
            corrected_amount = fb.get("corrected_amount")
            corrected_tx_id = fb.get("corrected_transaction_id")
            
            if corrected_amount and corrected_tx_id:
                # Could implement pattern recognition here
                pass
                
    def _comprehensive_analysis(self, feedback_batch: List[Dict]):
        """Perform comprehensive analysis on feedback"""
        # Calculate overall system metrics
        total_feedback = len(feedback_batch)
        if total_feedback == 0:
            return
            
        # Calculate various metrics
        corrections = sum(1 for fb in feedback_batch if fb.get("feedback_type") == "CORRECTION")
        confirmations = sum(1 for fb in feedback_batch if fb.get("feedback_type") == "CONFIRMATION")
        flags = sum(1 for fb in feedback_batch if fb.get("feedback_type") == "FLAG")
        
        legitimate_receipts = sum(1 for fb in feedback_batch if fb.get("is_legitimate_receipt") is True)
        fake_receipts = sum(1 for fb in feedback_batch if fb.get("is_legitimate_receipt") is False)
        
        # Update global metrics
        self.ocr_system.metrics.total_feedback += total_feedback
        self.ocr_system.metrics.corrections += corrections
        self.ocr_system.metrics.confirmations += confirmations
        
        # Update authenticity metrics
        if legitimate_receipts + fake_receipts > 0:
            self.ocr_system.metrics.authenticity_accuracy = legitimate_receipts / (legitimate_receipts + fake_receipts)
            
    def _update_all_formats_with_trends(self, feedback_batch: List[Dict]):
        """Update all formats based on identified trends"""
        # Group feedback by provider and analyze trends
        provider_trends = {}
        
        for fb in feedback_batch:
            provider = self._get_provider_from_feedback(fb)
            if provider not in provider_trends:
                provider_trends[provider] = {
                    'feedback_count': 0,
                    'correction_count': 0,
                    'legitimate_count': 0,
                    'avg_confidence': 0.0
                }
                
            trend = provider_trends[provider]
            trend['feedback_count'] += 1
            
            if fb.get("feedback_type") == "CORRECTION":
                trend['correction_count'] += 1
                
            if fb.get("is_legitimate_receipt") is True:
                trend['legitimate_count'] += 1
                
            if fb.get("ocr_confidence"):
                trend['avg_confidence'] += fb.get("ocr_confidence")
                
        # Calculate averages and update formats
        for provider, trend in provider_trends.items():
            if provider in self.ocr_system.receipt_formats:
                format_info = self.ocr_system.receipt_formats[provider]
                
                # Update based on trends
                if trend['feedback_count'] > 0:
                    correction_rate = trend['correction_count'] / trend['feedback_count']
                    legitimate_rate = trend['legitimate_count'] / trend['feedback_count']
                    
                    # Adjust confidence based on correction rate
                    format_info.confidence_score = max(0.1, min(0.9, 
                        format_info.confidence_score - (correction_rate * 0.2)))
                        
                    # Adjust authenticity based on legitimate rate
                    format_info.authenticity_score = max(0.1, min(0.9,
                        (format_info.authenticity_score * 0.7) + (legitimate_rate * 0.3)))
                        
    def _generate_learning_report(self, feedback_batch: List[Dict]):
        """Generate a learning report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_feedback_processed": len(feedback_batch),
            "learning_cycles_completed": 1,
            "system_improvements": []
        }
        
        # Save report to file
        report_file = Path(self.ocr_system.config_dir) / f"learning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Learning report generated: {report_file}")
        
    def get_learning_status(self) -> Dict:
        """Get current learning system status"""
        return {
            "is_running": self.is_running,
            "scheduled_jobs": len(self.learning_scheduler.jobs) if hasattr(self.learning_scheduler, 'jobs') else 0,
            "last_daily_run": getattr(self, '_last_daily_run', None),
            "last_weekly_run": getattr(self, '_last_weekly_run', None),
            "last_monthly_run": getattr(self, '_last_monthly_run', None)
        }


# Global instance
automatic_learning_system = AutomaticLearningSystem()


def start_automatic_learning():
    """Start the automatic learning system"""
    automatic_learning_system.start_scheduled_learning()


def stop_automatic_learning():
    """Stop the automatic learning system"""
    automatic_learning_system.stop_scheduled_learning()


if __name__ == "__main__":
    # Example usage
    print("Starting automatic learning system...")
    start_automatic_learning()
    
    try:
        # Keep the program running
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping automatic learning system...")
        stop_automatic_learning()
        print("System stopped.")
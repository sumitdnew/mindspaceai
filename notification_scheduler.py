#!/usr/bin/env python3
"""
Notification Scheduler
Manages timing and delivery of intelligent notifications based on patient patterns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
import asyncio
from sqlalchemy import and_, func, desc, extract
from sqlalchemy.orm import joinedload

from app_ml_complete import (
    db, Patient, ExerciseSession, MoodEntry, PHQ9Assessment, 
    NotificationSettings, EngagementMetrics
)
from intelligent_notification_system import intelligent_notification_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Manages scheduling and delivery of intelligent notifications"""
    
    def __init__(self):
        self.scheduled_notifications = {}
        self.emergency_contacts = {}
        self.provider_alert_queue = []
        
        # Notification delivery channels
        self.delivery_channels = {
            'in_app': True,
            'email': False,  # Would be configured per patient
            'sms': False,    # Would be configured per patient
            'push': False    # Would be configured per patient
        }
        
        # Timing constraints
        self.timing_constraints = {
            'quiet_hours_start': 22,  # 10 PM
            'quiet_hours_end': 8,     # 8 AM
            'min_interval_minutes': 30,
            'max_daily_notifications': 5,
            'escalation_override_quiet_hours': True
        }

    def schedule_patient_notifications(self, patient_id: int) -> Dict:
        """Schedule notifications for a specific patient"""
        try:
            # Get patient's notification settings
            settings = NotificationSettings.query.filter_by(patient_id=patient_id).first()
            
            # Generate adaptive notification
            notification = intelligent_notification_system.generate_adaptive_notification(patient_id)
            
            if 'error' in notification:
                return notification
            
            # Calculate delivery timing
            delivery_timing = self._calculate_delivery_timing(patient_id, notification, settings)
            
            # Schedule the notification
            scheduled_notification = {
                'patient_id': patient_id,
                'notification': notification,
                'delivery_timing': delivery_timing,
                'scheduled_time': delivery_timing['next_delivery_time'],
                'priority': notification['priority'],
                'escalation_level': notification['escalation_level'],
                'created_at': datetime.now()
            }
            
            # Store in memory (in production, this would be in a database)
            self.scheduled_notifications[patient_id] = scheduled_notification
            
            # Check if provider alert is needed
            if notification.get('provider_alert_needed'):
                self._queue_provider_alert(patient_id, notification)
            
            return {
                'success': True,
                'scheduled_notification': scheduled_notification,
                'message': f"Notification scheduled for {delivery_timing['next_delivery_time']}"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling patient notifications: {str(e)}")
            return {'error': f'Notification scheduling failed: {str(e)}'}

    def _calculate_delivery_timing(self, patient_id: int, notification: Dict, settings: NotificationSettings) -> Dict:
        """Calculate optimal delivery timing for notification"""
        try:
            current_time = datetime.now()
            optimal_timing = notification['optimal_timing']
            escalation_level = notification['escalation_level']
            
            # Base delivery time from optimal timing
            base_delivery_time = optimal_timing['next_optimal_time']
            
            # Apply escalation timing adjustments
            if escalation_level == 'crisis':
                # Crisis notifications override all timing constraints
                delivery_time = current_time + timedelta(minutes=5)
            elif escalation_level == 'urgent':
                # Urgent notifications within 30 minutes
                delivery_time = current_time + timedelta(minutes=30)
            elif escalation_level == 'concerned':
                # Concerned notifications within 2 hours
                delivery_time = current_time + timedelta(hours=2)
            else:
                # Normal notifications use optimal timing
                delivery_time = base_delivery_time
            
            # Apply quiet hours constraint (unless escalation overrides)
            if not self.timing_constraints['escalation_override_quiet_hours'] or escalation_level == 'gentle':
                delivery_time = self._adjust_for_quiet_hours(delivery_time)
            
            # Apply minimum interval constraint
            delivery_time = self._apply_minimum_interval(patient_id, delivery_time)
            
            # Apply daily limit constraint
            delivery_time = self._apply_daily_limit(patient_id, delivery_time)
            
            return {
                'next_delivery_time': delivery_time,
                'delay_minutes': (delivery_time - current_time).total_seconds() / 60,
                'escalation_override': escalation_level in ['crisis', 'urgent'],
                'quiet_hours_adjusted': delivery_time != base_delivery_time
            }
            
        except Exception as e:
            logger.error(f"Error calculating delivery timing: {str(e)}")
            return {
                'next_delivery_time': datetime.now() + timedelta(hours=2),
                'delay_minutes': 120,
                'escalation_override': False,
                'quiet_hours_adjusted': False
            }

    def _adjust_for_quiet_hours(self, delivery_time: datetime) -> datetime:
        """Adjust delivery time to avoid quiet hours"""
        try:
            quiet_start = self.timing_constraints['quiet_hours_start']
            quiet_end = self.timing_constraints['quiet_hours_end']
            
            delivery_hour = delivery_time.hour
            
            # Check if delivery time falls in quiet hours
            if delivery_hour >= quiet_start or delivery_hour < quiet_end:
                # Move to next available time
                if delivery_hour >= quiet_start:
                    # Move to next morning
                    next_day = delivery_time + timedelta(days=1)
                    delivery_time = next_day.replace(hour=quiet_end, minute=0, second=0, microsecond=0)
                else:
                    # Move to later today
                    delivery_time = delivery_time.replace(hour=quiet_end, minute=0, second=0, microsecond=0)
            
            return delivery_time
            
        except Exception as e:
            logger.error(f"Error adjusting for quiet hours: {str(e)}")
            return delivery_time

    def _apply_minimum_interval(self, patient_id: int, delivery_time: datetime) -> datetime:
        """Apply minimum interval between notifications"""
        try:
            min_interval = self.timing_constraints['min_interval_minutes']
            
            # Check last notification time
            last_notification = self.scheduled_notifications.get(patient_id)
            if last_notification:
                last_time = last_notification['scheduled_time']
                min_next_time = last_time + timedelta(minutes=min_interval)
                
                if delivery_time < min_next_time:
                    delivery_time = min_next_time
            
            return delivery_time
            
        except Exception as e:
            logger.error(f"Error applying minimum interval: {str(e)}")
            return delivery_time

    def _apply_daily_limit(self, patient_id: int, delivery_time: datetime) -> datetime:
        """Apply daily notification limit"""
        try:
            max_daily = self.timing_constraints['max_daily_notifications']
            
            # Count notifications today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_notifications = 0
            
            for scheduled in self.scheduled_notifications.values():
                if (scheduled['patient_id'] == patient_id and 
                    scheduled['scheduled_time'] >= today_start):
                    today_notifications += 1
            
            # If limit reached, move to tomorrow
            if today_notifications >= max_daily:
                tomorrow = delivery_time + timedelta(days=1)
                delivery_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
            
            return delivery_time
            
        except Exception as e:
            logger.error(f"Error applying daily limit: {str(e)}")
            return delivery_time

    def _queue_provider_alert(self, patient_id: int, notification: Dict):
        """Queue provider alert for escalation situations"""
        try:
            alert_data = {
                'patient_id': patient_id,
                'escalation_level': notification['escalation_level'],
                'priority': notification['priority'],
                'message': notification['message'],
                'timestamp': datetime.now(),
                'requires_immediate_action': notification['escalation_level'] in ['urgent', 'crisis']
            }
            
            self.provider_alert_queue.append(alert_data)
            
            # Trigger immediate alert for crisis situations
            if notification['escalation_level'] == 'crisis':
                self._trigger_immediate_provider_alert(patient_id, alert_data)
                
        except Exception as e:
            logger.error(f"Error queuing provider alert: {str(e)}")

    def _trigger_immediate_provider_alert(self, patient_id: int, alert_data: Dict):
        """Trigger immediate provider alert for crisis situations"""
        try:
            # In a real system, this would send immediate notifications to providers
            logger.critical(f"IMMEDIATE PROVIDER ALERT: Patient {patient_id} - {alert_data['escalation_level']} escalation")
            
            # Trigger the alert through the intelligent notification system
            result = intelligent_notification_system.trigger_provider_alert(
                patient_id, 
                alert_data['escalation_level'], 
                f"Patient missed {alert_data.get('days_missed', 5)}+ days of exercises"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error triggering immediate provider alert: {str(e)}")
            return {'error': f'Immediate alert failed: {str(e)}'}

    def get_scheduled_notifications(self, patient_id: Optional[int] = None) -> List[Dict]:
        """Get all scheduled notifications or for specific patient"""
        try:
            if patient_id:
                notification = self.scheduled_notifications.get(patient_id)
                return [notification] if notification else []
            else:
                return list(self.scheduled_notifications.values())
                
        except Exception as e:
            logger.error(f"Error getting scheduled notifications: {str(e)}")
            return []

    def cancel_notification(self, patient_id: int) -> Dict:
        """Cancel scheduled notification for patient"""
        try:
            if patient_id in self.scheduled_notifications:
                cancelled = self.scheduled_notifications.pop(patient_id)
                return {
                    'success': True,
                    'message': f"Notification cancelled for patient {patient_id}",
                    'cancelled_notification': cancelled
                }
            else:
                return {
                    'success': False,
                    'message': f"No scheduled notification found for patient {patient_id}"
                }
                
        except Exception as e:
            logger.error(f"Error cancelling notification: {str(e)}")
            return {'error': f'Notification cancellation failed: {str(e)}'}

    def reschedule_notification(self, patient_id: int, new_time: datetime) -> Dict:
        """Reschedule notification for different time"""
        try:
            if patient_id not in self.scheduled_notifications:
                return {'error': f'No scheduled notification found for patient {patient_id}'}
            
            # Update the scheduled time
            self.scheduled_notifications[patient_id]['scheduled_time'] = new_time
            self.scheduled_notifications[patient_id]['delivery_timing']['next_delivery_time'] = new_time
            
            return {
                'success': True,
                'message': f"Notification rescheduled for {new_time}",
                'updated_notification': self.scheduled_notifications[patient_id]
            }
            
        except Exception as e:
            logger.error(f"Error rescheduling notification: {str(e)}")
            return {'error': f'Notification rescheduling failed: {str(e)}'}

    def get_provider_alerts(self, include_resolved: bool = False) -> List[Dict]:
        """Get queued provider alerts"""
        try:
            if include_resolved:
                return self.provider_alert_queue
            else:
                # Filter out resolved alerts (in a real system, alerts would have status)
                return [alert for alert in self.provider_alert_queue 
                       if alert.get('requires_immediate_action', False)]
                
        except Exception as e:
            logger.error(f"Error getting provider alerts: {str(e)}")
            return []

    def resolve_provider_alert(self, patient_id: int) -> Dict:
        """Mark provider alert as resolved"""
        try:
            # Remove alert from queue
            self.provider_alert_queue = [
                alert for alert in self.provider_alert_queue 
                if alert['patient_id'] != patient_id
            ]
            
            return {
                'success': True,
                'message': f"Provider alert resolved for patient {patient_id}"
            }
            
        except Exception as e:
            logger.error(f"Error resolving provider alert: {str(e)}")
            return {'error': f'Alert resolution failed: {str(e)}'}

    def update_emergency_contacts(self, patient_id: int, contacts: List[Dict]) -> Dict:
        """Update emergency contacts for patient"""
        try:
            self.emergency_contacts[patient_id] = contacts
            
            return {
                'success': True,
                'message': f"Emergency contacts updated for patient {patient_id}",
                'contacts': contacts
            }
            
        except Exception as e:
            logger.error(f"Error updating emergency contacts: {str(e)}")
            return {'error': f'Emergency contact update failed: {str(e)}'}

    def get_notification_summary(self, patient_id: int) -> Dict:
        """Get comprehensive notification summary for patient"""
        try:
            # Get scheduled notification
            scheduled = self.scheduled_notifications.get(patient_id)
            
            # Get notification analytics
            analytics = intelligent_notification_system.get_notification_analytics(patient_id)
            
            # Get provider alerts
            alerts = [alert for alert in self.provider_alert_queue 
                     if alert['patient_id'] == patient_id]
            
            return {
                'scheduled_notification': scheduled,
                'analytics': analytics,
                'provider_alerts': alerts,
                'emergency_contacts': self.emergency_contacts.get(patient_id, []),
                'summary': {
                    'has_scheduled': scheduled is not None,
                    'alert_count': len(alerts),
                    'escalation_level': scheduled['escalation_level'] if scheduled else 'none',
                    'next_delivery': scheduled['scheduled_time'] if scheduled else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting notification summary: {str(e)}")
            return {'error': f'Summary generation failed: {str(e)}'}

    def bulk_schedule_notifications(self, patient_ids: List[int]) -> Dict:
        """Schedule notifications for multiple patients"""
        try:
            results = []
            successful = 0
            failed = 0
            
            for patient_id in patient_ids:
                result = self.schedule_patient_notifications(patient_id)
                results.append({'patient_id': patient_id, 'result': result})
                
                if 'error' in result:
                    failed += 1
                else:
                    successful += 1
            
            return {
                'success': True,
                'total_patients': len(patient_ids),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error in bulk scheduling: {str(e)}")
            return {'error': f'Bulk scheduling failed: {str(e)}'}

    def cleanup_expired_notifications(self) -> Dict:
        """Clean up expired notifications"""
        try:
            current_time = datetime.now()
            expired_count = 0
            
            # Remove notifications older than 24 hours
            expired_notifications = []
            for patient_id, notification in self.scheduled_notifications.items():
                if (current_time - notification['created_at']).days >= 1:
                    expired_notifications.append(patient_id)
                    expired_count += 1
            
            # Remove expired notifications
            for patient_id in expired_notifications:
                self.scheduled_notifications.pop(patient_id, None)
            
            return {
                'success': True,
                'expired_count': expired_count,
                'remaining_count': len(self.scheduled_notifications),
                'message': f"Cleaned up {expired_count} expired notifications"
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {str(e)}")
            return {'error': f'Cleanup failed: {str(e)}'}

# Initialize the notification scheduler
notification_scheduler = NotificationScheduler()

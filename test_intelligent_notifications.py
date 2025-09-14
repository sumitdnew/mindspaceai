#!/usr/bin/env python3
"""
Test Intelligent Notification System
Comprehensive testing and demonstration of the intelligent notification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import json
import logging

from intelligent_notification_system import intelligent_notification_system
from notification_scheduler import notification_scheduler
from intelligent_notification_integration import intelligent_notification_integration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_adaptive_notification_generation():
    """Test adaptive notification generation for different patient scenarios"""
    print("\n" + "="*60)
    print("TESTING ADAPTIVE NOTIFICATION GENERATION")
    print("="*60)
    
    # Test with different patient IDs (assuming they exist in the database)
    test_patients = [1, 2, 3]  # Adjust based on your database
    
    for patient_id in test_patients:
        print(f"\n--- Testing Patient {patient_id} ---")
        
        try:
            # Generate adaptive notification
            notification = intelligent_notification_system.generate_adaptive_notification(patient_id)
            
            if 'error' in notification:
                print(f"❌ Error: {notification['error']}")
                continue
            
            print(f"✅ Notification generated successfully")
            print(f"   Message: {notification['message']}")
            print(f"   Escalation Level: {notification['escalation_level']}")
            print(f"   Priority: {notification['priority']}")
            print(f"   Provider Alert Needed: {notification['provider_alert_needed']}")
            
            # Show timing information
            timing = notification['optimal_timing']
            print(f"   Next Optimal Time: {timing['next_optimal_time']}")
            print(f"   Delay Hours: {timing['delay_hours']:.2f}")
            print(f"   Optimal Hours: {timing['optimal_hours']}")
            print(f"   Busy Hours: {timing['busy_hours']}")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def test_escalation_protocols():
    """Test escalation protocols for different scenarios"""
    print("\n" + "="*60)
    print("TESTING ESCALATION PROTOCOLS")
    print("="*60)
    
    # Test different escalation scenarios
    escalation_scenarios = [
        {'patient_id': 1, 'description': 'Normal engagement'},
        {'patient_id': 2, 'description': 'Missed 2 days'},
        {'patient_id': 3, 'description': 'High risk patient'}
    ]
    
    for scenario in escalation_scenarios:
        patient_id = scenario['patient_id']
        print(f"\n--- {scenario['description']} (Patient {patient_id}) ---")
        
        try:
            # Generate notification to see escalation level
            notification = intelligent_notification_system.generate_adaptive_notification(patient_id)
            
            if 'error' in notification:
                print(f"❌ Error: {notification['error']}")
                continue
            
            escalation_level = notification['escalation_level']
            print(f"✅ Escalation Level: {escalation_level}")
            
            # Test provider alert if needed
            if notification['provider_alert_needed']:
                alert_result = intelligent_notification_system.trigger_provider_alert(
                    patient_id, 
                    escalation_level, 
                    f"Test escalation for {scenario['description']}"
                )
                
                if 'error' in alert_result:
                    print(f"❌ Alert Error: {alert_result['error']}")
                else:
                    print(f"✅ Provider Alert Triggered: {alert_result['message']}")
            
            # Show escalation details
            escalation_config = intelligent_notification_system.escalation_levels.get(escalation_level, {})
            print(f"   Tone: {escalation_config.get('tone', 'unknown')}")
            print(f"   Frequency: {escalation_config.get('frequency', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def test_motivational_messaging():
    """Test motivational messaging system"""
    print("\n" + "="*60)
    print("TESTING MOTIVATIONAL MESSAGING")
    print("="*60)
    
    # Test different motivational message types
    message_types = [
        'milestone_achievements',
        'progress_celebrations', 
        'educational_content',
        'phq9_connections'
    ]
    
    for message_type in message_types:
        print(f"\n--- {message_type.replace('_', ' ').title()} ---")
        
        messages = intelligent_notification_system.motivational_messages.get(message_type, [])
        
        for i, message_template in enumerate(messages[:2]):  # Show first 2 examples
            print(f"   {i+1}. {message_template}")
    
    # Test personalized message generation
    print(f"\n--- Personalized Message Generation ---")
    
    test_patients = [1, 2, 3]
    for patient_id in test_patients:
        try:
            notification = intelligent_notification_system.generate_adaptive_notification(patient_id)
            
            if 'error' not in notification:
                print(f"   Patient {patient_id}: {notification['message']}")
            
        except Exception as e:
            print(f"   Patient {patient_id}: Error - {str(e)}")

def test_notification_scheduling():
    """Test notification scheduling system"""
    print("\n" + "="*60)
    print("TESTING NOTIFICATION SCHEDULING")
    print("="*60)
    
    test_patients = [1, 2, 3]
    
    for patient_id in test_patients:
        print(f"\n--- Scheduling for Patient {patient_id} ---")
        
        try:
            # Schedule notification
            schedule_result = notification_scheduler.schedule_patient_notifications(patient_id)
            
            if 'error' in schedule_result:
                print(f"❌ Scheduling Error: {schedule_result['error']}")
                continue
            
            print(f"✅ Notification scheduled successfully")
            
            scheduled_notification = schedule_result['scheduled_notification']
            print(f"   Scheduled Time: {scheduled_notification['scheduled_time']}")
            print(f"   Priority: {scheduled_notification['priority']}")
            print(f"   Escalation Level: {scheduled_notification['escalation_level']}")
            
            # Test notification management
            print(f"\n   --- Notification Management ---")
            
            # Get scheduled notifications
            scheduled = notification_scheduler.get_scheduled_notifications(patient_id)
            print(f"   Scheduled Count: {len(scheduled)}")
            
            # Get notification summary
            summary = notification_scheduler.get_notification_summary(patient_id)
            if 'error' not in summary:
                summary_data = summary['summary']
                print(f"   Has Scheduled: {summary_data['has_scheduled']}")
                print(f"   Alert Count: {summary_data['alert_count']}")
                print(f"   Escalation Level: {summary_data['escalation_level']}")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def test_integration_system():
    """Test the comprehensive integration system"""
    print("\n" + "="*60)
    print("TESTING INTEGRATION SYSTEM")
    print("="*60)
    
    test_patients = [1, 2, 3]
    
    for patient_id in test_patients:
        print(f"\n--- Integration Test for Patient {patient_id} ---")
        
        try:
            # Process complete notification cycle
            cycle_result = intelligent_notification_integration.process_patient_notification_cycle(patient_id)
            
            if 'error' in cycle_result:
                print(f"❌ Cycle Error: {cycle_result['error']}")
                continue
            
            print(f"✅ Notification cycle completed successfully")
            
            # Show patient state
            patient_state = cycle_result['patient_state']
            if 'error' not in patient_state:
                metrics = patient_state.get('metrics', {})
                print(f"   Completion Rate: {metrics.get('completion_rate', 0):.2%}")
                print(f"   Engagement Level: {metrics.get('engagement_level', 'unknown')}")
                print(f"   Risk Level: {metrics.get('risk_level', 'unknown')}")
                
                mood_trend = metrics.get('mood_trend', {})
                print(f"   Mood Trend: {mood_trend.get('trend', 'unknown')}")
            
            # Show provider alerts
            provider_alerts = cycle_result['provider_alerts']
            if provider_alerts:
                print(f"   Provider Alerts: {len(provider_alerts)}")
                for alert in provider_alerts:
                    print(f"     - {alert['type']}: {alert['reason']} ({alert['priority']})")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def test_comprehensive_reporting():
    """Test comprehensive reporting features"""
    print("\n" + "="*60)
    print("TESTING COMPREHENSIVE REPORTING")
    print("="*60)
    
    test_patients = [1, 2, 3]
    
    for patient_id in test_patients:
        print(f"\n--- Comprehensive Report for Patient {patient_id} ---")
        
        try:
            # Get comprehensive notification report
            report = intelligent_notification_integration.get_comprehensive_notification_report(patient_id)
            
            if 'error' in report:
                print(f"❌ Report Error: {report['error']}")
                continue
            
            print(f"✅ Comprehensive report generated")
            
            # Show key report sections
            if 'patient_state' in report and 'error' not in report['patient_state']:
                patient_info = report['patient_state'].get('patient_info', {})
                print(f"   Patient: {patient_info.get('name', 'Unknown')}")
                print(f"   Severity: {patient_info.get('severity_level', 'Unknown')}")
            
            if 'recommendations' in report:
                recommendations = report['recommendations']
                print(f"   Recommendations: {len(recommendations)}")
                for i, rec in enumerate(recommendations[:3]):  # Show first 3
                    print(f"     {i+1}. {rec}")
            
            # Show analytics
            if 'notification_analytics' in report and 'error' not in report['notification_analytics']:
                analytics = report['notification_analytics']
                settings = analytics.get('notification_settings', {})
                print(f"   Frequency Type: {settings.get('frequency_type', 'Unknown')}")
                
                engagement = analytics.get('engagement_metrics', {})
                print(f"   Completion Rate: {engagement.get('completion_rate', 0):.2%}")
                print(f"   Current Streak: {engagement.get('current_streak', 0)} days")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def test_system_health():
    """Test system health monitoring"""
    print("\n" + "="*60)
    print("TESTING SYSTEM HEALTH MONITORING")
    print("="*60)
    
    try:
        # Get system health report
        health_report = intelligent_notification_integration.get_system_health_report()
        
        if 'error' in health_report:
            print(f"❌ Health Report Error: {health_report['error']}")
            return
        
        print(f"✅ System Health Report Generated")
        
        # Show system metrics
        metrics = health_report.get('metrics', {})
        print(f"   Total Patients: {metrics.get('total_patients', 0)}")
        print(f"   Active Patients: {metrics.get('active_patients', 0)}")
        print(f"   Scheduled Notifications: {metrics.get('scheduled_notifications', 0)}")
        print(f"   Provider Alerts: {metrics.get('provider_alerts', 0)}")
        print(f"   Critical Alerts: {metrics.get('critical_alerts', 0)}")
        
        # Show configuration
        config = health_report.get('configuration', {})
        print(f"   Auto Schedule Enabled: {config.get('auto_schedule_enabled', False)}")
        print(f"   Provider Alert Threshold: {config.get('provider_alert_threshold', 0)} days")
        print(f"   Crisis Escalation Threshold: {config.get('crisis_escalation_threshold', 0)} days")
        
        # Show system status
        print(f"   System Status: {health_report.get('system_status', 'Unknown')}")
        print(f"   Last Updated: {health_report.get('last_updated', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_emergency_features():
    """Test emergency notification features"""
    print("\n" + "="*60)
    print("TESTING EMERGENCY FEATURES")
    print("="*60)
    
    test_patients = [1, 2, 3]
    
    for patient_id in test_patients:
        print(f"\n--- Emergency Test for Patient {patient_id} ---")
        
        try:
            # Test emergency notification override
            emergency_result = intelligent_notification_integration.emergency_notification_override(
                patient_id,
                "Test emergency notification - patient safety check required",
                "critical"
            )
            
            if 'error' in emergency_result:
                print(f"❌ Emergency Error: {emergency_result['error']}")
                continue
            
            print(f"✅ Emergency notification triggered successfully")
            print(f"   Message: {emergency_result['emergency_notification']['message']}")
            print(f"   Priority: {emergency_result['emergency_notification']['priority']}")
            
            # Test provider alert resolution
            resolve_result = notification_scheduler.resolve_provider_alert(patient_id)
            
            if 'error' in resolve_result:
                print(f"❌ Resolution Error: {resolve_result['error']}")
            else:
                print(f"✅ Provider alert resolved: {resolve_result['message']}")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def test_bulk_operations():
    """Test bulk notification operations"""
    print("\n" + "="*60)
    print("TESTING BULK OPERATIONS")
    print("="*60)
    
    test_patients = [1, 2, 3]
    
    try:
        # Test bulk notification processing
        print(f"\n--- Bulk Notification Processing ---")
        bulk_result = intelligent_notification_integration.bulk_process_notifications(test_patients)
        
        if 'error' in bulk_result:
            print(f"❌ Bulk Processing Error: {bulk_result['error']}")
        else:
            print(f"✅ Bulk processing completed")
            print(f"   Total Patients: {bulk_result['total_patients']}")
            print(f"   Successful: {bulk_result['successful']}")
            print(f"   Failed: {bulk_result['failed']}")
        
        # Test bulk scheduling
        print(f"\n--- Bulk Notification Scheduling ---")
        bulk_schedule_result = notification_scheduler.bulk_schedule_notifications(test_patients)
        
        if 'error' in bulk_schedule_result:
            print(f"❌ Bulk Scheduling Error: {bulk_schedule_result['error']}")
        else:
            print(f"✅ Bulk scheduling completed")
            print(f"   Total Patients: {bulk_schedule_result['total_patients']}")
            print(f"   Successful: {bulk_schedule_result['successful']}")
            print(f"   Failed: {bulk_schedule_result['failed']}")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Run all tests"""
    print("🧠 INTELLIGENT NOTIFICATION SYSTEM TEST SUITE")
    print("="*60)
    print("Testing comprehensive notification and reminder system")
    print("="*60)
    
    # Run all test functions
    test_functions = [
        test_adaptive_notification_generation,
        test_escalation_protocols,
        test_motivational_messaging,
        test_notification_scheduling,
        test_integration_system,
        test_comprehensive_reporting,
        test_system_health,
        test_emergency_features,
        test_bulk_operations
    ]
    
    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print(f"\n❌ Test {test_func.__name__} failed: {str(e)}")
    
    print("\n" + "="*60)
    print("🎉 INTELLIGENT NOTIFICATION SYSTEM TEST COMPLETE")
    print("="*60)
    print("All tests completed. Check results above for any errors.")
    print("="*60)

if __name__ == "__main__":
    main()

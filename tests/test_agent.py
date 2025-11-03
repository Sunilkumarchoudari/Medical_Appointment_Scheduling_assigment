"""
Test cases for the Medical Appointment Scheduling Agent
"""
import pytest
import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.calendly_integration import calendly_api
from backend.tools.availability_tool import check_availability, suggest_slots
from backend.tools.booking_tool import book_appointment

def test_availability_check():
    """Test availability checking"""
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = check_availability("consultation", tomorrow)
    
    assert "date" in result or "available_dates" in result
    print("✅ Availability check test passed")

def test_slot_suggestions():
    """Test intelligent slot suggestions"""
    preferences = {
        "time_preference": "afternoon",
        "date_preference": "asap"
    }
    suggestions = suggest_slots(preferences, "consultation", days_ahead=7)
    
    assert isinstance(suggestions, list)
    print("✅ Slot suggestions test passed")

def test_booking():
    """Test appointment booking"""
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    result = book_appointment(
        appointment_type="consultation",
        date=tomorrow,
        start_time="10:00",
        patient_name="Test Patient",
        patient_email="test@example.com",
        patient_phone="+1-555-0100",
        reason="Test appointment"
    )
    
    assert result["success"] == True
    assert "booking_id" in result
    print("✅ Booking test passed")

def test_calendly_api_availability():
    """Test Calendly API availability endpoint"""
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    availability = calendly_api.get_available_slots(tomorrow, "consultation")
    
    assert availability.date == tomorrow
    assert isinstance(availability.available_slots, list)
    print("✅ Calendly API availability test passed")

if __name__ == "__main__":
    print("Running tests...")
    test_availability_check()
    test_slot_suggestions()
    test_booking()
    test_calendly_api_availability()
    print("\n✅ All tests passed!")


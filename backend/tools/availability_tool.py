"""
Tool for checking appointment availability
"""
from typing import List, Dict
from datetime import datetime, date, timedelta
from ..api.calendly_integration import calendly_api
from ..models.schemas import AppointmentType

def check_availability(
    appointment_type: AppointmentType = "consultation",
    target_date: str = None,
    days_ahead: int = 7
) -> Dict:
    """
    Check availability for appointments
    
    Args:
        appointment_type: Type of appointment
        target_date: Specific date (YYYY-MM-DD) or None for next available
        days_ahead: Number of days to check ahead
    
    Returns:
        Dictionary with availability information
    """
    if target_date:
        # Check specific date
        availability = calendly_api.get_available_slots(target_date, appointment_type)
        return {
            "date": target_date,
            "available_slots": [
                {
                    "time": slot.start_time,
                    "duration_minutes": get_appointment_duration(appointment_type)
                }
                for slot in availability.available_slots
            ]
        }
    else:
        # Check next N days
        today = date.today()
        results = {}
        
        for i in range(days_ahead):
            check_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            availability = calendly_api.get_available_slots(check_date, appointment_type)
            
            if availability.available_slots:
                results[check_date] = [
                    slot.start_time for slot in availability.available_slots
                ]
        
        return {
            "available_dates": results,
            "appointment_type": appointment_type,
            "duration_minutes": get_appointment_duration(appointment_type)
        }

def get_appointment_duration(appointment_type: AppointmentType) -> int:
    """Get duration in minutes for appointment type"""
    durations = {
        "consultation": 30,
        "followup": 15,
        "physical": 45,
        "specialist": 60
    }
    return durations.get(appointment_type, 30)

def suggest_slots(
    preferences: Dict,
    appointment_type: AppointmentType = "consultation",
    days_ahead: int = 7
) -> List[Dict]:
    """
    Intelligently suggest time slots based on preferences
    
    Args:
        preferences: Dict with keys like 'time_preference' (morning/afternoon/evening),
                     'date_preference' (asap/specific_date)
        appointment_type: Type of appointment
        days_ahead: Number of days to check
    
    Returns:
        List of suggested slots with explanations
    """
    today = date.today()
    suggestions = []
    
    time_pref = preferences.get("time_preference", "").lower()
    date_pref = preferences.get("date_preference", "asap")
    
    # Parse date preference
    target_date = None
    if date_pref != "asap":
        # Try to parse specific date
        try:
            target_date = datetime.strptime(date_pref, "%Y-%m-%d").date()
        except:
            pass
    
    # Get availability
    if target_date:
        availability = calendly_api.get_available_slots(
            target_date.strftime("%Y-%m-%d"),
            appointment_type
        )
        
        # Filter by time preference
        filtered_slots = filter_slots_by_preference(
            availability.available_slots,
            time_pref
        )
        
        for slot in filtered_slots[:5]:  # Top 5
            suggestions.append({
                "date": target_date.strftime("%Y-%m-%d"),
                "time": slot.start_time,
                "reason": f"Matches your preference for {time_pref if time_pref else 'any time'}"
            })
    else:
        # Check next few days
        for i in range(min(days_ahead, 14)):
            check_date = (today + timedelta(days=i))
            date_str = check_date.strftime("%Y-%m-%d")
            
            availability = calendly_api.get_available_slots(date_str, appointment_type)
            
            filtered_slots = filter_slots_by_preference(
                availability.available_slots,
                time_pref
            )
            
            for slot in filtered_slots[:2]:  # 2 slots per day
                day_name = check_date.strftime("%A")
                suggestions.append({
                    "date": date_str,
                    "day": day_name,
                    "time": slot.start_time,
                    "reason": f"{day_name} {slot.start_time} - {get_time_description(slot.start_time, time_pref)}"
                })
                
                if len(suggestions) >= 5:
                    break
            
            if len(suggestions) >= 5:
                break
    
    return suggestions

def filter_slots_by_preference(slots, time_pref: str) -> List:
    """Filter slots based on time preference"""
    if not time_pref:
        return slots
    
    morning_cutoff = 12
    afternoon_cutoff = 17
    
    filtered = []
    for slot in slots:
        if not slot.available:
            continue
            
        hour = int(slot.start_time.split(":")[0])
        
        if "morning" in time_pref and hour < morning_cutoff:
            filtered.append(slot)
        elif "afternoon" in time_pref and morning_cutoff <= hour < afternoon_cutoff:
            filtered.append(slot)
        elif "evening" in time_pref and hour >= afternoon_cutoff:
            filtered.append(slot)
    
    return filtered if filtered else slots

def get_time_description(time_str: str, preference: str) -> str:
    """Get human-readable time description"""
    hour = int(time_str.split(":")[0])
    
    if hour < 12:
        period = "AM"
        display_hour = hour if hour != 0 else 12
    else:
        period = "PM"
        display_hour = hour - 12 if hour != 12 else 12
    
    return f"{display_hour}:{time_str.split(':')[1]} {period}"


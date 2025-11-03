"""
Mock Calendly API Integration
Handles availability checking and appointment booking
"""
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, HTTPException, Query
from ..models.schemas import TimeSlot, AvailabilityResponse, BookingRequest, BookingResponse, AppointmentType
import json
import os

APPOINTMENT_DURATIONS = {
    "consultation": 30,
    "followup": 15,
    "physical": 45,
    "specialist": 60
}

BUSINESS_HOURS = {
    "start": 9,  # 9 AM
    "end": 17    # 5 PM
}

class MockCalendlyAPI:
    def __init__(self):
        self.bookings: Dict[str, Dict] = {}
        self.booking_counter = 1
        
    def get_available_slots(
        self, 
        target_date: str, 
        appointment_type: AppointmentType = "consultation"
    ) -> AvailabilityResponse:
        """
        Get available time slots for a given date and appointment type
        """
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
        today = date.today()
        
        if target < today:
            return AvailabilityResponse(date=target_date, available_slots=[])
        
        duration = APPOINTMENT_DURATIONS[appointment_type]
        slots = []
        
        current_hour = BUSINESS_HOURS["start"]
        while current_hour < BUSINESS_HOURS["end"]:
            end_hour = current_hour + (duration / 60)
            if end_hour > BUSINESS_HOURS["end"]:
                break
            
            start_time_str = f"{int(current_hour):02d}:00"
            end_minutes = int((end_hour - int(end_hour)) * 60)
            end_hour_int = int(end_hour)
            end_time_str = f"{end_hour_int:02d}:{end_minutes:02d}"
            
            slot_key = f"{target_date}_{start_time_str}"
            is_available = slot_key not in self.bookings
            
            slots.append(TimeSlot(
                start_time=start_time_str,
                end_time=end_time_str,
                available=is_available
            ))
            
            current_hour += 0.5
        
        available_slots = [slot for slot in slots if slot.available]
        
        return AvailabilityResponse(
            date=target_date,
            available_slots=available_slots
        )
    
    def get_multiple_days_availability(
        self,
        start_date: str,
        num_days: int = 7,
        appointment_type: AppointmentType = "consultation"
    ) -> Dict[str, AvailabilityResponse]:
        """
        Get availability for multiple days
        """
        results = {}
        current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        for i in range(num_days):
            date_str = (current_date + timedelta(days=i)).strftime("%Y-%m-%d")
            results[date_str] = self.get_available_slots(date_str, appointment_type)
        
        return results
    
    def book_appointment(self, booking_request: BookingRequest) -> BookingResponse:
        """
        Book an appointment
        """
        slot_key = f"{booking_request.date}_{booking_request.start_time}"
        
        # Check if slot is still available
        if slot_key in self.bookings:
            raise ValueError(f"Slot {booking_request.date} {booking_request.start_time} is already booked")
        
        # Create booking
        booking_id = f"APPT-{datetime.now().year}-{self.booking_counter:03d}"
        self.booking_counter += 1
        confirmation_code = f"ABC{self.booking_counter % 1000:03d}"
        
        booking_details = {
            "booking_id": booking_id,
            "appointment_type": booking_request.appointment_type,
            "date": booking_request.date,
            "start_time": booking_request.start_time,
            "patient": booking_request.patient.dict(),
            "reason": booking_request.reason,
            "duration_minutes": APPOINTMENT_DURATIONS[booking_request.appointment_type],
            "status": "confirmed"
        }
        
        self.bookings[slot_key] = booking_details
        
        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            confirmation_code=confirmation_code,
            details=booking_details
        )
    
    def cancel_appointment(self, booking_id: str) -> bool:
        """
        Cancel an appointment
        """
        for slot_key, booking in list(self.bookings.items()):
            if booking["booking_id"] == booking_id:
                del self.bookings[slot_key]
                return True
        return False

calendly_api = MockCalendlyAPI()

router = APIRouter()

@router.get("/availability")
async def get_availability(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    appointment_type: AppointmentType = Query("consultation", description="Type of appointment")
):
    """Get available time slots for a given date"""
    try:
        return calendly_api.get_available_slots(date, appointment_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/book", response_model=BookingResponse)
async def create_booking(booking_request: BookingRequest):
    """Book an appointment"""
    try:
        return calendly_api.book_appointment(booking_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


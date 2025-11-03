"""
Tool for booking appointments
"""
from ..api.calendly_integration import calendly_api
from ..models.schemas import BookingRequest, BookingResponse, PatientInfo, AppointmentType
from typing import Dict

def book_appointment(
    appointment_type: AppointmentType,
    date: str,
    start_time: str,
    patient_name: str,
    patient_email: str,
    patient_phone: str,
    reason: str = None
) -> Dict:
    """
    Book an appointment
    
    Returns:
        Dictionary with booking confirmation or error
    """
    try:
        patient = PatientInfo(
            name=patient_name,
            email=patient_email,
            phone=patient_phone
        )
        
        booking_request = BookingRequest(
            appointment_type=appointment_type,
            date=date,
            start_time=start_time,
            patient=patient,
            reason=reason
        )
        
        booking_response = calendly_api.book_appointment(booking_request)
        
        return {
            "success": True,
            "booking_id": booking_response.booking_id,
            "confirmation_code": booking_response.confirmation_code,
            "status": booking_response.status,
            "details": booking_response.details
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Booking failed: {str(e)}"
        }


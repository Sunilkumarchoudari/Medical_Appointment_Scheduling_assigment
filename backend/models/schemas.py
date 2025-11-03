from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import datetime, date, time

AppointmentType = Literal["consultation", "followup", "physical", "specialist"]

class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    available: bool

class AvailabilityResponse(BaseModel):
    date: str
    available_slots: List[TimeSlot]

class PatientInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str

class BookingRequest(BaseModel):
    appointment_type: AppointmentType
    date: str
    start_time: str
    patient: PatientInfo
    reason: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    confirmation_code: str
    details: dict

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    intent: Optional[str] = None
    requires_info: Optional[dict] = None


"""
Chat API endpoints
"""
import os
import sys
from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatMessage, ChatResponse
from ..agent.scheduling_agent import SchedulingAgent
import uuid

router = APIRouter()
_agent_instance = None

def get_agent():
    """Get or create agent instance (lazy initialization)"""
    global _agent_instance
    if _agent_instance is None:
        try:
            _agent_instance = SchedulingAgent()
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize scheduling agent: {str(e)}. Please check your OPENAI_API_KEY environment variable."
            )
    return _agent_instance

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Main chat endpoint for patient interaction
    """
    try:
        agent = get_agent() 
        conversation_id = message.conversation_id or str(uuid.uuid4())
        
        result = agent.process_message(
            message.message,
            conversation_id=conversation_id
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            intent=result.get("intent"),
            requires_info=result.get("requires_info")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book")
async def book_appointment_endpoint(booking_data: dict):
    """
    Book an appointment (called when all information is collected)
    """
    try:
        agent = get_agent() 
        result = agent.handle_booking(
            appointment_type=booking_data.get("appointment_type"),
            date=booking_data.get("date"),
            start_time=booking_data.get("start_time"),
            patient_name=booking_data.get("patient_name"),
            patient_email=booking_data.get("patient_email"),
            patient_phone=booking_data.get("patient_phone"),
            reason=booking_data.get("reason"),
            conversation_id=booking_data.get("conversation_id", "default")
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


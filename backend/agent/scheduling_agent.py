"""
Intelligent scheduling agent with natural conversation flow
"""
import os
import json
from typing import Dict, Optional, List
from openai import OpenAI
from ..tools.availability_tool import check_availability, suggest_slots
from ..tools.booking_tool import book_appointment
from ..rag.faq_rag import FAQRAG
from .prompts import get_system_prompt, get_scheduling_prompt

class SchedulingAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not set. Please set it in your .env file or environment variables."
            )
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
        try:
            self.faq_rag = FAQRAG()
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize FAQ RAG: {e}")
            self.faq_rag = None
        self.conversations: Dict[str, List[Dict]] = {}
    
    def _get_conversation_history(self, conversation_id: str) -> str:
        """Get formatted conversation history"""
        if conversation_id not in self.conversations:
            return ""
        
        history = []
        for msg in self.conversations[conversation_id]:
            role = msg["role"]
            content = msg["content"]
            history.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(history)
    
    def _add_message(self, conversation_id: str, role: str, content: str):
        """Add message to conversation history"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append({"role": role, "content": content})
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent (scheduling, FAQ, or both)"""
        message_lower = message.lower()
        
        scheduling_keywords = [
            "book", "schedule", "appointment", "see doctor", "visit",
            "available", "time slot", "when can", "make appointment"
        ]
        
        faq_keywords = [
            "what", "where", "how", "when", "why", "insurance",
            "accept", "policy", "hours", "location", "parking",
            "bring", "required", "cost", "price"
        ]
        
        is_scheduling = any(keyword in message_lower for keyword in scheduling_keywords)
        is_faq = any(keyword in message_lower for keyword in faq_keywords)
        
        if is_scheduling and is_faq:
            return "both"
        elif is_scheduling:
            return "scheduling"
        elif is_faq:
            return "faq"
        else:
            return "general"
    
    def _extract_preferences(self, message: str, conversation_history: str) -> Dict:
        """Extract preferences from user message"""
        preferences = {}
        
        message_lower = message.lower()
        
        # Time preference
        if any(word in message_lower for word in ["morning", "am", "early"]):
            preferences["time_preference"] = "morning"
        elif any(word in message_lower for word in ["afternoon", "pm", "midday"]):
            preferences["time_preference"] = "afternoon"
        elif any(word in message_lower for word in ["evening", "late"]):
            preferences["time_preference"] = "evening"
        
        # Date preference
        if any(word in message_lower for word in ["asap", "soon", "urgent", "today", "now"]):
            preferences["date_preference"] = "asap"
        elif any(word in message_lower for word in ["tomorrow", "next week", "this week"]):
            # Will be parsed by availability tool
            preferences["date_preference"] = message_lower
        
        return preferences
    
    def _get_available_tools_info(self) -> str:
        """Get information about available tools for the LLM"""
        return """Available Functions:

1. check_availability(appointment_type, target_date, days_ahead)
   - Check available time slots
   - appointment_type: "consultation", "followup", "physical", or "specialist"
   - target_date: "YYYY-MM-DD" format or None
   - Returns: Dictionary with available slots

2. suggest_slots(preferences, appointment_type, days_ahead)
   - Intelligently suggest slots based on preferences
   - preferences: Dict with "time_preference" (morning/afternoon/evening) and "date_preference"
   - Returns: List of suggested slots

3. book_appointment(appointment_type, date, start_time, patient_name, patient_email, patient_phone, reason)
   - Book an appointment
   - Returns: Booking confirmation or error

Use these tools when needed to help the patient."""
    
    def process_message(self, message: str, conversation_id: str = "default") -> Dict:
        """
        Process user message and generate response
        
        Returns:
            Dict with response, intent, and any required info
        """
        self._add_message(conversation_id, "user", message)
        
        intent = self._detect_intent(message)
        
        history = self._get_conversation_history(conversation_id)
        
        faq_context = ""
        if intent in ["faq", "both"] and self.faq_rag:
            try:
                faq_answer = self.faq_rag.answer_question(message)
                faq_context = f"FAQ Answer: {faq_answer}\n(You can incorporate this into your response if relevant)"
            except:
                pass
        
        system_prompt = get_system_prompt()
        available_tools = self._get_available_tools_info()
        user_prompt = get_scheduling_prompt(history, available_tools, faq_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            agent_response = response.choices[0].message.content.strip()
            
            self._add_message(conversation_id, "assistant", agent_response)
            
           
            tool_results = []
            
            if "check availability" in agent_response.lower() or "available" in agent_response.lower():
                preferences = self._extract_preferences(message, history)
                
                if preferences:
                    suggestions = suggest_slots(preferences, "consultation", days_ahead=7)
                    if suggestions:
                        tool_results.append(f"Available slots found: {json.dumps(suggestions, indent=2)}")
            
            if tool_results:
                enhanced_prompt = user_prompt + "\n\nTool Results:\n" + "\n".join(tool_results)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=500
                )
                
                agent_response = response.choices[0].message.content.strip()
                self.conversations[conversation_id][-1]["content"] = agent_response
            
            requires_info = {}
            if any(word in agent_response.lower() for word in ["name", "what's your name"]):
                requires_info["name"] = True
            if any(word in agent_response.lower() for word in ["email", "email address"]):
                requires_info["email"] = True
            if any(word in agent_response.lower() for word in ["phone", "phone number"]):
                requires_info["phone"] = True
            
            return {
                "response": agent_response,
                "conversation_id": conversation_id,
                "intent": intent,
                "requires_info": requires_info if requires_info else None
            }
            
        except Exception as e:
            error_response = f"I apologize, but I'm experiencing some technical difficulties. Please try again or call our office at +1-555-123-4567."
            
            self._add_message(conversation_id, "assistant", error_response)
            
            return {
                "response": error_response,
                "conversation_id": conversation_id,
                "intent": "error",
                "requires_info": None
            }
    
    def handle_booking(
        self,
        appointment_type: str,
        date: str,
        start_time: str,
        patient_name: str,
        patient_email: str,
        patient_phone: str,
        reason: str = None,
        conversation_id: str = "default"
    ) -> Dict:
        """Handle the actual booking"""
        result = book_appointment(
            appointment_type,
            date,
            start_time,
            patient_name,
            patient_email,
            patient_phone,
            reason
        )
        
        if result["success"]:
            confirmation = f"""Your appointment is confirmed!

Booking Details:
- Booking ID: {result['booking_id']}
- Confirmation Code: {result['confirmation_code']}
- Date: {date}
- Time: {start_time}
- Appointment Type: {appointment_type}
- Patient: {patient_name}
- Email: {patient_email}

You will receive a confirmation email. Is there anything else I can help you with?"""
            
            self._add_message(conversation_id, "assistant", confirmation)
            
            return {
                "success": True,
                "response": confirmation,
                "booking_details": result
            }
        else:
            error_msg = f"I apologize, but there was an issue booking your appointment: {result.get('error')}. Please try again or call our office."
            self._add_message(conversation_id, "assistant", error_msg)
            
            return {
                "success": False,
                "response": error_msg,
                "error": result.get("error")
            }


"""
Example usage of the Medical Appointment Scheduling Agent
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def example_chat_conversation():
    """Example of a chat conversation"""
    print("=" * 60)
    print("Example Chat Conversation")
    print("=" * 60)
    
    # Start conversation
    conversation_id = None
    
    messages = [
        "I need to see the doctor",
        "I've been having headaches",
        "General consultation is fine",
        "Afternoon if possible, sometime this week",
        "Wednesday at 3:30",
        "John Doe",
        "john.doe@example.com",
        "+1-555-123-4567",
        "Persistent headaches for the past week"
    ]
    
    for message in messages:
        print(f"\nUser: {message}")
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": message,
                "conversation_id": conversation_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            conversation_id = data["conversation_id"]
            print(f"Agent: {data['response']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    
    print("\n" + "=" * 60)

def example_faq_during_booking():
    """Example of FAQ during booking"""
    print("\n" + "=" * 60)
    print("Example: FAQ During Booking")
    print("=" * 60)
    
    conversation_id = None
    
    messages = [
        "I want to book an appointment",
        "Actually, first - what insurance do you accept?",
        "Yes, I have Blue Cross. Okay, I'd like to schedule a checkup"
    ]
    
    for message in messages:
        print(f"\nUser: {message}")
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": message,
                "conversation_id": conversation_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            conversation_id = data["conversation_id"]
            print(f"Agent: {data['response']}")
        else:
            print(f"Error: {response.status_code}")
            break
    
    print("\n" + "=" * 60)

def example_check_availability():
    """Example of checking availability directly"""
    print("\n" + "=" * 60)
    print("Example: Check Availability")
    print("=" * 60)
    
    from datetime import date, timedelta
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = requests.get(
        f"{BASE_URL}/api/calendly/availability",
        params={
            "date": tomorrow,
            "appointment_type": "consultation"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAvailable slots for {data['date']}:")
        for slot in data['available_slots'][:5]:  # Show first 5
            print(f"  - {slot['start_time']} to {slot['end_time']}")
    else:
        print(f"Error: {response.status_code}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\n⚠️  Make sure the server is running: python run.py\n")
    print("Press Enter to continue or Ctrl+C to exit...")
    input()
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not running. Please start it first with: python run.py")
            exit(1)
        
        example_check_availability()
        example_chat_conversation()
        example_faq_during_booking()
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        print("Start the server with: python run.py")
    except KeyboardInterrupt:
        print("\n\nExiting...")


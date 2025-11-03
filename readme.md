# Quick Start Guide

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your_actual_api_key_here
```

Edit `.env`:
```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=your_openai_api_key_here

# Vector Database
VECTOR_DB=chromadb
VECTOR_DB_PATH=./data/vectordb

# Clinic Configuration
CLINIC_NAME=HealthCare Plus Clinic
CLINIC_PHONE=+1-555-123-4567
TIMEZONE=America/New_York

# Application
BACKEND_PORT=8000
```

### 3. Run the Server

```bash
python run.py
```

The server will start on `http://localhost:8000`

### 4. Test the API

Open a new terminal and run:

```bash
# Health check
curl http://localhost:8000/health

# Start a conversation
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need to see the doctor"}'
```

### 5. Try Example Conversations

Run the example script:

```bash
python example_usage.py
```

## What's Implemented

**5 Core Features Completed:**

1. **Calendly Integration (Mock)**
   - Fetch available time slots
   - Book appointments
   - Handle different appointment types

2. **Natural Conversation Flow**
   - Intelligent scheduling agent
   - Understands patient needs
   - Collects preferences

3. **Smart Slot Recommendations**
   - Suggests slots based on preferences
   - Time and date filtering
   - Multiple options presented

4. **RAG-Powered FAQ System**
   - Answers clinic-related questions
   - Context-aware responses
   - Seamless integration

5. **Appointment Booking**
   - Full booking workflow
   - Confirmation system
   - Patient information collection

## Example Conversations

### Booking an Appointment

```
User: I need to see the doctor
Agent: I'd be happy to help you schedule an appointment! What's the main reason for your visit today?

User: I've been having headaches
Agent: I understand. For persistent headaches, I'd recommend a general consultation...

[Continue conversation to complete booking]
```

### FAQ During Booking

```
User: I want to book an appointment
Agent: I'd be happy to help! What brings you in today?

User: What insurance do you accept?
Agent: We accept most major insurance providers including Blue Cross Blue Shield...

User: Okay, I'd like to schedule a checkup
Agent: Perfect! [Continues with scheduling...]
```

## Project Structure

```
LYZR/
├── backend/           # FastAPI backend
├── data/              # Clinic info and schedules
├── tests/             # Test cases
├── run.py            # Main entry point
└── requirements.txt  # Dependencies
```

## Troubleshooting

### Server won't start
- Check if port 8000 is available
- Verify Python 3.10+ is installed
- Ensure all dependencies are installed

### RAG system not loading
- Check if `data/clinic_info.json` exists
- Verify OpenAI API key is set
- Check console for error messages

### Import errors
- Make sure you're running from project root
- Use `python run.py` instead of running main.py directly

## Next Steps

- Review `README.md` for detailed documentation
- Check `tests/test_agent.py` for test examples
- Explore `example_usage.py` for API usage patterns


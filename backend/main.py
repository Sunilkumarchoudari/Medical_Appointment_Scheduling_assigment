"""
Main FastAPI application for Medical Appointment Scheduling Agent
"""
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api import chat
from backend.api.calendly_integration import router as calendly_router
from backend.rag.faq_rag import FAQRAG

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Medical Appointment Scheduling Agent",
    description="Intelligent conversational agent for scheduling medical appointments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(calendly_router, prefix="/api/calendly", tags=["calendly"])

# Initialize RAG system on startup
@app.on_event("startup")
async def startup_event():
    """Initialize RAG system and load clinic information"""
    try:
        faq_rag = FAQRAG()
        # Get absolute path to clinic_info.json
        base_dir = os.path.dirname(os.path.dirname(__file__))
        clinic_info_path = os.path.join(base_dir, "data", "clinic_info.json")
        if os.path.exists(clinic_info_path):
            faq_rag.vector_store.load_clinic_info(clinic_info_path)
            print("✅ RAG system initialized and clinic information loaded")
        else:
            print(f"⚠️ Warning: Clinic info file not found at {clinic_info_path}")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize RAG system: {e}")
        import traceback
        traceback.print_exc()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical Appointment Scheduling Agent API",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "calendly_availability": "/api/calendly/availability",
            "calendly_book": "/api/calendly/book"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)


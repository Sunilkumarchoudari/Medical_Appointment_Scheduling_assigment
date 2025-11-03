"""
RAG system for answering FAQs
"""
import os
from openai import OpenAI
from typing import Optional
from .vector_store import FAQVectorStore

class FAQRAG:
    def __init__(self):
        self.vector_store = FAQVectorStore()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set for FAQ RAG system")
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    
    def answer_question(self, question: str, conversation_context: Optional[str] = None) -> str:
        """
        Answer FAQ using RAG
        """
        context = self.vector_store.get_context_for_rag(question, top_k=3)
        
        # Build prompt
        system_prompt = """You are a helpful medical appointment scheduling assistant. 
Answer questions about the clinic based on the provided context. 
Be friendly, concise, and accurate. Only use information from the provided context.
If the question cannot be answered from the context, politely say you don't have that information."""
        
        user_prompt = f"""Context about the clinic:
{context}

Question: {question}

Provide a helpful, accurate answer based on the context above."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"I apologize, but I'm having trouble accessing that information right now. Please call our office at +1-555-123-4567 for assistance."


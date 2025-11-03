"""
Vector store for FAQ retrieval using ChromaDB
"""
import os
import json
from typing import List, Dict, Optional
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

class FAQVectorStore:
    def __init__(self, persist_directory: str = "./data/vectordb"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.use_chromadb = CHROMADB_AVAILABLE
        
        if self.use_chromadb:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.collection = self.client.get_or_create_collection(
                name="clinic_faqs",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.documents: List[Dict] = []
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
    
    def load_clinic_info(self, clinic_info_path: str):
        """
        Load clinic info from JSON and chunk it for vector storage
        """
        with open(clinic_info_path, 'r') as f:
            clinic_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for section, content in clinic_data.items():
            if isinstance(content, dict):
                # Convert dict to text
                section_text = self._dict_to_text(section, content)
                
                # Split into chunks
                chunks = self.text_splitter.split_text(section_text)
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{section}_{i}"
                    documents.append(chunk)
                    metadatas.append({"section": section, "chunk_index": i})
                    ids.append(doc_id)
        
        if documents:
            if self.use_chromadb:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            else:
                for i, doc in enumerate(documents):
                    self.documents.append({
                        "content": doc,
                        "metadata": metadatas[i] if i < len(metadatas) else {},
                        "id": ids[i] if i < len(ids) else str(i)
                    })
    
    def _dict_to_text(self, section_name: str, data: Dict) -> str:
        """
        Convert dictionary to readable text format
        """
        text_parts = [f"Section: {section_name.replace('_', ' ').title()}"]
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    text_parts.append(f"{key.replace('_', ' ').title()}: {', '.join(map(str, value))}")
                elif isinstance(value, dict):
                    text_parts.append(f"{key.replace('_', ' ').title()}: {self._dict_to_text(key, value)}")
                else:
                    text_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        elif isinstance(data, list):
            text_parts.append(", ".join(map(str, data)))
        else:
            text_parts.append(str(data))
        
        return "\n".join(text_parts)
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant FAQ information
        """
        if self.use_chromadb:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            retrieved_docs = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    retrieved_docs.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
            
            return retrieved_docs
        else:
            # Simple keyword-based search fallback
            query_lower = query.lower()
            query_words = set(query_lower.split())
            
            scored_docs = []
            for doc in self.documents:
                content_lower = doc["content"].lower()
                # Simple scoring: count matching words
                score = sum(1 for word in query_words if word in content_lower)
                if score > 0:
                    scored_docs.append((score, doc))
            
            # Sort by score and return top_k
            scored_docs.sort(reverse=True, key=lambda x: x[0])
            return [doc for score, doc in scored_docs[:top_k]]
    
    def get_context_for_rag(self, query: str, top_k: int = 3) -> str:
        """
        Get formatted context string for RAG
        """
        docs = self.search(query, top_k)
        if not docs:
            return ""
        
        context_parts = ["Relevant Clinic Information:"]
        for doc in docs:
            context_parts.append(f"- {doc['content']}")
        
        return "\n".join(context_parts)


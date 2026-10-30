from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.rag_engine import rag_engine

def search_troubleshooting_knowledge(db: Session, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Performs semantic search across internal SOPs, runbooks, and postmortems."""
    citations = rag_engine.search(db, query, limit=limit)
    return [c.model_dump() for c in citations]

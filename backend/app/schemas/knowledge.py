from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class KnowledgeDocCreate(BaseModel):
    title: str
    category: Optional[str] = "RUNBOOK"
    content: str
    filename: Optional[str] = "manual_entry.md"

class KnowledgeDocResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    title: str
    category: str
    content: str
    created_at: datetime

class RAGQueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 3

class RAGSourceCitation(BaseModel):
    document_title: str
    filename: str
    section: Optional[str] = None
    similarity_score: float
    excerpt: str

class RAGQueryResult(BaseModel):
    query: str
    citations: List[RAGSourceCitation]

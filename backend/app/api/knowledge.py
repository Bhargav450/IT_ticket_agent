from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import tempfile
from app.core.database import get_db
from app.models.knowledge import KnowledgeDocument
from app.schemas.knowledge import KnowledgeDocResponse, RAGQueryRequest, RAGQueryResult
from app.services.rag_engine import rag_engine

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.get("", response_model=List[KnowledgeDocResponse])
def list_knowledge_documents(db: Session = Depends(get_db)):
    return db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()

@router.post("/upload", response_model=KnowledgeDocResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form("RUNBOOK"),
    db: Session = Depends(get_db)
):
    doc_title = title or file.filename.replace("_", " ").split(".")[0].title()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        content = rag_engine.extract_text(tmp_path, file.filename)
        if not content.strip():
            raise HTTPException(status_code=400, detail="Document appears empty or unreadable.")
        
        doc = rag_engine.ingest_document(
            db=db,
            filename=file.filename,
            title=doc_title,
            category=category,
            content=content
        )
        return doc
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/search", response_model=RAGQueryResult)
def search_knowledge(req: RAGQueryRequest, db: Session = Depends(get_db)):
    citations = rag_engine.search(db, req.query, limit=req.limit or 3)
    return RAGQueryResult(
        query=req.query,
        citations=citations
    )

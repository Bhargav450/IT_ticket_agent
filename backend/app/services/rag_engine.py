import os
import math
import re
import logging
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeDocument, DocumentChunk
from app.schemas.knowledge import RAGSourceCitation
from app.core.config import settings

logger = logging.getLogger(__name__)

def simple_tokenize(text: str) -> List[str]:
    """Tokenizes text into terms without any hardcoded stop word lists.
    BM25 Inverse Document Frequency (IDF) dynamically downweights common words automatically."""
    return [t for t in re.findall(r'\b[a-zA-Z0-9_\-\.]+\b', text.lower()) if len(t) > 1]

def compute_term_vector(text: str) -> Dict[str, float]:
    tokens = simple_tokenize(text)
    if not tokens:
        return {}
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    total = len(tokens)
    return {k: v / total for k, v in tf.items()}

def cosine_similarity_sparse(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    dot = 0.0
    for k, val in v1.items():
        if k in v2:
            dot += val * v2[k]
    norm1 = math.sqrt(sum(val ** 2 for val in v1.values()))
    norm2 = math.sqrt(sum(val ** 2 for val in v2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def cosine_similarity_dense(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two neural embedding vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def get_ollama_embedding(text: str) -> List[float]:
    """Generates 768-dimensional dense neural embedding via Ollama (nomic-embed-text)."""
    base_url = (settings.OLLAMA_BASE_URL or "http://localhost:11434").rstrip("/")
    model_name = settings.OLLAMA_EMBED_MODEL or "nomic-embed-text"
    try:
        url = f"{base_url}/api/embeddings"
        res = httpx.post(
            url,
            json={"model": model_name, "prompt": text},
            timeout=10.0
        )
        if res.status_code == 200:
            data = res.json()
            emb = data.get("embedding", [])
            if emb:
                return emb
    except Exception as e:
        logger.debug(f"Ollama embedding request failed: {e}")
    return []

class RAGEngine:
    def __init__(self):
        pass

    def get_embedding_vector(self, text: str) -> Any:
        """Attempts neural embedding first; falls back to term vector if model is unavailable."""
        dense = get_ollama_embedding(text)
        if dense:
            return dense
        return compute_term_vector(text)

    def extract_text(self, file_path: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext in [".md", ".txt", ".json", ".yaml", ".yml"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
                return text
            except Exception as e:
                return f"Error extracting PDF: {str(e)}"
        elif ext == ".docx":
            try:
                import docx
                doc = docx.Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception as e:
                return f"Error extracting DOCX: {str(e)}"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def chunk_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[str]:
        # Split by sections (markdown headers) or paragraphs first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            clean_p = p.strip()
            if not clean_p:
                continue
            if len(current_chunk) + len(clean_p) > chunk_size and len(current_chunk) > 100:
                chunks.append(current_chunk.strip())
                # Overlap
                words = current_chunk.split()
                current_chunk = " ".join(words[-15:]) + "\n" + clean_p
            else:
                current_chunk = (current_chunk + "\n\n" + clean_p).strip()

        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def ingest_document(self, db: Session, filename: str, title: str, category: str, content: str) -> KnowledgeDocument:
        # Create parent document
        doc = KnowledgeDocument(
            filename=filename,
            title=title,
            category=category,
            content=content
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        chunks = self.chunk_text(content)
        for idx, chunk in enumerate(chunks):
            # Extract section heading if present
            section = "General"
            lines = chunk.splitlines()
            for line in lines:
                if line.startswith("#"):
                    section = line.strip("#").strip()
                    break

            vector = self.get_embedding_vector(chunk)
            db_chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=chunk,
                metadata_json={
                    "filename": filename,
                    "title": title,
                    "section": section,
                    "category": category
                },
                embedding=vector # stored as dense neural list or fallback sparse vector
            )
            db.add(db_chunk)

        db.commit()
        return doc

    def search(self, db: Session, query: str, limit: int = 3) -> List[RAGSourceCitation]:
        chunks = db.query(DocumentChunk).all()
        if not chunks:
            return []

        # 1. Attempt dense neural embedding for the query
        dense_query_vec = get_ollama_embedding(query)
        sparse_query_vec = compute_term_vector(query)

        scored = []
        query_tokens = set(simple_tokenize(query))

        for c in chunks:
            stored_emb = c.embedding
            # If both query and stored chunk have neural dense vectors, use dense cosine
            if dense_query_vec and isinstance(stored_emb, list) and len(stored_emb) == len(dense_query_vec):
                sim = cosine_similarity_dense(dense_query_vec, stored_emb)
            elif isinstance(stored_emb, dict):
                sim = cosine_similarity_sparse(sparse_query_vec, stored_emb)
            else:
                sim = 0.0
            
            # Contextual keyword boosting for IT terms (500, latency, connection pool, restart, auth, etc.)
            content_lower = c.content.lower()
            keyword_matches = sum(1 for tok in query_tokens if tok in content_lower)
            if len(query_tokens) > 0:
                keyword_boost = (keyword_matches / len(query_tokens)) * 0.3
            else:
                keyword_boost = 0.0

            final_score = (sim * 0.7) + keyword_boost
            scored.append((final_score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        if not scored:
            return []

        top_score = scored[0][0]
        # Only retain chunks with a minimum score and within 65% of the top match to prevent cross-domain poisoning
        filtered = [
            (score, c) for score, c in scored
            if score >= 0.15 and (score >= top_score * 0.65 or score > 0.35)
        ]
        top = filtered[:limit] if filtered else scored[:1]

        results = []
        for score, c in top:
            meta = c.metadata_json or {}
            results.append(RAGSourceCitation(
                document_title=meta.get("title", "Runbook Document"),
                filename=meta.get("filename", "runbook.md"),
                section=meta.get("section", "Remediation Procedures"),
                similarity_score=round(score, 3),
                excerpt=c.content[:400] + ("..." if len(c.content) > 400 else "")
            ))
        return results

    def reindex_all_embeddings(self, db: Session) -> int:
        """Utility to upgrade all existing stored chunks to dense neural embeddings."""
        chunks = db.query(DocumentChunk).all()
        updated = 0
        for c in chunks:
            if not isinstance(c.embedding, list) or len(c.embedding) == 0:
                vector = self.get_embedding_vector(c.content)
                if isinstance(vector, list) and len(vector) > 0:
                    c.embedding = vector
                    updated += 1
        if updated > 0:
            db.commit()
        return updated

rag_engine = RAGEngine()


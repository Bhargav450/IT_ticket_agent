from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.services.rag_engine import compute_term_vector, cosine_similarity_sparse

class IncidentMemoryStore:
    """Manages short-term conversation context and long-term memory of previous resolved incidents."""

    def __init__(self):
        self._short_term_context: Dict[int, List[Dict[str, Any]]] = {}

    # Short-Term Memory Methods
    def record_step(self, incident_id: int, step_type: str, content: Any):
        if incident_id not in self._short_term_context:
            self._short_term_context[incident_id] = []
        self._short_term_context[incident_id].append({
            "step_type": step_type,
            "content": content
        })

    def get_short_term_context(self, incident_id: int) -> List[Dict[str, Any]]:
        return self._short_term_context.get(incident_id, [])

    def clear_short_term_context(self, incident_id: int):
        if incident_id in self._short_term_context:
            del self._short_term_context[incident_id]

    # Long-Term Memory: Historical Incident Search
    def search_similar_resolved_incidents(self, db: Session, query: str, limit: int = 2) -> List[Dict[str, Any]]:
        resolved_incidents = db.query(Incident).filter(
            Incident.status == "RESOLVED",
            Incident.resolution_notes.isnot(None)
        ).all()

        if not resolved_incidents:
            return []

        query_vec = compute_term_vector(query)
        scored = []

        for inc in resolved_incidents:
            doc_text = f"{inc.title} {inc.description} {inc.root_cause_analysis or ''}"
            inc_vec = compute_term_vector(doc_text)
            sim = cosine_similarity_sparse(query_vec, inc_vec)
            if sim > 0.05:
                scored.append((sim, inc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, inc in scored[:limit]:
            results.append({
                "ticket_number": inc.ticket_number,
                "title": inc.title,
                "similarity_score": round(score, 3),
                "root_cause": inc.root_cause_analysis,
                "resolution": inc.resolution_notes,
                "resolved_in_seconds": inc.resolution_time_seconds
            })
        return results

incident_memory = IncidentMemoryStore()


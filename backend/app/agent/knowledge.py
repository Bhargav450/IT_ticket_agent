from typing import Dict, Any
from app.agent.state import ITSupportState
from app.agent.tools.rag_tool import search_troubleshooting_knowledge
from app.agent.memory.incident_memory import incident_memory
from app.agent.tools.ticket_tool import update_incident_record
from app.core.database import SessionLocal
from app.models.audit import AgentStepLog

def knowledge_node(state: ITSupportState) -> Dict[str, Any]:
    """Knowledge Agent: Retrieves internal SOPs and runbooks using RAG, and queries long-term incident memory."""
    title = state.get("title", "")
    service = state.get("affected_service", "api-gateway")
    desc = state.get("description", "")
    
    # Ground RAG search primarily on the employee problem description
    query = f"{title} {desc}".strip()
    if not query:
        query = service
    
    db = SessionLocal()
    try:
        citations = search_troubleshooting_knowledge(db, query, limit=3)
        similar_past = incident_memory.search_similar_resolved_incidents(db, query, limit=2)
        
        thought = f"Retrieved {len(citations)} internal runbook sections and {len(similar_past)} past incident resolutions."
        if citations:
            top_source = citations[0]
            thought += f" Top match: '{top_source.get('document_title')}' (similarity: {top_source.get('similarity_score')})."
        
        step = AgentStepLog(
            incident_id=state["incident_id"],
            node_name="knowledge_rag",
            status="SUCCESS",
            thought_summary=thought,
            tool_name="rag_vector_search",
            tool_input={"query": query, "target_service": service},
            tool_output={
                "citations_count": len(citations),
                "citations": citations,
                "similar_past_incidents": similar_past
            }
        )
        db.add(step)
        
        update_incident_record(
            db=db,
            incident_id=state["incident_id"],
            rag_sources=citations
        )
        db.commit()
    finally:
        db.close()

    return {
        "knowledge_retrieved": True,
        "rag_citations": citations,
        "similar_past_incidents": similar_past,
        "current_node": "knowledge"
    }

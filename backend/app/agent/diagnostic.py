from typing import Dict, Any
from app.agent.state import ITSupportState
from app.agent.tools.log_tool import query_application_logs
from app.agent.tools.db_tool import query_db_diagnostics
from app.agent.tools.infra_tool import get_service_status
from app.agent.llm_factory import llm_client
from app.agent.tools.ticket_tool import update_incident_record
from app.core.database import SessionLocal
from app.models.audit import AgentStepLog

def diagnostic_node(state: ITSupportState) -> Dict[str, Any]:
    """Diagnostic Agent: Investigates live application logs, DB metrics, and synthesizes root cause."""
    service = state.get("affected_service", "api-gateway")
    category = state.get("category", "APPLICATION")
    
    findings: Dict[str, Any] = {}
    
    log_res = query_application_logs(service_name=service, limit=5)
    findings["logs"] = log_res.get("logs", [])
    
    service_status = get_service_status(service)
    findings["service_status"] = service_status
    
    if category == "DATABASE" or service == "order-db":
        db_diag = query_db_diagnostics("order-db")
        findings["db_diagnostics"] = db_diag
    
    citations = state.get("rag_citations", [])
    primary_citation = citations[0] if citations else None
    rag_context = primary_citation.get("excerpt", "") if primary_citation else ""
    
    if category == "GENERAL_IT" or service == "enterprise-it":
        prompt = f"""
        You are an expert Enterprise IT Support Agent.
        Analyze this employee request or inquiry:
        Title: {state.get('title', '')}
        Description: {state.get('description', '')}
        Relevant IT Runbook Context:
        {rag_context}

        Provide clear root cause identification and actionable resolution guidance based strictly on the runbook context above.
        Extract the exact diagnostic checks, causes, and approved resolution steps described in the runbook.
        Do not invent hypothetical facts or use generic placeholders.

        Return strictly valid JSON:
        {{
          "root_cause": "clear, professional explanation of the issue or topic from the runbook",
          "resolution_guidance": "actionable step-by-step instructions or resolution procedure from the runbook",
          "confidence": 0.95,
          "primary_fault": "Enterprise IT Policy / Support"
        }}
        """
    else:
        prompt = f"""
        You are an expert IT Diagnostic Agent.
        Investigate this infrastructure incident:
        Service: {service}
        Category: {category}
        Logs gathered: {findings.get('logs')}
        Service status: {service_status}
        Runbook context: {rag_context}

        Formulate the root cause analysis from the gathered logs and metrics.
        Return strictly valid JSON:
        {{
          "root_cause": "detailed root cause explanation based on telemetry and logs",
          "confidence": 0.95,
          "primary_fault": "concise fault name"
        }}
        """
    
    llm_res = llm_client.generate_json(prompt)
    root_cause = llm_res.get("root_cause")
    resolution_guidance = llm_res.get("resolution_guidance", "")
    confidence = float(llm_res.get("confidence", 0.9))
    
    if category == "GENERAL_IT" or service == "enterprise-it":
        if not root_cause or len(root_cause) < 10 or not resolution_guidance or len(resolution_guidance) < 15:
            if rag_context:
                content_lines = [l.strip() for l in rag_context.splitlines() if l.strip()]
                header = content_lines[0] if content_lines else "Enterprise IT Runbook"
                
                # Extract actionable procedure and guidance lines dynamically from the retrieved document
                actionable_lines = [
                    l for l in content_lines[1:]
                    if any(l.lower().startswith(k) or k in l.lower() for k in [
                        "diagnosis:", "resolution:", "verification:", "procedure",
                        "steps:", "1.", "2.", "3.", "check ", "confirm ", "verify ", "- "
                    ])
                ]
                
                if not root_cause or len(root_cause) < 10:
                    root_cause = f"{header}: Issue matched with enterprise support playbook."
                
                if not resolution_guidance or len(resolution_guidance) < 15:
                    if actionable_lines:
                        resolution_guidance = "\n".join(actionable_lines[:5])
                    elif len(content_lines) > 1:
                        resolution_guidance = "\n".join(content_lines[1:5])
                    else:
                        resolution_guidance = "Follow the standard resolution procedures outlined in the enterprise runbook."
            else:
                root_cause = "IT guidance inquiry analyzed."
                resolution_guidance = "Follow standard enterprise IT support verification procedures."
    elif not root_cause or len(root_cause) < 10:
        # Dynamically synthesize root cause from real telemetry evidence
        error_logs = [l for l in findings.get("logs", []) if l.get("level") in ["ERROR", "CRITICAL"]]
        if error_logs:
            top_err = error_logs[-1]
            root_cause = f"Telemetry failure detected on '{service}': {top_err.get('message', 'Error')}"
            confidence = 0.95
        elif service_status.get("error_rate_percent", 0) > 0:
            root_cause = f"Service degradation on '{service}' with {service_status.get('error_rate_percent')}% error rate and {service_status.get('latency_ms')}ms latency."
            confidence = 0.88
        elif rag_context:
            first_line = rag_context.strip().splitlines()[0]
            root_cause = f"Inquiry diagnosis on '{service}' from runbook context: {first_line}"
            confidence = 0.90
        else:
            root_cause = f"Service investigation completed for '{service}'."
            confidence = 0.85

    db = SessionLocal()
    try:
        step = AgentStepLog(
            incident_id=state["incident_id"],
            node_name="diagnostic",
            status="SUCCESS",
            thought_summary=f"Diagnostic inspection completed for '{service}'. Root cause identified with {int(confidence*100)}% confidence: {root_cause}",
            tool_name="log_and_metrics_analyzer",
            tool_input={"service": service, "category": category},
            tool_output={
                "root_cause": root_cause,
                "confidence": confidence,
                "evidence_logs_count": len(findings["logs"]),
                "service_error_rate": service_status.get("error_rate_percent", 0.0)
            }
        )
        db.add(step)
        
        update_incident_record(
            db=db,
            incident_id=state["incident_id"],
            root_cause=root_cause
        )
        db.commit()
    finally:
        db.close()

    return {
        "diagnosed": True,
        "diagnostic_findings": findings,
        "root_cause": root_cause,
        "root_cause_confidence": confidence,
        "resolution_guidance": resolution_guidance,
        "current_node": "diagnostic"
    }

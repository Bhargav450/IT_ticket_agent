from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from app.agent.state import ITSupportState
from app.agent.supervisor import supervisor_node, supervisor_router
from app.agent.triage import triage_node
from app.agent.knowledge import knowledge_node
from app.agent.diagnostic import diagnostic_node
from app.agent.resolution import resolution_node
from app.agent.verification import verification_node

def build_support_graph():
    builder = StateGraph(ITSupportState)

    # 1. Register specialized agent nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("triage", triage_node)
    builder.add_node("knowledge", knowledge_node)
    builder.add_node("diagnostic", diagnostic_node)
    builder.add_node("resolution", resolution_node)
    builder.add_node("verification", verification_node)

    # 2. Wire entry point
    builder.add_edge(START, "supervisor")

    # 3. Dynamic supervisor conditional routing
    builder.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "triage": "triage",
            "knowledge": "knowledge",
            "diagnostic": "diagnostic",
            "resolution": "resolution",
            "verification": "verification",
            "end": END
        }
    )

    # 4. Each node reports back to supervisor
    builder.add_edge("triage", "supervisor")
    builder.add_edge("knowledge", "supervisor")
    builder.add_edge("diagnostic", "supervisor")
    builder.add_edge("resolution", "supervisor")
    builder.add_edge("verification", "supervisor")

    # Memory Checkpointer for state persistence and human-in-the-loop pause/resume
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

agent_graph = build_support_graph()

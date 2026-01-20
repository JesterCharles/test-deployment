"""
Supervisor Agent - Graph Construction
======================================
Constructs the LangGraph StateGraph for the multi-agent supervisor system.

This is the main entry point for the agent, exporting the compiled `agent`
variable for LangSmith deployment.

LangSmith Studio: Run `langgraph dev` in the deployment directory
Documentation: https://docs.langchain.com/langsmith/application-structure
"""

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from my_lib.utils.state import SupervisorState
from my_lib.utils.nodes import (
    supervisor_node,
    calendar_node,
    email_node,
    research_node,
    respond_node,
    route_from_supervisor,
)

load_dotenv()


# === Build the Graph ===

workflow = StateGraph(SupervisorState)

# Add nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("calendar", calendar_node)
workflow.add_node("email", email_node)
workflow.add_node("research", research_node)
workflow.add_node("respond", respond_node)

# Add edges
workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "calendar": "calendar",
        "email": "email",
        "research": "research",
        "respond": "respond",
        "__end__": END
    }
)

# Sub-agents return to supervisor
workflow.add_edge("calendar", "supervisor")
workflow.add_edge("email", "supervisor")
workflow.add_edge("research", "supervisor")
workflow.add_edge("respond", END)

# Compile WITHOUT checkpointer - LangSmith provides one in production
agent = workflow.compile()


# === Local Testing ===
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    
    print("=" * 60)
    print("Supervisor Multi-Agent System - Local Test")
    print("=" * 60)
    print("\nFor LangSmith Studio testing, run: langgraph dev")
    print("Then open: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024\n")
    
    requests = [
        "Schedule a meeting with the team for next Tuesday at 2pm to discuss Q4 goals",
        "Research the latest trends in AI agents",
        "Draft an email to the marketing team about the product launch",
    ]
    
    for request in requests:
        print(f"\n{'='*60}")
        print(f"Request: {request}")
        print("="*60)
        result = agent.invoke({
            "messages": [HumanMessage(content=request)],
            "next_agent": "",
            "task_result": ""
        })
        print(f"\nResponse:\n{result['messages'][-1].content}")

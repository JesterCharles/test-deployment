"""
Node Functions for Supervisor Agent
=====================================
Contains all node functions used in the multi-agent workflow.
"""

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from my_lib.utils.state import SupervisorState


# === Model Configuration ===
SUPERVISOR_MODEL = "openai:gpt-4o"
SUBAGENT_MODEL = "openai:gpt-4o-mini"


# === Supervisor Node ===

def supervisor_node(state: SupervisorState) -> dict:
    """Supervisor analyzes requests and routes to appropriate specialist."""
    model = init_chat_model(SUPERVISOR_MODEL)
    
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    # Check if we have a task result to synthesize
    if state.get("task_result"):
        response = model.invoke([
            {"role": "system", "content": """You are a personal assistant supervisor.
Synthesize the specialist's response into a helpful final answer for the user."""},
            {"role": "user", "content": f"Original request: {last_message}\n\nSpecialist result: {state['task_result']}"}
        ])
        return {
            "messages": [AIMessage(content=response.content)],
            "next_agent": "__end__",
            "task_result": ""
        }
    
    # Route to appropriate specialist
    routing_response = model.invoke([
        {"role": "system", "content": """You are a supervisor that routes requests to specialists.
        
Available specialists:
- calendar: Schedule meetings, appointments, reminders
- email: Draft or send emails
- research: Research topics, gather information

Respond with ONLY the specialist name (calendar, email, or research).
If the request doesn't fit any specialist, respond with 'respond' to handle directly."""},
        {"role": "user", "content": last_message}
    ])
    
    route = routing_response.content.strip().lower()
    if route not in ["calendar", "email", "research"]:
        route = "respond"
    
    return {"next_agent": route}


# === Sub-Agent Nodes ===

def calendar_node(state: SupervisorState) -> dict:
    """Calendar specialist handles scheduling tasks."""
    model = init_chat_model(SUBAGENT_MODEL)
    
    last_message = state["messages"][-1].content
    
    response = model.invoke([
        {"role": "system", "content": """You are a calendar management specialist.

When asked to schedule, modify, or check calendar events:
1. Parse the request for date, time, and description
2. Confirm the details
3. Provide clear confirmation

CRITICAL: Include ALL scheduling details in your response."""},
        {"role": "user", "content": last_message}
    ])
    
    return {
        "task_result": response.content,
        "next_agent": "supervisor"
    }


def email_node(state: SupervisorState) -> dict:
    """Email specialist handles email composition."""
    model = init_chat_model(SUBAGENT_MODEL)
    
    last_message = state["messages"][-1].content
    
    response = model.invoke([
        {"role": "system", "content": """You are an email composition specialist.

When asked to draft or send emails:
1. Clarify recipient, subject, and key points
2. Draft professional, clear emails
3. Provide the complete draft

CRITICAL: Include the FULL email draft in your response."""},
        {"role": "user", "content": last_message}
    ])
    
    return {
        "task_result": response.content,
        "next_agent": "supervisor"
    }


def research_node(state: SupervisorState) -> dict:
    """Research specialist handles information gathering."""
    model = init_chat_model(SUBAGENT_MODEL)
    
    last_message = state["messages"][-1].content
    
    response = model.invoke([
        {"role": "system", "content": """You are a research specialist.

When asked to research a topic:
1. Break down the research question
2. Provide key findings and insights
3. Cite sources when applicable

CRITICAL: Include ALL findings in your response."""},
        {"role": "user", "content": last_message}
    ])
    
    return {
        "task_result": response.content,
        "next_agent": "supervisor"
    }


def respond_node(state: SupervisorState) -> dict:
    """Direct response when no specialist is needed."""
    model = init_chat_model(SUPERVISOR_MODEL)
    
    last_message = state["messages"][-1].content
    
    response = model.invoke([
        {"role": "system", "content": "You are a helpful personal assistant. Respond directly to the user."},
        {"role": "user", "content": last_message}
    ])
    
    return {
        "messages": [AIMessage(content=response.content)],
        "next_agent": "__end__"
    }


# === Routing Function ===

def route_from_supervisor(state: SupervisorState) -> str:
    """Route based on supervisor's decision."""
    return state["next_agent"]

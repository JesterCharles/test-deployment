"""
State Definition for Supervisor Agent
======================================
Defines the TypedDict state used throughout the multi-agent workflow.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class SupervisorState(TypedDict):
    """State for the supervisor multi-agent workflow.
    
    Attributes:
        messages: Conversation history with add_messages reducer
        next_agent: The next agent to route to
        task_result: Result from specialist sub-agents
    """
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: Literal["calendar", "email", "research", "respond", "__end__"]
    task_result: str

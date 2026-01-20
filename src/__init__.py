"""
Supervisor Agent Package
========================
A multi-agent supervisor system using LangGraph StateGraph.

This package is structured for LangSmith deployment following
the recommended LangGraph application structure.
"""

from supervisor_agent.agent import agent

__all__ = ["agent"]

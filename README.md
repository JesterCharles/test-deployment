# Supervisor Multi-Agent System - Deployment Package

A multi-agent supervisor system using LangGraph StateGraph, structured following the [official LangGraph application structure](https://docs.langchain.com/langsmith/application-structure).

## Architecture

This agent uses a **supervisor pattern** with specialized sub-agents:

```
┌─────────────────────────────────────────────────────────┐
│                       Supervisor                         │
│                    (gpt-4o - Routing)                   │
└───────────────┬──────────────┬──────────────┬───────────┘
                │              │              │
       ┌────────▼───┐  ┌───────▼────┐  ┌──────▼──────┐
       │  Calendar  │  │   Email    │  │  Research   │
       │ (gpt-4o-   │  │ (gpt-4o-   │  │ (gpt-4o-    │
       │   mini)    │  │   mini)    │  │   mini)     │
       └────────────┘  └────────────┘  └─────────────┘
```

## Project Structure

Following the [LangGraph application structure](https://docs.langchain.com/langsmith/application-structure):

```
deployment/
├── supervisor_agent/           # all project code lies within here
│   ├── utils/                  # utilities for your graph
│   │   ├── __init__.py
│   │   ├── nodes.py            # node functions for your graph
│   │   └── state.py            # state definition of your graph
│   ├── __init__.py
│   └── agent.py                # code for constructing your graph
├── .env                        # environment variables (create from .env.example)
├── .env.example                # template for environment variables
├── requirements.txt            # package dependencies
├── langgraph.json              # configuration file for LangGraph
└── README.md                   # this file
```

## Files

| File | Purpose |
|------|---------|
| `supervisor_agent/agent.py` | Main graph construction & exported `agent` |
| `supervisor_agent/utils/state.py` | `SupervisorState` TypedDict definition |
| `supervisor_agent/utils/nodes.py` | All node functions (supervisor, calendar, email, research) |
| `langgraph.json` | LangGraph configuration for deployment |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for environment variables |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY, LANGSMITH_API_KEY
```

### 3. Test Locally

```bash
# Start LangGraph dev server
langgraph dev

# Opens at http://127.0.0.1:2024
```

Then open LangSmith Studio:
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

Select `supervisor_agent` from the dropdown and test it!

### 4. Test via Python

```bash
cd deployment
python -m supervisor_agent.agent
```

## Deploying to LangSmith Cloud

### Option A: Via LangSmith UI (Recommended)

1. Push this folder to a GitHub repository
2. Go to [LangSmith Deployments](https://smith.langchain.com/deployments)
3. Click **New Deployment**
4. Connect your GitHub repository
5. Select the graph path: `./supervisor_agent/agent.py:agent`
6. Configure environment variables:
   - `OPENAI_API_KEY`
   - `LANGSMITH_API_KEY`
7. Click **Deploy**

### Option B: Via CLI

```bash
langgraph deploy --config langgraph.json
```

## Calling the Deployed API

### Using LangGraph SDK (Python)

```python
from langgraph_sdk import get_client

# Connect to your deployment
client = get_client(url="https://your-deployment.langsmith.com")

# Create a thread for conversation
thread = await client.threads.create()

# Invoke the agent
result = await client.runs.create(
    thread_id=thread["thread_id"],
    assistant_id="supervisor_agent",
    input={
        "messages": [{"role": "user", "content": "Schedule a meeting for Tuesday at 2pm"}]
    }
)
```

### Using HTTP Requests

```python
import requests

response = requests.post(
    "https://your-deployment.langsmith.com/runs",
    headers={"Authorization": "Bearer YOUR_LANGSMITH_API_KEY"},
    json={
        "assistant_id": "supervisor_agent",
        "input": {"messages": [{"role": "user", "content": "Research AI trends"}]},
        "config": {"configurable": {"thread_id": "user-123"}}
    }
)
result = response.json()
```

## Example Requests

The supervisor routes requests to the appropriate specialist:

| Request | Routes To |
|---------|----------|
| "Schedule a meeting for Tuesday at 2pm" | Calendar |
| "Draft an email to the marketing team" | Email |
| "Research AI agent architectures" | Research |
| "What's the weather like?" | Direct Response |

## Production Best Practices

1. **Checkpointing**: LangSmith handles this automatically - no local checkpointer needed
2. **API Keys**: Use LangSmith Secrets for production API keys
3. **Monitoring**: All runs are traced in LangSmith automatically
4. **Scaling**: LangSmith auto-scales based on demand
5. **Versioning**: Use git branches for different deployment versions

## Key Concepts

- **State** (`utils/state.py`): Defines the `SupervisorState` TypedDict with messages, routing, and task results
- **Nodes** (`utils/nodes.py`): Contains all node functions - supervisor for routing, specialists for tasks
- **Agent** (`agent.py`): Constructs the StateGraph, adds nodes/edges, and exports the compiled `agent`

## Troubleshooting

**"No module found" errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're running from the `deployment/` directory

**"API key not found" errors:**
- Check your `.env` file has valid API keys
- For deployment, configure secrets in LangSmith UI

**Agent not appearing in Studio:**
- Verify `langgraph.json` points to the correct file: `./supervisor_agent/agent.py:agent`
- Restart the dev server: `langgraph dev`

## References

- [LangGraph Application Structure](https://docs.langchain.com/langsmith/application-structure)
- [LangSmith Deployments](https://docs.langchain.com/langsmith/deployments)
- [LangGraph CLI Reference](https://docs.langchain.com/langsmith/cli)

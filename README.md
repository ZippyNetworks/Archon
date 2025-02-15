# Zippy's Archon (Fork of Cole Medin’s Archon)

This is a customized fork of [Archon by Cole Medin](https://github.com/coleam00/Archon). 
It includes additional branding and features maintained by Zippy. 

I am building a fork with these goals:

# Refactor Archon V2 Into a More Modular “Master Orchestrator” System

---

## Overview

We want to evolve Archon V2 into a more robust, modular, and extensible agent framework—capable of handling multiple sub-agents, a wide variety of tools, and smarter error handling. Below is a **prioritized to-do list** outlining the steps needed to achieve this goal, plus details on how to proceed with the first major refactor.

---

## To-Do List (Prioritized)

1. **Refactor Orchestrator Logic**  
   - **Goal**: Separate high-level orchestration (the “master agent”) from the individual nodes and sub-agents currently defined in `archon_graph.py`.  
   - **Outcome**: A new `orchestrator.py` to handle flow creation, memory state, and sub-agent orchestration.  
   - **Priority**: **High** (foundation for further work).

2. **Create a Plugin Architecture for Tools**  
   - **Goal**: Move tool definitions out of `pydantic_ai_coder.py` into a dedicated `plugins/` (or `tools/`) directory.  
   - **Outcome**: A simple plugin loader or registry that auto-detects tool modules, making them easily reusable and extensible.  
   - **Priority**: **High** (enables quick addition or removal of tools).

3. **Implement Error Handling & Diagnostic Agent**  
   - **Goal**: If a node or sub-agent fails repeatedly, pass context to a “Diagnostic Agent” that attempts self-healing or user guidance.  
   - **Outcome**: Prevention of entire flow failures; improved reliability and debugging.  
   - **Priority**: **High** (critical for production-ready stability).

4. **Add a “Tool Generator” Sub-Agent**  
   - **Goal**: Automatically generate new plugin files for external integrations (e.g., Twilio, Slack) when requested by the user.  
   - **Outcome**: Rapid expansion of capabilities and less manual coding for new services.  
   - **Priority**: **Medium** (depends on plugin architecture).

5. **Enhance Streamlit UI / Integrate with n8n**  
   - **Goal**: Provide a user-friendly interface to orchestrate tasks, show logs, and possibly visually link subflows.  
   - **Outcome**: Broader accessibility for non-developers; potential “drag-and-drop” automation via n8n nodes.  
   - **Priority**: **Medium** (quality-of-life improvement).

6. **Database & Logging Improvements**  
   - **Goal**: Add tables (e.g., `agent_runs`) for storing conversation logs, sub-agent usage, error messages, and “lessons learned” for RAG.  
   - **Outcome**: Persistent session tracking, advanced analytics, and potential continuous learning.  
   - **Priority**: **Medium** (helps debugging and analytics).

7. **Deployment & Scaling with Proxmox**  
   - **Goal**: Containerize or orchestrate (orchestrator + vector DB + crawler, etc.) in a Proxmox cluster.  
   - **Outcome**: Allows horizontal scaling, environment isolation, and easier resource allocation for heavier workloads.  
   - **Priority**: **Lower** (infrastructure enhancement).

---

## First Step: Refactor Orchestrator Logic

### Summary

The **first coding step** is to extract the orchestration logic out of `archon_graph.py` into a new file (e.g., `orchestrator.py`). This will make `archon_graph.py` focus only on:

- **Defining** sub-agents (Reasoner, Router, Coder, etc.)  
- **Declaring** node functions and their typed states  

Meanwhile, `orchestrator.py` will handle:

- **Building** the `StateGraph`  
- **Compiling** it with a memory saver  
- **Exposing** methods like `start_flow()` and `resume_flow()`  

### Example Refactor

<details>
<summary>Sample code</summary>

```python
# orchestrator.py

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
# Import the existing node functions & typed state from archon_graph
from archon_graph import (
    define_scope_with_reasoner,
    coder_agent,
    finish_conversation,
    route_user_message,
    AgentState
)

class Orchestrator:
    def __init__(self):
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)

        builder.add_node("define_scope_with_reasoner", define_scope_with_reasoner)
        builder.add_node("coder_agent", coder_agent)
        builder.add_node("get_next_user_message", self.get_next_user_message)
        builder.add_node("finish_conversation", finish_conversation)

        builder.add_edge(START, "define_scope_with_reasoner")
        builder.add_edge("define_scope_with_reasoner", "coder_agent")
        builder.add_edge("coder_agent", "get_next_user_message")

        builder.add_conditional_edges(
            "get_next_user_message",
            route_user_message,
            {"coder_agent": "coder_agent", "finish_conversation": "finish_conversation"}
        )
        builder.add_edge("finish_conversation", END)

        return builder.compile(checkpointer=self.memory)

    def get_next_user_message(self, state: AgentState):
        value = interrupt({})
        return {
            "latest_user_message": value
        }

    def start_flow(self, user_message: str):
        initial_state = {
            "latest_user_message": user_message,
            "messages": [],
            "scope": ""
        }
        return self.graph.run(initial_state)

    def resume_flow(self, user_message: str):
        return self.graph.run(user_message)
```
# archon_graph.py

# (Original content minus the orchestration logic)
# - Keep your Agents (reasoner, router_agent, end_conversation_agent)
# - Keep your node functions (define_scope_with_reasoner, coder_agent, route_user_message, finish_conversation)
# - Keep your typed state (AgentState)
# - Remove references to .compile() or .run() because that's now in orchestrator.py

</details>

Next Steps
Once this refactor is tested and stable:

Implement Task 2: Create a directory for plugins and move all existing “tools” out of pydantic_ai_coder.py.
Implement Task 3: Add robust error handling and a “Diagnostic Agent” node if repeated failures occur.
With these changes, Archon V2 can more easily scale, incorporate new features, and handle complex multi-agent workflows.

If you have any questions or ideas, please comment below!


# Archon - AI Agent Builder

<img src="public/Archon.png" alt="Archon Logo" />

<div align="center" style="margin-top: 20px;margin-bottom: 30px">

<h3>🚀 **CURRENT VERSION** 🚀</h3>

**[ V2 - Agentic Workflow ]**
*Using LangGraph + Pydantic AI for multi-agent orchestration and planning*

</div>

Archon is an AI meta-agent designed to autonomously build, refine, and optimize other AI agents. 

It serves both as a practical tool for developers and as an educational framework demonstrating the evolution of agentic systems.
Archon will be developed in iterations, starting with just a simple Pydantic AI agent that can build other Pydantic AI agents,
all the way to a full agentic workflow using LangGraph that can build other AI agents with any framework.
Through its iterative development, Archon showcases the power of planning, feedback loops, and domain-specific knowledge in creating robust AI agents.

The current version of Archon is V2 as mentioned above - see [V2 Documentation](iterations/v2-agentic-workflow/README.md) for details.

## Vision

Archon demonstrates three key principles in modern AI development:

1. **Agentic Reasoning**: Planning, iterative feedback, and self-evaluation overcome the limitations of purely reactive systems
2. **Domain Knowledge Integration**: Seamless embedding of frameworks like Pydantic AI and LangGraph within autonomous workflows
3. **Scalable Architecture**: Modular design supporting maintainability, cost optimization, and ethical AI practices

## Project Evolution

### V1: Single-Agent Foundation
- Basic RAG-powered agent using Pydantic AI
- Supabase vector database for documentation storage
- Simple code generation without validation
- [Learn more about V1](iterations/v1-single-agent/README.md)

### V2: Current - Agentic Workflow (LangGraph)
- Multi-agent system with planning and execution separation
- Reasoning LLM (O3-mini/R1) for architecture planning
- LangGraph for workflow orchestration
- Support for local LLMs via Ollama
- [Learn more about V2](iterations/v2-agentic-workflow/README.md)

### Future Iterations
- V3: Self-Feedback Loop - Automated validation and error correction
- V4: Tool Library Integration - Pre-built external tool incorporation
- V5: Multi-Framework Support - Framework-agnostic agent generation
- V6: Autonomous Framework Learning - Self-updating framework adapters

### Future Integrations
- Docker
- LangSmith
- MCP
- Other frameworks besides Pydantic AI
- Other vector databases besides Supabase

## Getting Started with V2 (current version)

Since V2 is the current version of Archon, all the code for V2 is in both the `archon` and `archon/iterations/v2-agentic-workflow` directories.

### Prerequisites
- Python 3.11+
- Supabase account and database
- OpenAI/OpenRouter API key or Ollama for local LLMs
- Streamlit (for web interface)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/coleam00/archon.git
cd archon
```

2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment:
   - Rename `.env.example` to `.env`
   - Edit `.env` with your settings:
   ```env
   BASE_URL=https://api.openai.com/v1 for OpenAI, https://api.openrouter.ai/v1 for OpenRouter, or your Ollama URL
   LLM_API_KEY=your_openai_or_openrouter_api_key
   OPENAI_API_KEY=your_openai_api_key  # Required for embeddings
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   PRIMARY_MODEL=gpt-4o-mini  # Main agent model
   REASONER_MODEL=o3-mini    # Planning model
   ```

### Quick Start

1. Set up the database:
   - Execute `site_pages.sql` in your Supabase SQL Editor
   - This creates tables and enables vector similarity search

2. Crawl documentation:
```bash
python crawl_pydantic_ai_docs.py
```

3. Launch the UI:
```bash
streamlit run streamlit_ui.py
```

Visit `http://localhost:8501` to start building AI agents!

## Architecture

### Current V2 Components
- `archon_graph.py`: LangGraph workflow and agent coordination
- `pydantic_ai_coder.py`: Main coding agent with RAG capabilities
- `crawl_pydantic_ai_docs.py`: Documentation processor
- `streamlit_ui.py`: Interactive web interface
- `site_pages.sql`: Database schema

### Database Schema
```sql
CREATE TABLE site_pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT,
    chunk_number INTEGER,
    title TEXT,
    summary TEXT,
    content TEXT,
    metadata JSONB,
    embedding VECTOR(1536)
);
```

## Contributing

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

---

For version-specific details:
- [V1 Documentation](iterations/v1-single-agent/README.md)
- [V2 Documentation](iterations/v2-agentic-workflow/README.md)

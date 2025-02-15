# orchestrator.py

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# Import your node functions & AgentState from archon_graph
from archon_graph import (
    AgentState,
    define_scope_with_reasoner,
    coder_agent,
    route_user_message,
    finish_conversation
)

# Import the diagnostic node
from diagnostic_agent import diagnose_errors

# NEW: Import tool generator node functions
from tool_generator_agent import generate_tool_code, finalize_new_tool

load_dotenv()

class Orchestrator:
    """
    The 'master orchestrator' that constructs the LangGraph workflow and runs it.
    """

    def __init__(self):
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)

        # ----------------------
        # Nodes
        # ----------------------
        builder.add_node("define_scope_with_reasoner", define_scope_with_reasoner)
        builder.add_node("coder_agent", coder_agent)
        builder.add_node("get_next_user_message", self.get_next_user_message)
        builder.add_node("finish_conversation", finish_conversation)
        builder.add_node("diagnose_errors", diagnose_errors)

        # NEW: Tool generator nodes
        builder.add_node("generate_tool_code", generate_tool_code)
        builder.add_node("finalize_new_tool", finalize_new_tool)

        # We allow dynamic routing from the node decorator's {"__route__": "diagnose_errors"}
        builder.add_dynamic_route("__route__")

        # ----------------------
        # Edges
        # ----------------------
        # Standard flow
        builder.add_edge(START, "define_scope_with_reasoner")
        builder.add_edge("define_scope_with_reasoner", "coder_agent")
        builder.add_edge("coder_agent", "get_next_user_message")

        # The route_user_message node returns "coder_agent", "finish_conversation",
        # or possibly "create_tool" if user wants a new plugin.
        builder.add_conditional_edges(
            "get_next_user_message",
            route_user_message,
            {
                "coder_agent": "coder_agent",
                "finish_conversation": "finish_conversation",
                # ADD this if your route_user_message can return "create_tool"
                "create_tool": "generate_tool_code"
            }
        )
        
        # End conversation leads to END
        builder.add_edge("finish_conversation", END)

        # After diagnosing errors, we end
        builder.add_edge("diagnose_errors", END)

        # NEW: Once we generate code, we finalize it, then end (or you can route back to get_next_user_message)
        builder.add_edge("generate_tool_code", "finalize_new_tool")
        builder.add_edge("finalize_new_tool", END)

        return builder.compile(checkpointer=self.memory)

    def get_next_user_message(self, state: AgentState):
        """
        Waits for user input (streamlit or other UI calls .resume_flow).
        """
        value = interrupt({})
        return {"latest_user_message": value}

    def start_flow(self, user_message: str):
        """
        Begin a new conversation from scratch.
        """
        # Initialize error fields
        initial_state: AgentState = {
            "latest_user_message": user_message,
            "messages": [],
            "scope": "",
            "error_log": [],
            "error_retries": {}
        }
        return self.graph.run(initial_state)

    def resume_flow(self, user_message: str):
        """
        Resume after an interruption (waiting on user input).
        """
        return self.graph.run(user_message)

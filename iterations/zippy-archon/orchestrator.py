# zippy-archon/orchestrator.py

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

# Import your node functions & AgentState
from archon_graph import (
    AgentState,
    define_scope_with_reasoner,
    coder_agent,
    route_user_message,
    finish_conversation
)
from diagnostic_agent import diagnose_errors
from tool_generator_agent import generate_tool_code, finalize_new_tool

load_dotenv()

class Orchestrator:
    """
    Constructs the LangGraph workflow and runs it. 
    Each Orchestrator instance can hold its own MemorySaver for a session.
    """

    def __init__(self):
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)

        # Nodes
        builder.add_node("define_scope_with_reasoner", define_scope_with_reasoner)
        builder.add_node("coder_agent", coder_agent)
        builder.add_node("get_next_user_message", self.get_next_user_message)
        builder.add_node("finish_conversation", finish_conversation)
        builder.add_node("diagnose_errors", diagnose_errors)

        # Tool generator nodes
        builder.add_node("generate_tool_code", generate_tool_code)
        builder.add_node("finalize_new_tool", finalize_new_tool)

        builder.add_dynamic_route("__route__")

        # Edges
        builder.add_edge(START, "define_scope_with_reasoner")
        builder.add_edge("define_scope_with_reasoner", "coder_agent")
        builder.add_edge("coder_agent", "get_next_user_message")

        builder.add_conditional_edges(
            "get_next_user_message",
            route_user_message,
            {
                "coder_agent": "coder_agent",
                "finish_conversation": "finish_conversation",
                "create_tool": "generate_tool_code"
            }
        )

        # End conversation
        builder.add_edge("finish_conversation", END)

        # Diagnose then end
        builder.add_edge("diagnose_errors", END)

        # Tool code flow
        builder.add_edge("generate_tool_code", "finalize_new_tool")
        builder.add_edge("finalize_new_tool", END)

        return builder.compile(checkpointer=self.memory)

    def get_next_user_message(self, state: AgentState):
        value = interrupt({})
        return {"latest_user_message": value}

    def start_flow(self, user_message: str):
        """
        Start a new conversation from scratch.
        """
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
        Resume after waiting for user input.
        """
        return self.graph.run(user_message)

# orchestrator.py

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

# Import node functions & typed state from archon_graph:
#   - define_scope_with_reasoner
#   - coder_agent
#   - finish_conversation
#   - route_user_message
#   - AgentState
from archon_graph import (
    define_scope_with_reasoner,
    coder_agent,
    finish_conversation,
    route_user_message,
    AgentState
)

class Orchestrator:
    """
    The 'master orchestrator' that constructs the workflow graph and runs it.
    """

    def __init__(self):
        # We store the MemorySaver so that the LangGraph state can persist across runs
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        """
        Construct and compile the LangGraph flow, specifying which node
        functions appear and how they connect.
        """
        builder = StateGraph(AgentState)

        # Add nodes
        builder.add_node("define_scope_with_reasoner", define_scope_with_reasoner)
        builder.add_node("coder_agent", coder_agent)
        builder.add_node("get_next_user_message", self.get_next_user_message)
        builder.add_node("finish_conversation", finish_conversation)

        # Set up edges
        builder.add_edge(START, "define_scope_with_reasoner")
        builder.add_edge("define_scope_with_reasoner", "coder_agent")
        builder.add_edge("coder_agent", "get_next_user_message")

        builder.add_conditional_edges(
            "get_next_user_message",
            route_user_message,
            {"coder_agent": "coder_agent", "finish_conversation": "finish_conversation"}
        )

        builder.add_edge("finish_conversation", END)

        # Compile the workflow
        return builder.compile(checkpointer=self.memory)

    def get_next_user_message(self, state: AgentState):
        """
        Interrupt the flow and wait for user input (via .resume_flow).
        This function is called by the graph after coder_agent finishes.
        """
        value = interrupt({})
        return {"latest_user_message": value}

    def start_flow(self, user_message: str):
        """
        Begin a new conversation from scratch.
        """
        initial_state = {
            "latest_user_message": user_message,
            "messages": [],
            "scope": ""
        }
        return self.graph.run(initial_state)

    def resume_flow(self, user_message: str):
        """
        Resume the conversation after we have user input (like in a Streamlit or n8n UI).
        """
        return self.graph.run(user_message)

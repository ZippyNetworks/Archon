# zippy-archon/archon_graph.py

from typing import TypedDict, Annotated, List, Optional
import os
import functools
import traceback
from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

load_dotenv()

base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1')
api_key = os.getenv('LLM_API_KEY', 'no-llm-api-key-provided')

# -------------------------------------------------------------------
# AGENTS
# -------------------------------------------------------------------
reasoner_llm_model = os.getenv('REASONER_MODEL', 'o3-mini')
reasoner = Agent(
    OpenAIModel(reasoner_llm_model, base_url=base_url, api_key=api_key),
    system_prompt="You are an expert at coding AI agents with Pydantic AI..."
)

primary_llm_model = os.getenv('PRIMARY_MODEL', 'gpt-4o-mini')
router_agent = Agent(
    OpenAIModel(primary_llm_model, base_url=base_url, api_key=api_key),
    system_prompt="Your job is to route the user message..."
)

end_conversation_agent = Agent(
    OpenAIModel(primary_llm_model, base_url=base_url, api_key=api_key),
    system_prompt="Your job is to end a conversation..."
)

# -------------------------------------------------------------------
# STATE DEFINITION
# -------------------------------------------------------------------
class AgentState(TypedDict):
    latest_user_message: str
    messages: Annotated[List[bytes], lambda x, y: x + y]
    scope: str

    # We'll store error info here
    error_log: Optional[List[str]]
    error_retries: Optional[dict]

# -------------------------------------------------------------------
# ERROR-HANDLING DECORATOR
# -------------------------------------------------------------------
def error_handler_decorator(node_name: str, max_retries: int = 1):
    """
    Decorator to catch errors in node functions, store them in state['error_log'],
    and possibly route to 'diagnose_errors' if threshold is reached.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(state: AgentState, *args, **kwargs):
            if "error_log" not in state:
                state["error_log"] = []
            if "error_retries" not in state:
                state["error_retries"] = {}

            attempt = state["error_retries"].get(node_name, 0)
            try:
                result = await func(state, *args, **kwargs)
                state["error_retries"][node_name] = 0  # reset on success
                return result
            except Exception as e:
                trace = traceback.format_exc()
                error_message = f"Error in node '{node_name}': {str(e)}\nTraceback:\n{trace}"
                state["error_log"].append(error_message)

                attempt += 1
                state["error_retries"][node_name] = attempt

                if attempt >= max_retries:
                    return {"__route__": "diagnose_errors"}
                else:
                    raise
        return wrapper
    return decorator

# -------------------------------------------------------------------
# NODE FUNCTIONS
# -------------------------------------------------------------------
@error_handler_decorator("define_scope_with_reasoner", max_retries=2)
async def define_scope_with_reasoner(state: AgentState):
    """
    Use the reasoner agent to define a scope for building an AI agent.
    """
    user_input = state["latest_user_message"]
    result = await reasoner.run(
        f"Analyze user request: {user_input}\n"
        "Return a scope for building a Pydantic AI agent."
    )
    return {"scope": result.data}

@error_handler_decorator("coder_agent", max_retries=2)
async def coder_agent(state: AgentState, writer=None):
    """
    Main coding agent node. Takes the scope/user messages and builds code or modifies existing code.
    """
    return {"messages": []}

@error_handler_decorator("route_user_message", max_retries=1)
async def route_user_message(state: AgentState):
    """
    Decide if we keep coding, finish, or create a tool if user says 'create tool'.
    """
    user_msg = state["latest_user_message"].lower()
    result = await router_agent.run(user_msg)

    if "finish" in user_msg:
        return "finish_conversation"
    elif "create tool" in user_msg or "new plugin" in user_msg:
        return "create_tool"

    return "coder_agent"

@error_handler_decorator("finish_conversation", max_retries=1)
async def finish_conversation(state: AgentState, writer=None):
    """
    End the conversation with a final message from the end_conversation_agent.
    """
    user_msg = state["latest_user_message"]
    result = await end_conversation_agent.run(
        f"User last message: {user_msg}\nPlease say goodbye."
    )
    return {"messages": [result.new_messages_json()]}

# archon_graph.py

from typing import TypedDict, Annotated, List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
import os
from dotenv import load_dotenv
load_dotenv()

# Agents
base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1')
api_key = os.getenv('LLM_API_KEY', 'no-llm-api-key-provided')

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

# This typed dictionary defines the shape of the state that flows through the graph
class AgentState(TypedDict):
    latest_user_message: str
    messages: Annotated[List[bytes], lambda x, y: x + y]
    scope: str

# Node function: define the scope with the reasoner
async def define_scope_with_reasoner(state: AgentState):
    """
    Your logic for the reasoner node goes here. Typically:
    1) Possibly fetch documentation pages
    2) Use reasoner.run(...) to create a scope
    3) Return an updated state
    """
    # Example outline (update with your real code):
    user_input = state["latest_user_message"]
    # ... call the reasoner agent ...
    # scope = ...
    # Save the scope to a file or memory if needed
    return {"scope": "<your-scope-here>"}

# Node function: main coder agent
async def coder_agent(state: AgentState, writer=None):
    """
    This node uses your coding agent to generate code for the user.
    """
    # Example outline:
    # user_input = state["latest_user_message"]
    # message_history = state["messages"]
    # ...
    # return {"messages": [result.new_messages_json()]}
    return {"messages": []}  # placeholder

# Node function: route user message
async def route_user_message(state: AgentState):
    """
    Uses the router_agent to decide if we 'finish_conversation' or 'coder_agent'.
    """
    user_msg = state["latest_user_message"]
    # Example logic (update with your real code):
    result = await router_agent.run(user_msg)
    if "finish" in result.data.lower():
        return "finish_conversation"
    else:
        return "coder_agent"

# Node function: finish conversation
async def finish_conversation(state: AgentState, writer=None):
    """
    Ends the conversation, possibly giving instructions for how to run the code generated.
    """
    user_msg = state["latest_user_message"]
    # Example logic:
    # result = await end_conversation_agent.run(user_msg)
    # return {"messages": [result.new_messages_json()]}
    return {"messages": []}  # placeholder

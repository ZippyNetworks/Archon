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

# This typed dictionary defines the shape of state that flows through the graph
class AgentState(TypedDict):
    latest_user_message: str
    messages: Annotated[List[bytes], lambda x, y: x + y]
    scope: str

# Node function: define the scope with the reasoner
async def define_scope_with_reasoner(state: AgentState):
    # Implementation from your original code...
    # ...
    return {"scope": scope}

# Node function: main coder agent
async def coder_agent(state: AgentState, writer=None):
    # Implementation from your original code...
    # ...
    return {"messages": [result.new_messages_json()]}

# Node function: route user message to either continue coding or finish
async def route_user_message(state: AgentState):
    # Implementation from your original code...
    # ...
    return "coder_agent"  # or "finish_conversation"

# Node function: finish conversation
async def finish_conversation(state: AgentState, writer=None):
    # Implementation from your original code...
    # ...
    return {"messages": [result.new_messages_json()]}

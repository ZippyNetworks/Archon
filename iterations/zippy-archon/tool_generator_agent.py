# zippy-archon/tool_generator_agent.py

import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from archon_graph import AgentState

# We assume you have a plugins directory with plugin_manager
from plugins.plugin_manager import load_plugins

load_dotenv()

BASE_URL = os.getenv('BASE_URL', 'https://api.openai.com/v1')
API_KEY = os.getenv('LLM_API_KEY', 'no-llm-api-key-provided')
TOOL_GEN_MODEL = os.getenv('TOOL_GEN_MODEL', 'gpt-4o-mini')

tool_generator_agent = Agent(
    OpenAIModel(TOOL_GEN_MODEL, base_url=BASE_URL, api_key=API_KEY),
    system_prompt="""
You are a Tool Generator Agent. 
Given a user request like "Create a Slack plugin," produce a .py plugin 
with 'name', 'description', and a 'run' method. 
"""
)

async def generate_tool_code(state: AgentState):
    user_req = state["latest_user_message"]
    prompt = f"""
User request: {user_req}

Generate a Python plugin that implements a class with 'name', 'description', and 'run(...)'.
"""
    result = await tool_generator_agent.run(prompt)
    return {"generated_code": result.data}

async def finalize_new_tool(state: AgentState):
    code = state.get("generated_code", "")
    if not code.strip():
        return {"tool_creation_status": "No code generated."}

    file_name = "tool_generated.py"
    file_path = os.path.join("plugins", file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    load_plugins("plugins")

    return {"tool_creation_status": f"Plugin created: {file_name}"}

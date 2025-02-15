# tool_generator_agent.py

import os
from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Import your typed AgentState from archon_graph
from archon_graph import AgentState

# If your plugins/plugin_manager code is separate, you'll import load_plugins from there
from plugins.plugin_manager import load_plugins

load_dotenv()

BASE_URL = os.getenv('BASE_URL', 'https://api.openai.com/v1')
API_KEY = os.getenv('LLM_API_KEY', 'no-llm-api-key-provided')
TOOL_GEN_MODEL = os.getenv('TOOL_GEN_MODEL', 'gpt-4o-mini')

# A minimal plugin template.
PLUGIN_TEMPLATE = """\"\"\"
{tool_description}
\"\"\"

import os

class {class_name}:
    name = "{tool_name}"
    description = "{tool_description}"

    def run(self, *args, **kwargs):
        # Insert logic here
        return "Example run output"
"""

# Define the specialized Tool Generator Agent
tool_generator_agent = Agent(
    OpenAIModel(TOOL_GEN_MODEL, base_url=BASE_URL, api_key=API_KEY),
    system_prompt="""
You are a Tool Generator Agent. Your job is to produce Python plugin files 
that fit our plugin architecture. 
When given a request like 'Build me a Slack plugin', you will:
1. Read any relevant API docs (if provided).
2. Generate a .py plugin with a class implementing:
   - name
   - description
   - run(...) method
3. Provide complete Python code in your final answer.

Use the provided PLUGIN_TEMPLATE for structure if possible.
"""
)

async def generate_tool_code(state: AgentState):
    """
    Node function that calls the Tool Generator Agent to create plugin code
    based on the user's request in state['latest_user_message'].
    """
    user_req = state["latest_user_message"]
    
    prompt = f"""
User request: {user_req}

Please create a new plugin source code snippet following our plugin template.
Fill in placeholders for name, description, and run method as best you can.
    """

    # Run the agent
    result = await tool_generator_agent.run(prompt)
    plugin_code = result.data

    # We store the generated code in state so the next node can finalize (write to disk).
    return {"generated_code": plugin_code}

async def finalize_new_tool(state: AgentState):
    """
    After generate_tool_code, write the plugin code to a .py file in the plugins directory,
    then reload the plugin registry so it's immediately available.
    """
    code = state.get("generated_code", "")
    if not code.strip():
        return {"tool_creation_status": "No code generated."}

    # We'll pick a default name for the file, or parse from user request
    file_name = "tool_generated.py"

    # Optionally parse user input or do fancy naming logic:
    # user_req = state["latest_user_message"].lower()
    # if "slack" in user_req:
    #     file_name = "tool_slack.py"
    # ...
    
    file_path = os.path.join("plugins", file_name)

    # Write the code to a new plugin file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    # Reload plugins
    load_plugins("plugins")

    return {"tool_creation_status": f"Plugin created: {file_name}"}

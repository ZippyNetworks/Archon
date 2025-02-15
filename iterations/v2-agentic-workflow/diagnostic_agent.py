# diagnostic_agent.py

import os
import traceback
from dotenv import load_dotenv
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# If you store typed states in archon_graph or a separate file, you can import them:
# from archon_graph import AgentState
# Or, if you prefer a separate states.py, import from there.

# For this example, let's define the same shape used by your system.
# Ideally, you'll import the real AgentState from archon_graph.py to avoid duplication.
from typing import TypedDict, Annotated, List

load_dotenv()

base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1')
api_key = os.getenv('LLM_API_KEY', 'no-llm-api-key-provided')
diagnostic_llm_model = os.getenv('DIAGNOSTIC_MODEL', 'gpt-4o-mini')

# Example typed state if you haven't extracted it elsewhere:
class AgentState(TypedDict):
    latest_user_message: str
    messages: Annotated[List[bytes], lambda x, y: x + y]
    scope: str
    # Optionally store error info or retries
    error_log: Optional[List[str]]
    error_retries: Optional[dict]

# Define the Diagnostic Agent
diagnostic_agent = Agent(
    OpenAIModel(diagnostic_llm_model, base_url=base_url, api_key=api_key),
    system_prompt="""
You are a Diagnostic Agent. The system will provide you with recent error logs.
Your job is to:
1. Analyze these errors to identify likely causes.
2. Propose specific solutions or follow-up questions for the developer.
"""
)

# Node function for LangGraph: diagnose_errors
async def diagnose_errors(state: AgentState) -> dict:
    """
    Looks up the error_log in state, calls the Diagnostic Agent to analyze them,
    and returns the agent's feedback for further handling.
    """
    error_log = state.get("error_log", [])
    if not error_log:
        # If no errors, just return empty
        return {"diagnostic_feedback": "No errors to diagnose."}

    # Summarize the last few errors
    error_summary = "\n\n".join(error_log[-3:])  # last 3 errors or so

    # Create a prompt for the Diagnostic Agent
    prompt = f"""
The system has encountered repeated errors:

{error_summary}

Please analyze these errors and suggest possible reasons, fixes, 
or additional clarifications that might help resolve them.
    """

    # Run the Diagnostic Agent
    try:
        result = await diagnostic_agent.run(prompt)
        # We can store the result in a new field in the state
        return {"diagnostic_feedback": result.data}
    except Exception as e:
        tb = traceback.format_exc()
        # If the diagnostic agent itself fails, store that info
        fail_msg = f"Diagnostic Agent failed: {e}\nTraceback:\n{tb}"
        return {"diagnostic_feedback": fail_msg}

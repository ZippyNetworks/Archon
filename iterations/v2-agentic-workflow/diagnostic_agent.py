# diagnostic_agent.py

import os
import traceback
from dotenv import load_dotenv
from typing import List

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
# Import the AgentState from archon_graph to avoid re-defining it
from archon_graph import AgentState

load_dotenv()

base_url = os.getenv('BASE_URL', 'https://api.openai.com/v1')
api_key = os.getenv('LLM_API_KEY', 'no-llm-api-key-provided')
diagnostic_llm_model = os.getenv('DIAGNOSTIC_MODEL', 'gpt-4o-mini')

# Define the specialized Diagnostic Agent
diagnostic_agent = Agent(
    OpenAIModel(diagnostic_llm_model, base_url=base_url, api_key=api_key),
    system_prompt="""
You are a Diagnostic Agent. The system will provide you with recent error logs.
Your job is to:
1. Analyze these errors to identify likely causes.
2. Propose specific solutions or follow-up questions for the developer.
"""
)

async def diagnose_errors(state: AgentState) -> dict:
    """
    Reads error logs from state['error_log'], calls the Diagnostic Agent, 
    and returns feedback in 'diagnostic_feedback'.
    """
    error_log = state.get("error_log", [])
    if not error_log:
        return {"diagnostic_feedback": "No errors to diagnose."}

    # Summarize the last few errors
    error_summary = "\n\n".join(error_log[-3:])  # last 3 errors

    prompt = f"""
The system has encountered repeated errors:

{error_summary}

Please analyze these errors and suggest possible reasons, fixes, 
or additional clarifications that might help resolve them.
    """

    try:
        result = await diagnostic_agent.run(prompt)
        return {"diagnostic_feedback": result.data}
    except Exception as e:
        tb = traceback.format_exc()
        fail_msg = f"Diagnostic Agent failed: {e}\nTraceback:\n{tb}"
        return {"diagnostic_feedback": fail_msg}

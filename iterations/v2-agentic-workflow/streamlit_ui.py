# streamlit_ui.py

import streamlit as st
import asyncio
from orchestrator import Orchestrator

# If you have logs or DB, import them here
# from supabase import Client
# from .env or something

st.set_page_config(page_title="Archon - Agent Builder", layout="wide")

# Initialize Orchestrator
orchestrator = Orchestrator()

@st.cache_resource
def get_thread_id():
    # If you want separate session IDs for each user or conversation
    import uuid
    return str(uuid.uuid4())

thread_id = get_thread_id()

async def run_flow_stream(user_input: str):
    """
    Runs the orchestrator in "streaming" mode, if you have that set up.
    If not, you can just call .start_flow(...) or .resume_flow(...) and yield the final text.
    """
    # If first user message, start_flow
    if len(st.session_state.messages) == 1:
        # This might not be streaming if your orchestrator doesn't yield
        # We'll simulate partial chunks anyway
        results = orchestrator.start_flow(user_input)
        yield str(results)
    else:
        results = orchestrator.resume_flow(user_input)
        yield str(results)

def main():
    st.title("Archon - Agent Builder")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show existing conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["type"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Describe your AI agent or request a new plugin...")
    if user_input:
        # Add to session
        st.session_state.messages.append({"type": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response_content = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            async def handle_flow():
                async for chunk in run_flow_stream(user_input):
                    nonlocal response_content
                    response_content += chunk
                    message_placeholder.markdown(response_content)
            asyncio.run(handle_flow())

        st.session_state.messages.append({"type": "assistant", "content": response_content})

        # After the flow, we can check the final orchestrator state for special fields
        final_state = orchestrator.graph.state  # Or however you store the final state
        # E.g., if the Diagnostic Agent was triggered
        if "diagnostic_feedback" in final_state:
            st.error("Diagnostics:\n" + final_state["diagnostic_feedback"])
        # If the Tool Generator ran
        if "tool_creation_status" in final_state:
            st.success(final_state["tool_creation_status"])

if __name__ == "__main__":
    asyncio.run(main())

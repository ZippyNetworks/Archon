# streamlit_ui.py

from __future__ import annotations
import streamlit as st
import asyncio
from orchestrator import Orchestrator

# If you need any other imports, like your DB or logs, keep them.
# from openai import AsyncOpenAI
# from supabase import Client

orchestrator = Orchestrator()

@st.cache_resource
def get_thread_id():
    import uuid
    return str(uuid.uuid4())

thread_id = get_thread_id()

async def run_agent_with_streaming(user_input: str):
    # If this is the very first user message (i.e., we only have a single system msg in state),
    # start a new flow
    if len(st.session_state.messages) == 1:
        async for partial_text in orchestrator.start_flow(user_input):
            yield partial_text
    else:
        # Otherwise, resume the flow
        async for partial_text in orchestrator.resume_flow(user_input):
            yield partial_text

def main():
    st.title("Archon - Agent Builder")
    st.write("Describe an AI agent you want to build...")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["type"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("What do you want to build today?")
    if user_input:
        st.session_state.messages.append({"type": "human", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Placeholder for streaming output
        response_content = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            # Stream
            async def handle_stream():
                async for chunk in run_agent_with_streaming(user_input):
                    nonlocal response_content
                    response_content += chunk
                    message_placeholder.markdown(response_content)
            asyncio.run(handle_stream())

        st.session_state.messages.append({"type": "ai", "content": response_content})

if __name__ == "__main__":
    asyncio.run(main())

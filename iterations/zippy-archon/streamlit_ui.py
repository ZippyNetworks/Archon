# zippy-archon/streamlit_ui.py

import streamlit as st
import requests
import uuid

API_URL_START = "http://localhost:8080/start_flow"
API_URL_RESUME = "http://localhost:8080/resume_flow"

# We'll store a session_id in st.session_state to keep concurrency separate
def init_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

init_session()

st.title("Zippy's Archon - Streamlit UI with Concurrency")

def display_messages():
    for msg in st.session_state.messages:
        with st.chat_message(msg["type"]):
            st.markdown(msg["content"])

display_messages()

user_input = st.chat_input("Ask Archon, or type 'create tool' to build a plugin...")
if user_input:
    st.session_state.messages.append({"type": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Decide if this is the first message or a resume
    if len(st.session_state.messages) == 1:
        # first message -> start_flow
        payload = {
            "session_id": st.session_state.session_id,
            "user_message": user_input
        }
        resp = requests.post(API_URL_START, json=payload).json()
    else:
        # subsequent -> resume_flow
        payload = {
            "session_id": st.session_state.session_id,
            "user_message": user_input
        }
        resp = requests.post(API_URL_RESUME, json=payload).json()

    # Show result
    final_text = resp.get("result", "")
    final_state = resp.get("state", {})
    st.session_state.messages.append({"type": "assistant", "content": final_text})

    with st.chat_message("assistant"):
        st.markdown(final_text)

    # Check if there's special data like diagnostic_feedback or tool_creation_status
    diagnostic_feedback = final_state.get("diagnostic_feedback")
    if diagnostic_feedback:
        st.error("Diagnostic Feedback:\n" + diagnostic_feedback)

    tool_creation_status = final_state.get("tool_creation_status")
    if tool_creation_status:
        st.success(tool_creation_status)


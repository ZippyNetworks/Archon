# zippy-archon/archon_server.py

import os
from fastapi import FastAPI, Request
from typing import Dict

from orchestrator import Orchestrator

# We'll keep a dictionary of session_id -> Orchestrator instance
orchestrators: Dict[str, Orchestrator] = {}

app = FastAPI()

@app.post("/start_flow")
async def start_flow(request: Request):
    """
    Starts a new flow or re-creates an Orchestrator for a given session_id.
    Expects JSON: {"user_message": "...", "session_id": "..."}
    """
    data = await request.json()
    user_message = data.get("user_message", "")
    session_id = data.get("session_id", "default")

    # If we don't have an Orchestrator for this session, create one
    if session_id not in orchestrators:
        orchestrators[session_id] = Orchestrator()

    result = orchestrators[session_id].start_flow(user_message)
    final_state = orchestrators[session_id].graph.state

    return {"result": str(result), "state": final_state, "session_id": session_id}

@app.post("/resume_flow")
async def resume_flow(request: Request):
    """
    Resumes an existing flow for the given session_id.
    Expects JSON: {"user_message": "...", "session_id": "..."}
    """
    data = await request.json()
    user_message = data.get("user_message", "")
    session_id = data.get("session_id", "default")

    if session_id not in orchestrators:
        # If no orchestrator, create one or return an error
        orchestrators[session_id] = Orchestrator()

    result = orchestrators[session_id].resume_flow(user_message)
    final_state = orchestrators[session_id].graph.state

    return {"result": str(result), "state": final_state, "session_id": session_id}

@app.post("/reset_session")
async def reset_session(request: Request):
    """
    Clears the orchestrator for a given session_id, effectively resetting the conversation.
    """
    data = await request.json()
    session_id = data.get("session_id", "default")

    if session_id in orchestrators:
        del orchestrators[session_id]

    return {"status": "session reset", "session_id": session_id}

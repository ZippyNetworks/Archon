# archon_server.py

import os
from fastapi import FastAPI, Request
from orchestrator import Orchestrator

# If you want concurrency and multiple user sessions, you might keep a dict of orchestrator instances
# For now, we'll do a single global Orchestrator for simplicity
orchestrator = Orchestrator()

app = FastAPI()

@app.post("/start_flow")
async def start_flow(request: Request):
    """
    Initializes a brand-new flow using the Orchestrator.
    Payload might look like: {"user_message": "Hello, I'd like to do X"}
    """
    data = await request.json()
    user_message = data.get("user_message", "")

    # Optionally parse a session_id if you want multiple concurrent sessions
    # session_id = data.get("session_id", "default")

    result = orchestrator.start_flow(user_message)
    # We'll return the entire result plus the final state
    # The 'result' can be partial text or a generator if you want streaming
    state = orchestrator.graph.state  # The final or current state
    return {"result": result, "state": state}

@app.post("/resume_flow")
async def resume_flow(request: Request):
    """
    Resumes an existing flow after an interruption (waiting for user input).
    Payload might look like: {"user_message": "Ok, let's do it"}
    """
    data = await request.json()
    user_message = data.get("user_message", "")

    # session_id = data.get("session_id", "default")

    result = orchestrator.resume_flow(user_message)
    state = orchestrator.graph.state
    return {"result": result, "state": state}

from fastapi import FastAPI, HTTPException
from models import Observation, Action, Reward, State, ActionType
from env import EmailTriageEnv
from tasks import create_task_1, create_task_2, create_task_3
from graders import GRADERS
from typing import Dict, Any, List
import uvicorn
import uuid

app = FastAPI(
    title="Email Triage OpenEnv",
    description="A real-world email triage and management simulator for AI agents.",
    version="1.0.0",
)

# In-memory store for active environments
envs: Dict[str, EmailTriageEnv] = {}

@app.post("/reset", response_model=Observation)
async def reset(task_id: str = "archive_newsletters"):
    if task_id == "archive_newsletters":
        emails = create_task_1()
    elif task_id == "reply_urgent":
        emails = create_task_2()
    elif task_id == "inbox_clean":
        emails = create_task_3()
    else:
        raise HTTPException(status_code=404, detail="Task not found")

    session_id = str(uuid.uuid4())
    env = EmailTriageEnv(initial_emails=emails)
    envs[session_id] = env

    obs = await env.reset()
    obs.last_action_result = f"Session: {session_id}. Ready for task: {task_id}"
    return obs

@app.post("/step", response_model=Dict[str, Any])
async def step(session_id: str, action: Action):
    if session_id not in envs:
        raise HTTPException(status_code=404, detail="Session not found")

    env = envs[session_id]
    obs, reward, done, info = await env.step(action)

    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info
    }

@app.get("/state", response_model=State)
async def state(session_id: str):
    if session_id not in envs:
        raise HTTPException(status_code=404, detail="Session not found")
    return await envs[session_id].state()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/metadata")
async def metadata():
    return {
        "name": "email_triage",
        "description": "A real-world email triage and management simulator for AI agents.",
        "version": "1.0.0",
        "tasks": ["archive_newsletters", "reply_urgent", "inbox_clean"]
    }

@app.get("/schema")
async def schema():
    return {
        "action": Action.model_json_schema(),
        "observation": Observation.model_json_schema(),
        "state": State.model_json_schema(),
    }

import gradio as gr
from server.ui import demo

app = gr.mount_gradio_app(app, demo, path="/")

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()

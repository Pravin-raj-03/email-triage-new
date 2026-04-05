from fastapi import FastAPI, HTTPException
from models import Observation, Action, Reward, State, ActionType
from env import EmailTriageEnv
from tasks import create_task_1, create_task_2, create_task_3
from graders import GRADERS
from typing import Dict, Any, List
import uuid

app = FastAPI(title="Email Triage OpenEnv")

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
    
    obs = env.reset()
    # Add session id to info for client tracking
    obs.last_action_result = f"Session: {session_id}. Ready for task: {task_id}"
    return obs

@app.post("/step", response_model=Dict[str, Any])
async def step(session_id: str, action: Action):
    if session_id not in envs:
        raise HTTPException(status_code=404, detail="Session not found")
    
    env = envs[session_id]
    obs, reward, done, info = env.step(action)
    
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
    
    return envs[session_id].state()

@app.get("/health")
async def health():
    return {"status": "ok"}

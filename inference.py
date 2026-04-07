import asyncio
import os
import json
import textwrap
from typing import List, Optional, Dict, Any
from openai import OpenAI

# Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-4o")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional - if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
MAX_STEPS = 10
BENCHMARK = "email_triage"

# Import local environment
from env import EmailTriageEnv
from models import Action, ActionType
from tasks import TAS_GENERATORS
from graders import GRADERS

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

async def run_single_task(client: OpenAI, task_id: str):
    emails = TAS_GENERATORS[task_id]()
    env = EmailTriageEnv(initial_emails=emails)
    
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    
    obs = await env.reset()
    done = False
    
    for step in range(1, MAX_STEPS + 1):
        if done:
            break
            
        # Prepare observation for LLM
        inbox_str = "\n".join([
            f"ID: {e.id} | From: {e.sender} | Subject: {e.subject} | Cat: {e.category} | Urgent: {e.is_urgent}" 
            for e in obs.emails
        ])
        
        prompt = f"""
        You are an email triage assistant.
        Inbox:
        {inbox_str}

        Actions:
        - {{"action_type": "archive", "email_id": "ID"}}
        - {{"action_type": "delete", "email_id": "ID"}}
        - {{"action_type": "reply", "email_id": "ID", "reply_text": "REPLY"}}
        - {{"action_type": "mark_read", "email_id": "ID"}}

        Respond with exactly ONE action JSON.
        """
        
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            action_json = completion.choices[0].message.content.strip()
            action_data = json.loads(action_json)
            
            # Step env
            action = Action(**action_data)
            obs, reward, done, info = await env.step(action)
            
            rewards.append(reward.value)
            steps_taken = step
            error = None
            
            log_step(step=step, action=action_json, reward=reward.value, done=done, error=error)
            
        except Exception as e:
            print(f"[DEBUG] Model request failed: {e}", flush=True)
            log_step(step=step, action="error", reward=0.0, done=True, error=str(e))
            break
            
    # Final Grade
    score = GRADERS[task_id](env.inbox, [])
    success = score >= 0.1
    
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return score

async def main():
    client = OpenAI(
        base_url=os.environ["API_BASE_URL"],
        api_key=os.environ["API_KEY"]
    )
    
    tasks = ["archive_newsletters", "reply_urgent", "inbox_clean"]
    for task in tasks:
        await run_single_task(client, task)

if __name__ == "__main__":
    asyncio.run(main())

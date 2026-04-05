import asyncio
import random
from env import EmailTriageEnv
from tasks import TAS_GENERATORS
from graders import GRADERS
from models import Action, ActionType

async def run_random_agent(task_id: str):
    print(f"\n[START] Testing task: {task_id}")
    emails = TAS_GENERATORS[task_id]()
    env = EmailTriageEnv(initial_emails=emails)
    
    obs = await env.reset()
    print(f"  Initialized Inbox with {len(obs.emails)} emails.")
    
    rewards = []
    
    for step in range(1, 11):
        if env.done:
            break
            
        # Pick a random email and random valid action
        if not obs.emails:
            break
            
        target_email = random.choice(obs.emails)
        action_type = random.choice(list(ActionType))
        
        action = Action(
            action_type=action_type,
            email_id=target_email.id,
            reply_text="Automated reply" if action_type == ActionType.REPLY else None
        )
        
        print(f"  [STEP {step}] Attempting to {action.action_type.value} email '{target_email.id}'")
        obs, reward, done, info = await env.step(action)
        rewards.append(reward.value)
        
        print(f"     => Result: {obs.last_action_result} | Reward: {reward.value} | Done: {done}")

    # Final Grade
    score = GRADERS[task_id](env.inbox, [])
    success = score > 0.0
    print(f"[END] Grade: {score:.2f} | Success: {success} | Total Steps: {len(rewards)}")

async def main():
    print("--- DUMMY AGENT TEST ---")
    for task in ["archive_newsletters", "reply_urgent", "inbox_clean"]:
        await run_random_agent(task)

if __name__ == "__main__":
    asyncio.run(main())

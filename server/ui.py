import gradio as gr
import pandas as pd
from models import Action, ActionType
import asyncio
import asyncio

async def start_task(task_id):
    from server.app import reset
    obs = await reset(task_id)
    # Parse session ID from last_action_result: "Session: {session_id}. Ready for task: {task_id}"
    session_str = obs.last_action_result.split("Session: ")[1].split(".")[0]
    
    df = pd.DataFrame([e.model_dump() for e in obs.emails])
    if len(df) > 0:
        df = df[["id", "sender", "subject", "category", "is_urgent", "status"]]
    
    return session_str, df, obs.last_action_result, 0, "No reward yet", "🟢 Running"

async def take_action(session_id, action_type, email_id, reply_text):
    from server.app import step
    if not session_id:
        # Default empty df format
        df = pd.DataFrame(columns=["id", "sender", "subject", "category", "is_urgent", "status"])
        return session_id, df, "⚠️ Error: Please Start a Task first.", 0, "No reward yet", "🔴 Not Started"
        
    try:
        action = Action(action_type=ActionType(action_type), email_id=email_id, reply_text=reply_text or None)
        result = await step(session_id, action)
        
        obs = result["observation"]
        reward = result["reward"]["value"]
        done = result["done"]
        
        df = pd.DataFrame(obs["emails"])
        if len(df) > 0:
            df = df[["id", "sender", "subject", "category", "is_urgent", "status"]]
            
        status_msg = "🏁 Game Over!" if done else "🟢 Running"
            
        return session_id, df, obs["last_action_result"], obs["step_count"], f"{reward:.2f}", status_msg
    except Exception as e:
        df = pd.DataFrame(columns=["id", "sender", "subject", "category", "is_urgent", "status"])
        return session_id, df, f"⚠️ Error: {str(e)}", 0, "Error", "🔴 Error"

# Gradio Interface theme
theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
)

with gr.Blocks(theme=theme, title="Email Triage Agent Sandbox") as demo:
    gr.Markdown("# 📧 Email Triage OpenEnv Arena")
    gr.Markdown("Welcome! This is the frontend interface for the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) Email Triage simulator. Choose a task level below and manage the inbox manually to see what an AI agent experiences. The underlying `step()` and `reset()` programmatic APIs remain fully active for bots.")
    
    session_state = gr.State("")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1. Setup & Status")
            task_dropdown = gr.Dropdown(
                choices=["archive_newsletters", "reply_urgent", "inbox_clean"], 
                value="archive_newsletters", 
                label="Environment Task Variant"
            )
            reset_btn = gr.Button("🚀 Start / Reset Task", variant="primary")
            
            with gr.Group():
                gr.Markdown("**Current State Details:**")
                status_box = gr.Textbox(label="Status", value="🔴 Not Started", interactive=False)
                reward_box = gr.Textbox(label="Latest Reward", value="No reward yet", interactive=False)
                steps_box = gr.Number(label="Step Count", value=0, interactive=False)
                
            gr.Markdown("---")
            gr.Markdown("### 3. Action Space")
            gr.Markdown("Select an action and the ID of the email to apply it to.")
            action_dropdown = gr.Dropdown(
                choices=[e.value for e in ActionType], 
                value="archive", 
                label="Action Type"
            )
            target_id = gr.Textbox(label="Target Email ID (e.g. 1)")
            reply_input = gr.Textbox(label="Reply Message (Optional)", placeholder="Type your reply here...")
            step_btn = gr.Button("⚡ Execute Action", variant="secondary")

        with gr.Column(scale=3):
            gr.Markdown("### 2. Observation (Inbox State)")
            result_box = gr.Textbox(label="Environment Logger", lines=2, interactive=False)
            inbox_df = gr.Dataframe(
                headers=["id", "sender", "subject", "category", "is_urgent", "status"],
                interactive=False,
                label="Current Emails in Inbox"
            )
            
    # Connect Interactions
    reset_btn.click(
        fn=start_task,
        inputs=[task_dropdown],
        outputs=[session_state, inbox_df, result_box, steps_box, reward_box, status_box]
    )
    
    step_btn.click(
        fn=take_action,
        inputs=[session_state, action_dropdown, target_id, reply_input],
        outputs=[session_state, inbox_df, result_box, steps_box, reward_box, status_box]
    )

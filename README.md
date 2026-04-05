# Email Triage OpenEnv Interface

## Environment Description
The **Email Triage OpenEnv** is a real-world task simulation designed for AI agents to learn and perform inbox management tasks. In this environment, an agent interacts with a virtual email store where it can archive, delete, reply, and mark emails as read. The goal is to maximize the efficiency and accuracy of email processing while avoiding destructive actions on important or urgent content.

## Motivation
Email triage is a common, high-value task for AI assistants. It requires understanding of context, priority, and user intent. This environment provides a standardized interface (OpenEnv) to evaluate and train agents on these capabilities.

## Action and Observation Space

### Action Space (Typed Pydantic)
```python
{
    "action_type": "archive" | "delete" | "reply" | "mark_read",
    "email_id": "string",
    "reply_text": "string (optional)"
}
```

### Observation Space (Typed Pydantic)
```python
{
    "emails": [
        {
            "id": "string",
            "sender": "string",
            "subject": "string",
            "body": "string",
            "status": "inbox" | "archived" | "deleted",
            "category": "primary" | "social" | "promotions" | "spam",
            "is_urgent": "boolean"
        }
    ],
    "last_action_result": "string",
    "step_count": "integer"
}
```

## Task Descriptions

1.  **Archive Newsletters (Easy)**: The agent must identify newsletters (promotions/social) and archive them.
2.  **Urgent Reply (Medium)**: The agent must find an email marked as urgent and reply with an appropriate message.
3.  **Inbox Management (Hard)**: A multi-step task involving deleting spam, archiving updates, and handling urgent requests.

## Setup and Usage

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```bash
   uv run uvicorn server.app:app --host 0.0.0.0 --port 7860
   ```

### Baseline Inference
To run the baseline agent (ensure `HF_TOKEN` is set):
```bash
python inference.py
```

### Docker
```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

## Baseline Scores
- **Archive Newsletters**: 1.00
- **Urgent Reply**: 1.00
- **Inbox Management**: 1.00
*(Scores are based on a GPT-4o agent's performance in zero-shot interaction)*

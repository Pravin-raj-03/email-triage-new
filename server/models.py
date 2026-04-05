from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class EmailStatus(str, Enum):
    INBOX = "inbox"
    ARCHIVED = "archived"
    DELETED = "deleted"

class Email(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str = "2024-01-01T00:00:00Z"
    status: EmailStatus = EmailStatus.INBOX
    category: Literal["primary", "social", "promotions", "spam"] = "primary"
    is_urgent: bool = False

class ActionType(str, Enum):
    ARCHIVE = "archive"
    DELETE = "delete"
    REPLY = "reply"
    MARK_READ = "mark_read"

class Action(BaseModel):
    action_type: ActionType = Field(..., description="The type of action to perform.")
    email_id: str = Field(..., description="The ID of the email to target.")
    reply_text: Optional[str] = Field(None, description="The message content for a reply action.")

class Observation(BaseModel):
    emails: List[Email] = Field(..., description="List of emails currently in the inbox.")
    last_action_result: Optional[str] = Field(None, description="Result message from the last action performed.")
    step_count: int = Field(0, description="Number of steps taken in the current episode.")

class Reward(BaseModel):
    value: float = Field(..., description="The reward signal for the last action (0.0 to 1.0).")
    explanation: Optional[str] = Field(None, description="A brief description of why this reward was given.")

class State(BaseModel):
    inbox: Dict[str, Email]
    done: bool = False
    info: Dict[str, Any] = {}

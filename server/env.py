from typing import List, Dict, Any, Tuple
import uuid
import datetime
from models import Email, EmailStatus, Action, Observation, Reward, State, ActionType

class EmailTriageEnv:
    def __init__(self, initial_emails: List[Email] = None):
        self.initial_emails = initial_emails or []
        self.inbox = {e.id: e.model_copy() for e in self.initial_emails}
        self.step_count = 0
        self.done = False
        self.info = {}
        self.last_action_result = "Initialized."

    async def reset(self) -> Observation:
        self.inbox = {e.id: e.model_copy() for e in self.initial_emails}
        self.step_count = 0
        self.done = False
        self.info = {}
        self.last_action_result = "Reset complete."
        return self._get_observation()

    def _get_observation(self) -> Observation:
        return Observation(
            emails=[e for e in self.inbox.values() if e.status == EmailStatus.INBOX],
            last_action_result=self.last_action_result,
            step_count=self.step_count
        )

    async def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        self.step_count += 1
        reward_val = 0.0
        explanation = ""

        if action.email_id not in self.inbox:
            self.last_action_result = f"Invalid Email ID: {action.email_id}"
            return self._get_observation(), Reward(value=-0.1, explanation="Invalid email targeted."), False, {}

        email = self.inbox[action.email_id]

        if action.action_type == ActionType.ARCHIVE:
            email.status = EmailStatus.ARCHIVED
            self.last_action_result = f"Archived email: {email.subject}"
            if email.category in ["promotions", "social"]:
                reward_val = 0.2
            elif email.is_urgent:
                reward_val = -0.5
            else:
                reward_val = 0.1

        elif action.action_type == ActionType.DELETE:
            email.status = EmailStatus.DELETED
            self.last_action_result = f"Deleted email: {email.subject}"
            if email.category == "spam":
                reward_val = 0.3
            else:
                reward_val = -0.8

        elif action.action_type == ActionType.REPLY:
            if not action.reply_text:
                self.last_action_result = "Reply text missing."
                reward_val = -0.2
            else:
                self.last_action_result = f"Replied to: {email.subject}"
                if email.is_urgent:
                    reward_val = 0.6
                else:
                    reward_val = 0.2

        elif action.action_type == ActionType.MARK_READ:
            self.last_action_result = f"Marked as read: {email.subject}"
            reward_val = 0.05

        inbox_count = sum(1 for e in self.inbox.values() if e.status == EmailStatus.INBOX)
        if inbox_count == 0 or self.step_count >= 10:
            self.done = True

        return self._get_observation(), Reward(value=reward_val, explanation=explanation), self.done, self.info

    async def state(self) -> State:
        return State(inbox=self.inbox, done=self.done, info=self.info)

    async def close(self):
        pass

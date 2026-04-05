from typing import List, Dict, Any, Tuple
from models import Email, EmailStatus, EmailStatus as ES, Action, ActionType, ActionType as AT
import uuid

def create_task_1() -> List[Email]:
    """Archive all newsletters (Easy)"""
    return [
        Email(id="1", sender="news@techcrunch.com", subject="Daily Tech Update", body="Here is your daily dose of tech news...", category="promotions"),
        Email(id="2", sender="updates@github.com", subject="Weekly Digest", body="Summary of your repository activity...", category="social"),
        Email(id="3", sender="hr@company.com", subject="Important: Payroll Update", body="Please review the new payroll schedule.", category="primary", is_urgent=True),
        Email(id="4", sender="news@nyt.com", subject="Breaking News", body="Top stories of the hour...", category="promotions"),
    ]

def create_task_2() -> List[Email]:
    """Urgent Reply (Medium)"""
    return [
        Email(id="1", sender="boss@company.com", subject="URGENT: Project Deadline", body="Can we meet at 3 PM to discuss the project?", category="primary", is_urgent=True),
        Email(id="2", sender="noreply@bank.com", subject="Monthly Statement", body="Your monthly bank statement is ready for download.", category="primary"),
        Email(id="3", sender="marketing@brand.com", subject="Special Offer inside!", body="Get 50% off on your next purchase.", category="promotions"),
    ]

def create_task_3() -> List[Email]:
    """Inbox Management (Hard)"""
    return [
        Email(id="1", sender="spammer@bot.com", subject="You Won a Prize!", body="Click here to claim your reward...", category="spam"),
        Email(id="2", sender="colleague@company.com", subject="Quick Question", body="Do you have a minute to chat about the report?", category="primary"),
        Email(id="3", sender="social@linkedin.com", subject="New Connection Request", body="John Doe wants to connect with you.", category="social"),
        Email(id="4", sender="news@substack.com", subject="Latest Post", body="Read the latest post from your favorite author...", category="promotions"),
        Email(id="5", sender="urgent@service.com", subject="CRITICAL: Server Down", body="The production server is experiencing downtime.", category="primary", is_urgent=True),
    ]

TAS_GENERATORS = {
    "archive_newsletters": create_task_1,
    "reply_urgent": create_task_2,
    "inbox_clean": create_task_3
}

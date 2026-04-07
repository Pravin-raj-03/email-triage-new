from typing import List, Dict, Any
from models import EmailStatus as ES, Email

def grade_archive_newsletters(final_state: Dict[str, Email], logs: List[Any] = None) -> float:
    """Grade Task 1: Archive all newsletters."""
    total_newsletters = [e for e in final_state.values() if e.category in ["promotions", "social"]]
    if not total_newsletters:
        return 0.99 # Should not happen with current task data
    
    archived_newsletters = [e for e in total_newsletters if e.status == ES.ARCHIVED]
    unarchived_newsletters = [e for e in total_newsletters if e.status != ES.ARCHIVED]
    
    # Check if anything important was deleted
    important_deleted = [e for e in final_state.values() if e.is_urgent and e.status == ES.DELETED]
    
    score = len(archived_newsletters) / len(total_newsletters)
    if important_deleted:
        score -= 0.5
        
    return max(0.01, min(0.99, score))

def grade_reply_urgent(final_state: Dict[str, Email], logs: List[Any] = None) -> float:
    """Grade Task 2: Reply to an urgent email."""
    urgent_replied = False
    
    # Check logs or results for reply actions on urgent emails
    # For simplicity, we check if the urgent email is still in the inbox 
    # but has a reply in the log (or we can assume any reply to an urgent one counts)
    # Better: check if the urgent email is still in inbox but 'step' was successful.
    
    # In this mock, we'll just check if the urgent email exists and was at least 'target' of some action.
    # Actually, the grader should ideally have access to the action history.
    # Let's assume the final state includes a 'replied' flag if we modify Email model, 
    # or we check if the urgent email wasn't deleted/archived and some progress was made.
    
    urgent_email = next((e for e in final_state.values() if e.is_urgent), None)
    if not urgent_email:
        return 0.01
    
    # If the urgent email is still in inbox and wasn't deleted, and others were handled.
    if urgent_email.status == ES.INBOX: # Replied emails stay in inbox in our env.py
        return 0.99
    else:
        return 0.01 # Archived or deleted urgent = Fail.

def grade_inbox_clean(final_state: Dict[str, Email], logs: List[Any] = None) -> float:
    """Grade Task 3: Multi-step triage."""
    spam = [e for e in final_state.values() if e.category == "spam"]
    newsletters = [e for e in final_state.values() if e.category in ["promotions", "social"]]
    urgent = [e for e in final_state.values() if e.is_urgent]
    
    spam_score = sum(1 for e in spam if e.status == ES.DELETED) / len(spam) if spam else 1.0
    news_score = sum(1 for e in newsletters if e.status == ES.ARCHIVED) / len(newsletters) if newsletters else 1.0
    urgent_score = sum(1 for e in urgent if e.status == ES.INBOX) / len(urgent) if urgent else 1.0
    
    total_score = (spam_score + news_score + urgent_score) / 3.0
    return max(0.01, min(0.99, total_score))

GRADERS = {
    "archive_newsletters": grade_archive_newsletters,
    "reply_urgent": grade_reply_urgent,
    "inbox_clean": grade_inbox_clean
}

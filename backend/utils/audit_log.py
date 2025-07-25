# Simple audit logging utility
import datetime

def log_event(user_id, action, resource_id):
    timestamp = datetime.datetime.utcnow().isoformat()
    print(f"AUDIT LOG: {timestamp} | User: {user_id} | Action: {action} | Resource: {resource_id}")
    # In production, store in DB or send to logging service

import os
import json
from datetime import datetime

def load_data(file_path, default):
    """Load data from JSON file with error handling"""
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {file_path}: {e}")
            return default
    return default

def save_data(file_path, data):
    """Save data to JSON file with error handling"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving {file_path}: {e}")

def send_task_notification(title, desc, app_context=None):
    """Send task notification (console output for now)"""
    if title:
        notification_text = f"Lembrete: {title}"
        if desc:
            notification_text += f" | {desc}"
        else:
            notification_text += " | Hora de começar!"
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {notification_text}")
        return notification_text
    return None

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_task_time(time_str):
    """Format task time for display"""
    if not time_str:
        return ""
    try:
        # Parse and reformat time
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except ValueError:
        return time_str

def get_task_priority(task):
    """Determine task priority based on due time and completion status"""
    if task.get("completed", False):
        return 3  # Lowest priority for completed tasks
    
    due_time = task.get("due_date", "")
    if not due_time:
        return 2  # Medium priority for tasks without time
    
    try:
        now = datetime.now()
        task_time = datetime.strptime(due_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        
        # High priority if task is due within next hour
        if 0 <= (task_time - now).total_seconds() <= 3600:
            return 0
        # Medium priority for future tasks
        elif task_time > now:
            return 1
        # Low priority for overdue tasks
        else:
            return 2
    except ValueError:
        return 2

def clean_old_sessions():
    """Clean up old session files (can be called periodically)"""
    session_file = "session.json"
    if os.path.exists(session_file):
        try:
            with open(session_file, "r") as f:
                session_data = json.load(f)
            
            # Add timestamp checking logic here if needed
            # For now, just validate the structure
            if not isinstance(session_data, dict):
                os.remove(session_file)
                
        except (json.JSONDecodeError, IOError):
            # Remove corrupted session file
            os.remove(session_file)

def export_user_tasks(user_data, format_type="json"):
    """Export user tasks to different formats"""
    if format_type == "json":
        return json.dumps(user_data.get("tasks", []), indent=2, ensure_ascii=False)
    elif format_type == "text":
        tasks = user_data.get("tasks", [])
        output = f"Tasks for {user_data.get('username', 'User')}:\n\n"
        for i, task in enumerate(tasks, 1):
            output += f"{i}. {task.get('title', 'Untitled')}\n"
            if task.get('description'):
                output += f"   Description: {task.get('description')}\n"
            if task.get('due_date'):
                output += f"   Due: {task.get('due_date')}\n"
            output += f"   Status: {'✓ Completed' if task.get('completed') else '○ Pending'}\n"
            output += f"   Type: {task.get('type', 'single').title()}\n\n"
        return output
    return str(user_data.get("tasks", []))

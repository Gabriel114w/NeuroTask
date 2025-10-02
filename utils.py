import os
from datetime import datetime
from supabase import create_client

# 🔗 Conexão global com Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ SUPABASE_URL e SUPABASE_KEY não estão configurados!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =============================
# USUÁRIOS
# =============================

def get_user_by_email(email):
    resp = supabase.table("users").select("*").eq("email", email).execute()
    return resp.data[0] if resp.data else None

def get_user_by_username(username):
    resp = supabase.table("users").select("*").eq("username", username).execute()
    return resp.data[0] if resp.data else None

def create_user(username, email, password):
    resp = supabase.table("users").insert({
        "username": username,
        "email": email,
        "password": password,
        "theme_settings": {}
    }).execute()
    return resp.data[0] if resp.data else None

def update_user(user_id, updates: dict):
    resp = supabase.table("users").update(updates).eq("user_id", user_id).execute()
    return resp.data[0] if resp.data else None


# =============================
# TAREFAS
# =============================

def get_tasks(user_id):
    resp = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    return resp.data if resp.data else []

def add_task(user_id, title, description="", due_date="", task_type="single", completed=False):
    resp = supabase.table("tasks").insert({
        "user_id": user_id,
        "title": title,
        "description": description,
        "due_date": due_date,
        "type": task_type,
        "completed": completed
    }).execute()
    return resp.data[0] if resp.data else None

def update_task(task_id, updates: dict):
    resp = supabase.table("tasks").update(updates).eq("task_id", task_id).execute()
    return resp.data[0] if resp.data else None

def delete_task(task_id):
    supabase.table("tasks").delete().eq("task_id", task_id).execute()


# =============================
# UTILITÁRIOS
# =============================

def send_task_notification(title, desc, app_context=None):
    """Envia notificação de tarefa (simulação console)"""
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
    """Validação simples de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_task_time(time_str):
    """Formata hora para exibição"""
    if not time_str:
        return ""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except ValueError:
        return time_str

def get_task_priority(task):
    """Determina prioridade da tarefa"""
    if task.get("completed", False):
        return 3  # menor prioridade
    
    due_time = task.get("due_date", "")
    if not due_time:
        return 2  # média sem data
    
    try:
        now = datetime.now()
        task_time = datetime.strptime(due_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if 0 <= (task_time - now).total_seconds() <= 3600:
            return 0  # alta prioridade
        elif task_time > now:
            return 1  # futura
        else:
            return 2  # atrasada
    except ValueError:
        return 2

def export_user_tasks(user_id, format_type="json"):
    """Exporta tarefas do usuário direto do BD"""
    import json
    tasks = get_tasks(user_id)
    
    if format_type == "json":
        return json.dumps(tasks, indent=2, ensure_ascii=False)
    elif format_type == "text":
        output = f"Tasks for user {user_id}:\n\n"
        for i, task in enumerate(tasks, 1):
            output += f"{i}. {task.get('title', 'Untitled')}\n"
            if task.get('description'):
                output += f"   Description: {task['description']}\n"
            if task.get('due_date'):
                output += f"   Due: {task['due_date']}\n"
            output += f"   Status: {'✓ Completed' if task.get('completed') else '○ Pending'}\n"
            output += f"   Type: {task.get('type', 'single').title()}\n\n"
        return output
    return str(tasks)

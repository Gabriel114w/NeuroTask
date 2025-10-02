import os
from datetime import datetime
from supabase import create_client

# 🔗 Conexão global com Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def load_data(table_name, filters=None):
    """Carrega dados do Supabase"""
    try:
        query = supabase.table(table_name).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        response = query.execute()
        return response.data or []
    except Exception as e:
        print(f"Erro ao carregar dados da tabela {table_name}: {e}")
        return []


def save_data(table_name, data):
    """Salva dados no Supabase"""
    try:
        response = supabase.table(table_name).insert(data).execute()
        return response.data
    except Exception as e:
        print(f"Erro ao salvar dados na tabela {table_name}: {e}")
        return None


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
    tasks = load_data("tasks", {"user_id": user_id})
    
    if format_type == "json":
        import json
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

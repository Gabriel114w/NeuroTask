import os
from supabase import create_client, Client
from datetime import datetime

# 🔗 Conexão global com Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("As variáveis SUPABASE_URL e SUPABASE_KEY não estão configuradas!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================================
# 🧱 Funções CRUD de usuário
# ==========================================================

def create_user(username, email, password):
    """Cria um novo usuário"""
    data = {"username": username, "email": email, "password": password}
    result = supabase.table("users").insert(data).execute()
    return result.data[0] if result.data else None


def get_user_by_email(email):
    """Retorna o usuário pelo email (ou None)"""
    result = supabase.table("users").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None


def get_user_by_username(username):
    """Retorna o usuário pelo nome de usuário (ou None)"""
    result = supabase.table("users").select("*").eq("username", username).execute()
    return result.data[0] if result.data else None


def update_user(email, updates):
    """Atualiza informações do usuário"""
    result = supabase.table("users").update(updates).eq("email", email).execute()
    return result.data[0] if result.data else None


def delete_user(email):
    """Deleta um usuário"""
    result = supabase.table("users").delete().eq("email", email).execute()
    return result.data


# ==========================================================
# 🧩 Funções CRUD de tarefas
# ==========================================================

def get_tasks(user_id):
    """Retorna todas as tarefas de um usuário"""
    result = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    return result.data or []


def add_task(user_id, title, description="", due_date="", type="single"):
    """Adiciona uma nova tarefa"""
    data = {
        "user_id": user_id,
        "title": title,
        "description": description,
        "due_date": due_date,
        "type": type,
        "completed": False
    }
    result = supabase.table("tasks").insert(data).execute()
    return result.data[0] if result.data else None


def update_task(task_id, updates):
    """Atualiza uma tarefa existente"""
    result = supabase.table("tasks").update(updates).eq("id", task_id).execute()
    return result.data[0] if result.data else None


def delete_task(task_id):
    """Deleta uma tarefa"""
    result = supabase.table("tasks").delete().eq("id", task_id).execute()
    return result.data


# ==========================================================
# 🔔 Notificações (placeholder)
# ==========================================================

def send_task_notification(title, desc, app_context=None):
    """Envia uma notificação simples (placeholder para logs)"""
    if title:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Lembrete: {title} - {desc}")

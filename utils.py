import os
from supabase import create_client
from datetime import datetime

# 🔗 Conexão global com Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("As variáveis SUPABASE_URL e SUPABASE_KEY não estão configuradas!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🧱 Funções CRUD de usuário
def create_user(username, email, password):
    data = {"username": username, "email": email, "password": password}
    return supabase.table("users").insert(data).execute()

def get_user_by_email(email):
    return supabase.table("users").select("*").eq("email", email).execute()

def get_user_by_username(username):
    return supabase.table("users").select("*").eq("username", username).execute()

def update_user(email, updates):
    return supabase.table("users").update(updates).eq("email", email).execute()

def delete_user(email):
    return supabase.table("users").delete().eq("email", email).execute()

# 🧩 Funções CRUD de tarefas
def get_tasks(user_id):
    return supabase.table("tasks").select("*").eq("user_id", user_id).execute()

def add_task(user_id, title, description="", due_date="", type="single"):
    data = {
        "user_id": user_id,
        "title": title,
        "description": description,
        "due_date": due_date,
        "type": type,
        "completed": False
    }
    return supabase.table("tasks").insert(data).execute()

def update_task(task_id, updates):
    return supabase.table("tasks").update(updates).eq("id", task_id).execute()

def delete_task(task_id):
    return supabase.table("tasks").delete().eq("id", task_id).execute()

"""
Arquivo utils.py mock para testes do NeuroTask
"""
import json
import os
from datetime import datetime
import hashlib

# Arquivo de dados simulado
DATA_FILE = "/tmp/neurotask_data.json"

def load_data():
    """Carrega dados do arquivo JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": [], "tasks": []}

def save_data(data):
    """Salva dados no arquivo JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def hash_password(password):
    """Gera hash simples da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verifica senha"""
    return hash_password(password) == hashed

def migrate_password(user_id, email, password, old_hash):
    """Migra senha antiga (mock)"""
    pass

def get_user_by_email(email):
    """Busca usuário por email"""
    data = load_data()
    for user in data["users"]:
        if user["email"] == email:
            return user
    return None

def get_user_by_username(username):
    """Busca usuário por nome de usuário"""
    data = load_data()
    for user in data["users"]:
        if user["username"] == username:
            return user
    return None

def create_user(username, email, password):
    """Cria novo usuário"""
    data = load_data()
    
    user_id = len(data["users"]) + 1
    new_user = {
        "id": user_id,
        "username": username,
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    
    data["users"].append(new_user)
    save_data(data)
    return new_user

def update_user(user_id, updates):
    """Atualiza dados do usuário"""
    data = load_data()
    for user in data["users"]:
        if user["id"] == user_id:
            user.update(updates)
            save_data(data)
            return user
    return None

def delete_user(email):
    """Deleta usuário"""
    data = load_data()
    data["users"] = [u for u in data["users"] if u["email"] != email]
    # Também remove tarefas do usuário
    user = get_user_by_email(email)
    if user:
        data["tasks"] = [t for t in data["tasks"] if t["user_id"] != user["id"]]
    save_data(data)

def get_tasks(user_id):
    """Busca todas as tarefas de um usuário"""
    data = load_data()
    return [t for t in data["tasks"] if t["user_id"] == user_id]

def add_task(user_id, title, description="", due_date="", type="single", priority="low"):
    """Adiciona nova tarefa"""
    data = load_data()
    
    task_id = len(data["tasks"]) + 1
    new_task = {
        "id": task_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "due_date": due_date,
        "type": type,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    
    data["tasks"].append(new_task)
    save_data(data)
    return new_task

def update_task(task_id, updates):
    """Atualiza tarefa"""
    data = load_data()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task.update(updates)
            save_data(data)
            return task
    return None

def delete_task(task_id):
    """Deleta tarefa"""
    data = load_data()
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    save_data(data)

def send_task_notification(user_email, task_title, task_description):
    """Envia notificação (mock)"""
    print(f"Notificação enviada para {user_email}: {task_title}")
    return True

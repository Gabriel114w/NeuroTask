import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import json

# Conectar ao Supabase via secrets
url = st.secrets["https://rnhaghcygghooseuaaen.supabase.com"]
key = st.secrets["fQpaQ_TY9MVjOy-KBWxim91rmL9ZRkebXkKY8V5I7hg"]
supabase: Client = create_client(url, key)

# ----------------- USERS -----------------
def get_users():
    """Retorna lista de todos os usuários"""
    res = supabase.table("users").select("*").execute()
    return res.data if res.data else []

def save_user(user):
    """Atualiza ou cria usuário"""
    users = get_users()
    existing = next((u for u in users if u["email"] == user["email"]), None)
    if existing:
        # Atualiza
        supabase.table("users").update(user).eq("email", user["email"]).execute()
    else:
        # Cria
        supabase.table("users").insert(user).execute()

# ----------------- SESSION -----------------
def get_active_session():
    """Retorna sessão ativa do usuário"""
    res = supabase.table("sessions").select("*").eq("active", True).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    return None

def save_session(email):
    """Cria sessão ativa"""
    # Desativa sessões anteriores
    supabase.table("sessions").update({"active": False}).execute()
    # Cria nova sessão
    supabase.table("sessions").insert({"active_user_email": email, "active": True, "created_at": str(datetime.now())}).execute()

def clear_session():
    """Remove sessão ativa"""
    supabase.table("sessions").update({"active": False}).execute()

# ----------------- TASKS -----------------
def update_user_tasks(email, tasks):
    """Atualiza a lista de tarefas do usuário"""
    supabase.table("users").update({"tasks": tasks}).eq("email", email).execute()

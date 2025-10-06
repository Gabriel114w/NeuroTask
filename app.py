import os
import time
from datetime import datetime
import streamlit as st
from utils import (
    get_user_by_email, get_user_by_username, create_user, update_user,
    get_tasks, add_task, update_task, delete_task
)

# =============================
# Sessão e tema
# =============================
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = "login"
if 'task_to_edit' not in st.session_state:
    st.session_state.task_to_edit = None
if 'show_task_form' not in st.session_state:
    st.session_state.show_task_form = False
if 'theme_settings' not in st.session_state:
    st.session_state.theme_settings = {
        "primary_color": "#FFD6BA",
        "background_color": "#FFFFFF",
        "secondary_color": "#A1C3D1",
        "text_color": "#333333",
        "success_color": "#A8D5BA",
        "warning_color": "#FFE7A0",
        "error_color": "#F4A6A6"
    }

st.set_page_config(page_title="NeuroTask", page_icon="🧠", layout="wide")

# =============================
# Funções auxiliares
# =============================
def carregar_tema_usuario():
    if st.session_state.current_user and st.session_state.current_user.get("theme_settings"):
        st.session_state.theme_settings = st.session_state.current_user["theme_settings"]

def verificar_notificacoes():
    if not st.session_state.current_user:
        return []
    agora = datetime.now()
    hora_atual = agora.strftime("%H:%M")
    notificacoes = []
    tasks = get_tasks(st.session_state.current_user["id"])
    for tarefa in tasks:
        if tarefa.get("due_date") == hora_atual and not tarefa.get("completed", False):
            notificacoes.append({
                "title": tarefa.get("title", "Tarefa"),
                "description": tarefa.get("description", "Hora de começar!")
            })
    return notificacoes

def mostrar_notificacao_popup(notificacao):
    st.markdown(f"""
    <div style="position: fixed; top: 20px; right: 20px; 
    background: {st.session_state.theme_settings['warning_color']};
    color: white; padding: 15px; border-radius: 10px; z-index: 9999;">
        <strong>🔔 {notificacao['title']}</strong><br>
        {notificacao['description']}
    </div>
    """, unsafe_allow_html=True)

def validar_horario(hora):
    try:
        h, m = map(int, hora.split(":"))
        return 0 <= h <= 23 and 0 <= m <= 59
    except:
        return False

# =============================
# Telas
# =============================
def tela_login():
    st.title("NeuroTask 🧠")
    st.subheader("Entre na sua conta")
    with st.form("login_form"):
        identificador = st.text_input("Email ou Nome de Usuário")
        senha = st.text_input("Senha", type="password")
        botao_login = st.form_submit_button("LOGIN")
        if botao_login:
            if not identificador or not senha:
                st.error("Preencha todos os campos")
                return
            user = get_user_by_email(identificador.lower()) or get_user_by_username(identificador)
            if user and user["password"] == senha:
                st.session_state.current_user = user
                carregar_tema_usuario()
                st.session_state.current_screen = "menu"
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    if st.button("Não tem conta? Registre-se"):
        st.session_state.current_screen = "register"
        st.rerun()

def tela_registro():
    st.title("Criar Conta 🧠")
    with st.form("register_form"):
        usuario = st.text_input("Nome de Usuário")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        confirmar_senha = st.text_input("Confirmar Senha", type="password")
        botao_registro = st.form_submit_button("REGISTRAR")
        if botao_registro:
            if not all([usuario, email, senha, confirmar_senha]):
                st.error("Todos os campos são obrigatórios")
                return
            if senha != confirmar_senha:
                st.error("Senhas não coincidem")
                return
            if get_user_by_email(email.lower()):
                st.error("Email já cadastrado")
                return
            if get_user_by_username(usuario):
                st.error("Nome de usuário já em uso")
                return
            create_user(usuario, email.lower(), senha)
            st.success("Registro bem-sucedido! Faça login.")
            st.session_state.current_screen = "login"
            st.rerun()
    if st.button("Já tem conta? Faça login"):
        st.session_state.current_screen = "login"
        st.rerun()

# =============================
# Menu Lateral
# =============================
def menu_lateral():
    st.sidebar.title(f"Olá, {st.session_state.current_user['username']}! 👋")
    escolha = st.sidebar.radio("Menu", ["📋 Tarefas", "⚙️ Configurações", "👤 Perfil"])
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.current_user = None
        st.session_state.current_screen = "login"
        st.rerun()
    return escolha

# =============================
# Tarefas
# =============================
def tela_tarefas():
    if st.session_state.show_task_form:
        mostrar_dialogo_tarefa()
    else:
        st.title("📋 Minhas Tarefas")
        tasks = get_tasks(st.session_state.current_user["id"])
        if not tasks:
            st.info("Nenhuma tarefa encontrada. Adicione sua primeira!")
            return
        for tarefa in sorted(tasks, key=lambda t: t.get("due_date", "99:99")):
            col1, col2, col3, col4 = st.columns([0.5,3,1,0.5])
            with col1:
                concluida = st.checkbox("✔", value=tarefa.get("completed", False), key=f"c_{tarefa['id']}")
                if concluida != tarefa.get("completed", False):
                    update_task(tarefa["id"], {"completed": concluida})
                    st.rerun()
            with col2:
                texto = f"**{tarefa['title']}**"
                if tarefa.get('description'):
                    texto += f"\n{tarefa['description']}"
                if tarefa.get('due_date'):
                    texto += f"\n⏰ {tarefa['due_date']}"
                st.markdown(texto)
            with col3:
                if st.button("✏️", key=f"edit_{tarefa['id']}"):
                    st.session_state.task_to_edit = tarefa
                    st.session_state.show_task_form = True

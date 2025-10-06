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
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False
if 'show_profile' not in st.session_state:
    st.session_state.show_profile = False
if 'menu_open' not in st.session_state:
    st.session_state.menu_open = False
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

st.set_page_config(page_title="NeuroTask", page_icon="🧠", layout="centered")

# =============================
# Funções auxiliares
# =============================

def carregar_tema_usuario():
    """Carrega tema salvo do usuário"""
    if st.session_state.current_user and st.session_state.current_user.get("theme_settings"):
        st.session_state.theme_settings = st.session_state.current_user["theme_settings"]

def verificar_notificacoes():
    """Verifica tarefas com horário atual"""
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
    """Mostra notificação popup"""
    st.markdown(f"""
    <div style="position: fixed; top: 20px; right: 20px; 
    background: {st.session_state.theme_settings['warning_color']};
    color: white; padding: 15px; border-radius: 10px; z-index: 9999;">
        <strong>🔔 {notificacao['title']}</strong><br>
        {notificacao['description']}
    </div>
    """, unsafe_allow_html=True)

def validar_horario(hora):
    """Valida formato HH:MM"""
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
                st.session_state.current_screen = "task_list"
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

def mostrar_menu_navegacao():
    col1, col2 = st.columns([3,1])
    with col1:
        st.write(f"Olá, **{st.session_state.current_user.get('username', 'Usuário')}**! 👋")
    with col2:
        if st.button("🚪 Sair"):
            st.session_state.current_user = None
            st.session_state.current_screen = "login"
            st.rerun()

def tela_tarefas():
    mostrar_menu_navegacao()
    st.markdown("---")
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
                st.rerun()
        with col4:
            if st.button("🗑️", key=f"delete_{tarefa['id']}"):
                delete_task(tarefa["id"])
                st.success("Tarefa excluída!")
                st.rerun()

def mostrar_dialogo_tarefa():
    tarefa = st.session_state.task_to_edit or {}
    with st.form("task_form"):
        titulo = st.text_input("Título", value=tarefa.get("title", ""))
        descricao = st.text_area("Descrição", value=tarefa.get("description", ""))
        horario = st.text_input("Horário (HH:MM)", value=tarefa.get("due_date", ""))
        diaria = st.checkbox("Tarefa Diária", value=tarefa.get("type") == "daily")
        salvar = st.form_submit_button("💾 Salvar")
        cancelar = st.form_submit_button("❌ Cancelar")
        if salvar:
            if not titulo.strip():
                st.error("Título obrigatório")
                return
            if horario.strip() and not validar_horario(horario.strip()):
                st.error("Formato inválido. Use HH:MM")
                return
            dados = {
                "title": titulo.strip(),
                "description": descricao.strip(),
                "due_date": horario.strip(),
                "type": "daily" if diaria else "single",
                "completed": tarefa.get("completed", False)
            }
            if tarefa.get("id"):
                update_task(tarefa["id"], dados)
            else:
                add_task(st.session_state.current_user["id"], **dados)
            st.session_state.task_to_edit = None
            st.session_state.show_task_form = False
            st.success("Tarefa salva com sucesso!")
            st.rerun()
        if cancelar:
            st.session_state.task_to_edit = None
            st.session_state.show_task_form = False
            st.rerun()

# =============================
# Main
# =============================

def main():
    if st.session_state.current_user:
        notificacoes = verificar_notificacoes()
        for notif in notificacoes:
            mostrar_notificacao_popup(notif)

    if st.session_state.current_screen == "login":
        tela_login()
    elif st.session_state.current_screen == "register":
        tela_registro()
    elif st.session_state.current_screen == "task_list":
        if st.session_state.current_user:
            if st.session_state.show_task_form:
                mostrar_dialogo_tarefa()
            else:
                tela_tarefas()
        else:
            st.session_state.current_screen = "login"
            st.rerun()

if __name__ == "__main__":
    main()

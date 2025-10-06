import os
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
    <div style="
        position: fixed; top: 20px; right: 10px; width: 90%;
        max-width: 300px;
        background: {st.session_state.theme_settings['warning_color']};
        color: #333; padding: 15px; border-radius: 12px; z-index: 9999;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 14px;
    ">
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
    st.markdown('<h2 style="text-align:center">NeuroTask 🧠</h2>', unsafe_allow_html=True)
    st.markdown('<h4 style="text-align:center; color:#666;">Entre na sua conta</h4>', unsafe_allow_html=True)
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
    st.markdown('<h2 style="text-align:center">Criar Conta 🧠</h2>', unsafe_allow_html=True)
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
# Menu superior (mobile-friendly)
# =============================
def menu_superior():
    st.markdown("""
    <style>
    .menu-container {
        display: flex;
        justify-content: space-around;
        background-color: #FFD6BA;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .menu-button {
        background-color: #A1C3D1;
        color: #333;
        padding: 8px 15px;
        border-radius: 10px;
        margin: 3px;
        text-align: center;
        display: inline-block;
        width: 100px;
        font-weight: bold;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    cols = st.columns([1,1,1])
    escolha = st.radio("", ["📋 Tarefas", "⚙️ Configurações", "👤 Perfil"], horizontal=True)
    if st.button("🚪 Sair"):
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
        st.markdown('<h3 style="text-align:center">📋 Minhas Tarefas</h3>', unsafe_allow_html=True)
        tasks = get_tasks(st.session_state.current_user["id"])
        if not tasks:
            st.info("Nenhuma tarefa encontrada. Adicione sua primeira!")
            return
        for tarefa in sorted(tasks, key=lambda t: t.get("due_date", "99:99")):
            st.markdown(f"""
            <div style="
                background-color: {st.session_state.theme_settings['primary_color']};
                padding: 15px; border-radius: 20px;
                margin-bottom: 15px;
                box-shadow: 0 6px 10px rgba(0,0,0,0.12);
                color: {st.session_state.theme_settings['text_color']};
                font-size: 16px;
            ">
                <strong>{tarefa['title']}</strong><br>
                {tarefa.get('description','')}<br>
                ⏰ {tarefa.get('due_date','')}
            </div>
            """, unsafe_allow_html=True)
        if st.button("➕ Adicionar Tarefa"):
            st.session_state.show_task_form = True
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
# Configurações e Perfil
# =============================
def tela_configuracoes():
    st.markdown('<h3>⚙️ Configurações</h3>', unsafe_allow_html=True)
    st.info("Aqui você poderá futuramente alterar tema, notificações e preferências.")

def tela_perfil():
    st.markdown('<h3>👤 Perfil</h3>', unsafe_allow_html=True)
    st.write(f"**Nome de Usuário:** {st.session_state.current_user['username']}")
    st.write(f"**Email:** {st.session_state.current_user['email']}")

# =============================
# Main
# =============================
def main():
    if st.session_state.current_user:
        carregar_tema_usuario()
        notificacoes = verificar_notificacoes()
        for notif in notificacoes:
            mostrar_notificacao_popup(notif)

    if st.session_state.current_screen == "login":
        tela_login()
    elif st.session_state.current_screen == "register":
        tela_registro()
    elif st.session_state.current_screen == "menu":
        escolha = menu_superior()
        if escolha == "📋 Tarefas":
            tela_tarefas()
        elif escolha == "⚙️ Configurações":
            tela_configuracoes()
        elif escolha == "👤 Perfil":
            tela_perfil()

if __name__ == "__main__":
    main()

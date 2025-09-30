import streamlit as st
from datetime import datetime
from supabase_client import supabase
from utils import validar_horario, aplicar_css, verificar_notificacoes

# ----------------------
# Inicializar estado
# ----------------------
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
if 'last_check_date' not in st.session_state:
    st.session_state.last_check_date = datetime.now().date()
if 'theme_settings' not in st.session_state:
    st.session_state.theme_settings = {
        "primary_color": "#FFD6BA",
        "background_color": "#FFFFFF", 
        "secondary_color": "#A1C3D1",
        "text_color": "#FFFFFF",
        "success_color": "#A8D5BA",
        "warning_color": "#FFE7A0",
        "error_color": "#F4A6A6"
    }

# ----------------------
# CSS
# ----------------------
aplicar_css(st.session_state.theme_settings)

# ----------------------
# Funções Supabase
# ----------------------
def get_users(): return supabase.table("users").select("*").execute().data or []
def create_user(user): supabase.table("users").insert(user).execute()
def update_user(email, data): supabase.table("users").update(data).eq("email", email).execute()
def delete_user(email): supabase.table("users").delete().eq("email", email).execute()

def get_tasks(email): return supabase.table("tasks").select("*").eq("user_email", email).execute().data or []
def create_task(task): supabase.table("tasks").insert(task).execute()
def update_task(task_id, data): supabase.table("tasks").update(data).eq("id", task_id).execute()
def delete_task(task_id): supabase.table("tasks").delete().eq("id", task_id).execute()

# ----------------------
# Login / Registro
# ----------------------
def tela_login():
    st.title("NeuroTask 🧠")
    st.subheader("Entre na sua conta")
    with st.form("login_form"):
        identificador = st.text_input("Email ou Nome de Usuário")
        senha = st.text_input("Senha", type="password")
        botao = st.form_submit_button("LOGIN")
        if botao:
            usuarios = get_users()
            usuario = next((u for u in usuarios if (u["username"].lower()==identificador.lower() or u["email"].lower()==identificador.lower()) and u["password"]==senha), None)
            if usuario:
                st.session_state.current_user = usuario
                st.session_state.current_screen = "task_list"
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    if st.button("Não tem conta? Registre-se"):
        st.session_state.current_screen = "register"
        st.rerun()

def tela_registro():
    st.title("NeuroTask 🧠")
    st.subheader("Criar Conta")
    with st.form("register_form"):
        usuario = st.text_input("Nome de Usuário")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        confirmar = st.text_input("Confirmar Senha", type="password")
        botao = st.form_submit_button("REGISTRAR")
        if botao:
            if not all([usuario,email,senha,confirmar]):
                st.error("Todos os campos obrigatórios")
                return
            if senha != confirmar:
                st.error("Senhas não coincidem")
                return
            if any(u["email"].lower()==email.lower() for u in get_users()):
                st.error("Email já cadastrado")
                return
            if any(u["username"].lower()==usuario.lower() for u in get_users()):
                st.error("Nome de usuário já em uso")
                return
            novo_usuario = {"username":usuario,"email":email.lower(),"password":senha,"theme_settings":{}}
            create_user(novo_usuario)
            st.success("Registro concluído! Faça login.")
            st.session_state.current_screen = "login"
            st.rerun()

# ----------------------
# Tarefas
# ----------------------
def tela_tarefas():
    st.title("📋 Minhas Tarefas")
    mostrar_menu()
    tarefas = get_tasks(st.session_state.current_user["email"])
    if not tarefas:
        st.info("Nenhuma tarefa encontrada. Adicione sua primeira!")
        return
    for t in tarefas:
        col1, col2, col3, col4 = st.columns([0.5,3,1,0.5])
        with col1:
            concluida = st.checkbox("", value=t.get("completed",False), key=f"task_{t['id']}")
            if concluida != t.get("completed",False):
                t["completed"]=concluida
                update_task(t["id"],t)
                st.rerun()
        with col2:
            classe="task-completed" if t.get("completed") else "task-pending"
            texto=f"**{t['title']}**\n{t.get('description','')}\n{t.get('due_date','')}"
            st.markdown(f'<div class="task-item {classe}">{texto}</div>',unsafe_allow_html=True)
        with col3:
            if st.button("✏️",key=f"edit_{t['id']}"):
                st.session_state.task_to_edit=t
                st.session_state.show_task_form=True
                st.rerun()
        with col4:
            if st.button("🗑️",key=f"delete_{t['id']}"):
                delete_task(t["id"])
                st.success("Tarefa excluída!")
                st.rerun()

# ----------------------
# Menu
# ----------------------
def mostrar_menu():
    col1,col2,col3,col4=st.columns([2,1,1,1])
    with col1: st.write(f"Olá, **{st.session_state.current_user['username']}**! 👋")
    with col3:
        if st.button("👤 Perfil"):
            st.session_state.show_profile=True
            st.rerun()
    with col4:
        if st.button("≡ Menu"):
            st.session_state.menu_open=not st.session_state.menu_open
            st.rerun()
    if st.session_state.menu_open:
        if st.button("➕ Nova Tarefa"):
            st.session_state.show_task_form=True
            st.rerun()
        if st.button("⚙️ Configurações"):
            st.session_state.show_settings=True
            st.rerun()
        if st.button("🚪 Sair"):
            st.session_state.current_user=None
            st.session_state.current_screen="login"
            st.rerun()

# ----------------------
# Main
# ----------------------
def main():
    if st.session_state.current_screen=="login":
        tela_login()
    elif st.session_state.current_screen=="register":
        tela_registro()
    elif st.session_state.current_screen=="task_list":
        if st.session_state.show_profile:
            st.write("🧑 Perfil do usuário (editar futuramente)")
        elif st.session_state.show_settings:
            st.write("⚙️ Configurações (tema, notificações etc)")
        elif st.session_state.show_task_form:
            st.write("➕ Formulário de tarefa (criar/editar)")
        else:
            tela_tarefas()

    # Notificações
    if st.session_state.current_user:
        tarefas = get_tasks(st.session_state.current_user["email"])
        notifs, st.session_state.last_check_date = verificar_notificacoes(tarefas, st.session_state.last_check_date)
        for n in notifs:
            st.markdown(f"""
            <div class="notification-popup">
                <strong>🔔 {n['title']}</strong><br>{n['description']}
            </div>
            """,unsafe_allow_html=True)

if __name__=="__main__":
    main()

import streamlit as st
import threading
import time
import os
from datetime import datetime
from utils import load_data, save_data, send_task_notification

# File paths
USERS_FILE = "users.json"
SESSION_FILE = "session.json"

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = "login"
if 'task_to_edit' not in st.session_state:
    st.session_state.task_to_edit = None
if 'notification_thread_started' not in st.session_state:
    st.session_state.notification_thread_started = False
if 'last_check_date' not in st.session_state:
    st.session_state.last_check_date = datetime.now().date()

# Configure page
st.set_page_config(
    page_title="NeuroTask - ADHD Task Organizer",
    page_icon="🧠",
    layout="centered"
)

# Custom CSS for ADHD-friendly design
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .task-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    .task-completed {
        background-color: #d4edda;
        opacity: 0.7;
    }
    .task-pending {
        background-color: #fff3cd;
    }
    h1 {
        color: #4A90E2;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def task_checker():
    """Background thread to check for task notifications"""
    while True:
        try:
            if st.session_state.current_user and "tasks" in st.session_state.current_user:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                
                for task in st.session_state.current_user["tasks"]:
                    if (task.get("due_date") == current_time and 
                        not task.get("completed", False) and 
                        not task.get("notified_today", False)):
                        
                        # Mark as notified for today
                        task["notified_today"] = True
                        
                        # Update user data
                        users = load_data(USERS_FILE, [])
                        for idx, u in enumerate(users):
                            if u["email"] == st.session_state.current_user["email"]:
                                users[idx] = st.session_state.current_user
                                break
                        save_data(USERS_FILE, users)
                        
                        # Show notification (in console for now, as Streamlit notifications require page interaction)
                        print(f"Task Notification: {task.get('title')} - {task.get('description', 'Time to start!')}")
                
                # Reset notification flags at midnight
                if now.date() != st.session_state.last_check_date:
                    st.session_state.last_check_date = now.date()
                    for task in st.session_state.current_user.get("tasks", []):
                        task.pop("notified_today", None)
                        
        except Exception as e:
            print(f"Task checker error: {e}")
        
        time.sleep(60)  # Check every minute

def check_session():
    """Check for existing session"""
    session = load_data(SESSION_FILE, {})
    email = session.get("active_user_email")
    if email:
        users = load_data(USERS_FILE, [])
        user = next((u for u in users if u["email"] == email), None)
        if user:
            st.session_state.current_user = user
            st.session_state.current_screen = "task_list"
            return True
    return False

def login_screen():
    """Display login screen"""
    st.title("🧠 NeuroTask")
    st.subheader("Login to your account")
    
    with st.form("login_form"):
        identifier = st.text_input("Email or Username", key="login_identifier")
        password = st.text_input("Senha", type="password", key="login_password")
        remember_me = st.checkbox("Lembrar-se de mim", key="remember_me")
        
        login_btn = st.form_submit_button("LOGIN")
        
        if login_btn:
            if not identifier or not password:
                st.error("Preencha todos os campos")
                return
            
            users = load_data(USERS_FILE, [])
            user = next((u for u in users if 
                        (u["username"].lower() == identifier.lower() or 
                         u["email"].lower() == identifier.lower()) and 
                        u["password"] == password), None)
            
            if user:
                st.session_state.current_user = user
                if remember_me:
                    save_data(SESSION_FILE, {"active_user_email": user["email"]})
                st.session_state.current_screen = "task_list"
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    
    if st.button("Não tem uma conta? Registre-se"):
        st.session_state.current_screen = "register"
        st.rerun()

def register_screen():
    """Display registration screen"""
    st.title("🧠 NeuroTask")
    st.subheader("Criar Conta")
    
    with st.form("register_form"):
        username = st.text_input("Nome de Usuário", key="reg_username")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Senha", type="password", key="reg_password")
        confirm_password = st.text_input("Confirmar Senha", type="password", key="reg_confirm")
        
        register_btn = st.form_submit_button("REGISTRAR")
        
        if register_btn:
            if not all([username, email, password, confirm_password]):
                st.error("Todos os campos são obrigatórios")
                return
            
            if password != confirm_password:
                st.error("Senhas não coincidem")
                return
            
            users = load_data(USERS_FILE, [])
            
            if any(u["email"].lower() == email.lower() for u in users):
                st.error("Email já em uso")
                return
            
            if any(u["username"].lower() == username.lower() for u in users):
                st.error("Nome de usuário já em uso")
                return
            
            new_user = {
                "user_id": len(users) + 1,
                "username": username,
                "email": email.lower(),
                "password": password,
                "tasks": []
            }
            
            users.append(new_user)
            save_data(USERS_FILE, users)
            
            st.success("Registro bem-sucedido! Faça login.")
            st.session_state.current_screen = "login"
            st.rerun()
    
    if st.button("Já tem uma conta? Faça login"):
        st.session_state.current_screen = "login"
        st.rerun()

def task_list_screen():
    """Display task list screen"""
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📋 Minhas Tarefas")
    with col2:
        if st.button("Logout"):
            st.session_state.current_user = None
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            st.session_state.current_screen = "login"
            st.rerun()
    
    # Add task button
    if st.button("➕ Adicionar Nova Tarefa"):
        st.session_state.task_to_edit = None
        show_task_dialog()
        return
    
    # Display tasks
    if not st.session_state.current_user or "tasks" not in st.session_state.current_user:
        st.info("Nenhuma tarefa encontrada. Adicione sua primeira tarefa!")
        return
    
    tasks = sorted(st.session_state.current_user["tasks"], 
                  key=lambda t: t.get("due_date", "99:99"))
    
    if not tasks:
        st.info("Nenhuma tarefa encontrada. Adicione sua primeira tarefa!")
        return
    
    for idx, task in enumerate(tasks):
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 3, 1, 0.5])
            
            # Completion checkbox
            with col1:
                completed = st.checkbox("", 
                                      value=task.get("completed", False),
                                      key=f"task_complete_{idx}")
                if completed != task.get("completed", False):
                    task["completed"] = completed
                    save_user_data()
                    st.rerun()
            
            # Task details
            with col2:
                status_class = "task-completed" if task.get("completed") else "task-pending"
                task_text = f"**{task.get('title', '')}**"
                if task.get('description'):
                    task_text += f"\n{task.get('description')}"
                if task.get('due_date'):
                    task_text += f"\n⏰ {task.get('due_date')}"
                if task.get('type') == 'daily':
                    task_text += " 🔄"
                
                st.markdown(f'<div class="task-item {status_class}">{task_text}</div>', 
                           unsafe_allow_html=True)
            
            # Edit button
            with col3:
                if st.button("✏️", key=f"edit_{idx}"):
                    st.session_state.task_to_edit = task
                    show_task_dialog()
                    return
            
            # Delete button
            with col4:
                if st.button("🗑️", key=f"delete_{idx}"):
                    confirm_delete_task(task, idx)
                    return

def show_task_dialog():
    """Show task creation/editing dialog"""
    st.subheader("➕ Adicionar/Editar Tarefa")
    
    # Pre-fill if editing
    task = st.session_state.task_to_edit or {}
    
    with st.form("task_form"):
        title = st.text_input("Título da Tarefa", value=task.get("title", ""))
        description = st.text_area("Descrição (opcional)", value=task.get("description", ""))
        due_time = st.text_input("Horário (HH:MM)", value=task.get("due_date", ""),
                                help="Formato: 14:30 para 2:30 PM")
        is_daily = st.checkbox("Tarefa Diária", value=task.get("type") == "daily")
        
        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Salvar")
        with col2:
            cancel_btn = st.form_submit_button("❌ Cancelar")
        
        if save_btn:
            if not title.strip():
                st.error("Título obrigatório")
                return
            
            # Validate time format
            if due_time and not validate_time_format(due_time):
                st.error("Formato de horário inválido. Use HH:MM (ex: 14:30)")
                return
            
            task_data = {
                "title": title.strip(),
                "description": description.strip(),
                "due_date": due_time.strip(),
                "type": "daily" if is_daily else "single",
                "completed": task.get("completed", False)
            }
            
            if st.session_state.task_to_edit:
                # Update existing task
                for i, t in enumerate(st.session_state.current_user["tasks"]):
                    if t == st.session_state.task_to_edit:
                        st.session_state.current_user["tasks"][i] = task_data
                        break
            else:
                # Add new task
                st.session_state.current_user["tasks"].append(task_data)
            
            save_user_data()
            st.session_state.task_to_edit = None
            st.success("Tarefa salva com sucesso!")
            st.rerun()
        
        if cancel_btn:
            st.session_state.task_to_edit = None
            st.rerun()

def confirm_delete_task(task, idx):
    """Confirm task deletion"""
    st.subheader("⚠️ Confirmar Exclusão")
    st.warning(f"Tem certeza que deseja deletar '{task.get('title')}'?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Sim, Deletar"):
            st.session_state.current_user["tasks"].remove(task)
            save_user_data()
            st.success("Tarefa deletada com sucesso!")
            st.rerun()
    
    with col2:
        if st.button("❌ Cancelar"):
            st.rerun()

def save_user_data():
    """Save current user data to file"""
    users = load_data(USERS_FILE, [])
    for idx, u in enumerate(users):
        if u["email"] == st.session_state.current_user["email"]:
            users[idx] = st.session_state.current_user
            break
    save_data(USERS_FILE, users)

def validate_time_format(time_str):
    """Validate time format HH:MM"""
    try:
        time_parts = time_str.split(":")
        if len(time_parts) != 2:
            return False
        hours, minutes = int(time_parts[0]), int(time_parts[1])
        return 0 <= hours <= 23 and 0 <= minutes <= 59
    except ValueError:
        return False

# Main app logic
def main():
    # Check session on startup
    if st.session_state.current_user is None and st.session_state.current_screen == "login":
        if check_session():
            st.rerun()
    
    # Start notification thread
    if (st.session_state.current_user and 
        not st.session_state.notification_thread_started):
        threading.Thread(target=task_checker, daemon=True).start()
        st.session_state.notification_thread_started = True
    
    # Display appropriate screen
    if st.session_state.current_screen == "login":
        login_screen()
    elif st.session_state.current_screen == "register":
        register_screen()
    elif st.session_state.current_screen == "task_list":
        if st.session_state.current_user:
            if st.session_state.task_to_edit is not None or 'show_task_dialog' in st.session_state:
                show_task_dialog()
            else:
                task_list_screen()
        else:
            st.session_state.current_screen = "login"
            st.rerun()

if __name__ == "__main__":
    main()

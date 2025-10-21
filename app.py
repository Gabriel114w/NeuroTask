import streamlit as st
import time
from datetime import datetime
from utils import (
    get_user_by_email, get_user_by_username, create_user, update_user, delete_user,
    get_tasks, add_task, update_task, delete_task,
    send_task_notification, verify_password, migrate_password, get_pending_tasks
)

# =============================
# Session State Initialization
# =============================
def init_session_state():
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'current_screen' not in st.session_state:
        st.session_state.current_screen = "login"
    if 'task_to_edit' not in st.session_state:
        st.session_state.task_to_edit = None
    if 'show_task_form' not in st.session_state:
        st.session_state.show_task_form = False
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
    if 'current_theme' not in st.session_state:
        st.session_state.current_theme = "light_lavender" 
    if 'layout_mode' not in st.session_state:
        st.session_state.layout_mode = "desktop"
    if 'filter_priority' not in st.session_state:
        st.session_state.filter_priority = "all"
    if 'filter_sort' not in st.session_state:
        st.session_state.filter_sort = "priority"
    if 'filter_type' not in st.session_state:
        st.session_state.filter_type = "all"
    if 'show_tutorial' not in st.session_state:
        st.session_state.show_tutorial = False

        st.session_state.layout_mode = "desktop"
    if 'sidebar_expanded' not in st.session_state:
        st.session_state.sidebar_expanded = True
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = False

# =============================
# Theme Configuration - Cores Suaves e Pastéis
# =============================
THEMES = {
    "light_lavender": {
        "name": "Lavanda Claro (Foco)",
        "primary": "#F3E5F5",
        "secondary": "#E1BEE7",
        "accent": "#D7C4F3",
        "background": "#FAFAFA",
        "surface": "#FFFFFF",
        "text": "#4A148C",
        "text_secondary": "#7B1FA2",
        "success": "#A5D6A7", # Verde Suave (Baixa)

        "warning": "#FFE082", # Amarelo Suave (Média)

        "error": "#EF9A9A", # Vermelho Suave (Alta)

        "border": "#E0E0E0",
        "shadow": "rgba(0, 0, 0, 0.08)",
        "hover": "#F5F5F5"
    },
    "light_mint": {
        "name": "Menta Claro (Calma)",
        "primary": "#E8F5E9",
        "secondary": "#C8E6C9",
        "accent": "#81C784",
        "background": "#FAFAFA",
        "surface": "#FFFFFF",
        "text": "#388E3C",
        "text_secondary": "#66BB6A",
        "success": "#A5D6A7", # Verde Suave (Baixa)

        "warning": "#FFE082", # Amarelo Suave (Média)

        "error": "#EF9A9A", # Vermelho Suave (Alta)

        "border": "#E0E0E0",
        "shadow": "rgba(0, 0, 0, 0.08)",
        "hover": "#F5F5F5"
    },
    "light_peach": {
        "name": "Pêssego Claro (Acolhedor)",
        "primary": "#FFF3E0",
        "secondary": "#FFE0B2",
        "accent": "#FFB74D",
        "background": "#FAFAFA",
        "surface": "#FFFFFF",
        "text": "#E65100",
        "text_secondary": "#FF9800",
        "success": "#C5E1A5",
        "warning": "#FFCC80",
        "error": "#FFAB91",
        "border": "#E0E0E0",
        "shadow": "rgba(0, 0, 0, 0.08)",
        "hover": "#FFF8F0"
    },
    "dark_lavender": {
        "name": "Lavanda Escuro (Foco)",
        "primary": "#311B92",
        "secondary": "#4527A0",
        "accent": "#D7C4F3",
        "background": "#1A1A1A",
        "surface": "#263238",
        "text": "#E1BEE7",
        "text_secondary": "#CE93D8",
        "success": "#81C784",
        "warning": "#FFD54F",
        "error": "#E57373",
        "border": "#37474F",
        "shadow": "rgba(0, 0, 0, 0.3)",
        "hover": "#2C393F"
    },
    "dark_mint": {
        "name": "Menta Escuro (Calma)",
        "primary": "#1B5E20",
        "secondary": "#2E7D32",
        "accent": "#A5D6A7",
        "background": "#1A1A1A",
        "surface": "#263238",
        "text": "#C8E6C9",
        "text_secondary": "#A5D6A7",
        "success": "#81C784",
        "warning": "#FFD54F",
        "error": "#E57373",
        "border": "#37474F",
        "shadow": "rgba(0, 0, 0, 0.3)",
        "hover": "#2C393F"
    },
    "dark_brown": {
        "name": "Marrom Escuro (Acolhedor)",
        "primary": "#3E2723",
        "secondary": "#4E342E",
        "accent": "#FFAB40",
        "background": "#1A1A1A",
        "surface": "#3E2723",
        "text": "#EFEBE9",
        "text_secondary": "#BCAAA4",
        "success": "#AED581",
        "warning": "#FFB74D",
        "error": "#FF8A65",
        "border": "#4E342E",
        "shadow": "rgba(0, 0, 0, 0.3)",
        "hover": "#4A2C24"
    }
}

def apply_theme_css():
    theme = THEMES[st.session_state.current_theme]
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-sizing: border-box;
    }
    
    .main {
        background-color: {theme['background']};
        padding: 0;
    }
    
    .block-container {
        padding: 2rem 1rem;
        max-width: 1400px;
    }
    
    /* Task Cards - Blocos Visuais Dinâmicos */
    .task-card {
        background: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px {theme['shadow']};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .task-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: {theme['accent']};
        transition: width 0.3s ease;
    }
    
    .task-card:hover {
        box-shadow: 0 6px 20px {theme['shadow']};
        transform: translateY(-2px);
        border-color: {theme['accent']};
    }
    
    .task-card:hover::before {
        width: 6px;
    }
    
    .task-completed {
        opacity: 0.65;
        background: {theme['primary']};
    }
    
    .task-completed::before {
        background: {theme['success']} !important;
    }
    
    /* Cores de Prioridade Suaves - Bordas */
    .task-priority-high::before {
        background: {theme['error']} !important; /* Vermelho Suave */
    }
    
    .task-priority-medium::before {
        background: {theme['warning']} !important; /* Amarelo Suave */
    }
    
    .task-priority-low::before {
        background: {theme['success']} !important; /* Verde Suave */
    }
    
    .task-title {
        font-size: 18px;
        font-weight: 600;
        color: {theme['text']};
        margin: 0 0 8px 0;
        line-height: 1.4;
    }
    
    .task-description {
        font-size: 14px;
        color: {theme['text_secondary']};
        margin: 8px 0;
        line-height: 1.6;
    }
    
    .task-meta {
        font-size: 13px;
        color: {theme['text_secondary']};
        margin-top: 12px;
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }
    
    .task-meta-item {
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Priority Badges */
    .priority-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Cores de Prioridade Suaves - Badges */
    .priority-high {
        background: {theme['error']};
        color: {theme['text']}; /* Texto escuro para contraste suave */
    }
    
    .priority-medium {
        background: {theme['warning']};
        color: {theme['text']};
    }
    
    .priority-low {
        background: {theme['success']};
        color: {theme['text']}; /* Texto escuro para contraste suave */
    }
    
    /* Stats Cards */
    .stats-card {
        background: {theme['surface']};
        border: 1px solid {theme['border']};
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px {theme['shadow']};
        transition: all 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 16px {theme['shadow']};
    }
    
    .stats-number {
        font-size: 36px;
        font-weight: 700;
        color: {theme['accent']};
        line-height: 1;
        margin-bottom: 8px;
    }
    
    .stats-label {
        font-size: 12px;
        color: {theme['text_secondary']};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Page Headers */
    .page-header {
        font-size: 32px;
        font-weight: 700;
        color: {theme['text']};
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .page-subtitle {
        font-size: 16px;
        color: {theme['text_secondary']};
        margin-bottom: 32px;
    }
    
    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: {theme['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 32px 0 16px 0;
    }
    
    /* Profile Card */
    .profile-card {
        background: {theme['surface']};
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 2px 8px {theme['shadow']};
        border: 1px solid {theme['border']};
    }
    
    /* Buttons */
    .stButton button {
        background-color: {theme['accent']} !important;
        color: {theme['text']} !important;
        border: 1px solid {theme['accent']} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background-color: {theme['secondary']} !important;
        border-color: {theme['secondary']} !important;
        box-shadow: 0 4px 12px {theme['shadow']};
    }
    
    .stButton button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px {theme['accent']}40 !important;
    }

    .stButton button.delete-button {
        background-color: {theme['error']} !important;
        border-color: {theme['error']} !important;
    }

    .stButton button.delete-button:hover {
        background-color: #D32F2F !important;
        border-color: #D32F2F !important;
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        background-color: {theme['surface']} !important;
        color: {theme['text']} !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: {theme['accent']} !important;
        box-shadow: 0 0 0 2px {theme['accent']}40 !important;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: {theme['surface']};
        border-right: 1px solid {theme['border']};
    }

    .css-1d391kg .st-emotion-cache-16txtl3 span {
        color: {theme['text']};
    }

    /* Mobile Specific */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.5rem;
        }
        .task-card {
            padding: 16px;
            margin: 12px 0;
        }
        .page-header {
            font-size: 26px;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# =============================
# Authentication Screens
# =============================
def show_login_screen():
    st.markdown('<h1 class="page-header" style="text-align: center;">NeuroTask</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle" style="text-align: center;">Organize sua mente, um passo de cada vez.</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown('<p class="section-title">Acessar sua conta</p>', unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Senha", type="password", key="login_password")
            submitted = st.form_submit_button("Entrar", use_container_width=True)

            if submitted:
                user = get_user_by_email(email)
                if user and verify_password(password, user['password']):
                    st.session_state.current_user = user
                    st.session_state.current_screen = "main"
                    st.rerun()
                else:
                    st.error("Email ou senha inválidos. Tente novamente.")
        
        st.markdown("---_", unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #888;">Não tem uma conta?</p>', unsafe_allow_html=True)
        if st.button("Criar Conta", key="go_to_register", use_container_width=True):
            st.session_state.current_screen = "register"
            st.rerun()

def show_register_screen():
    st.markdown('<h1 class="page-header" style="text-align: center;">Crie sua Conta</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle" style="text-align: center;">Comece a organizar suas tarefas hoje mesmo.</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("register_form"):
            st.markdown('<p class="section-title">Informações de Cadastro</p>', unsafe_allow_html=True)
            username = st.text_input("Nome de Usuário", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Senha", type="password", key="register_password")
            confirm_password = st.text_input("Confirmar Senha", type="password", key="register_confirm_password")
            submitted = st.form_submit_button("Registrar", use_container_width=True)

            if submitted:
                if not (username and email and password and confirm_password):
                    st.warning("Por favor, preencha todos os campos.")
                elif password != confirm_password:
                    st.error("As senhas não coincidem.")
                elif get_user_by_email(email) or get_user_by_username(username):
                    st.error("Email ou nome de usuário já cadastrado.")
                else:
                    user = create_user(username, email, password)
                    if user:
                        st.session_state.current_user = user
                        st.session_state.current_screen = "main"
                        st.success("Conta criada com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Ocorreu um erro ao criar a conta.")

        st.markdown("---_", unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #888;">Já tem uma conta?</p>', unsafe_allow_html=True)
        if st.button("Fazer Login", key="go_to_login", use_container_width=True):
            st.session_state.current_screen = "login"
            st.rerun()

# =============================
# Main Application Screens
# =============================
def show_main_screen():
    if st.session_state.show_profile:
        show_profile_screen()
    else:
        show_task_dashboard()

def show_task_dashboard():
    # Cabeçalho e Controles
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<h1 class="page-header">Bem-vindo, {st.session_state.current_user["username"]}!</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">Aqui estão suas tarefas. Mantenha o foco e a produtividade.</p>', unsafe_allow_html=True)
    
    with col2:
        if st.button("➕ Adicionar Tarefa", use_container_width=True, key="add_task_main"):
            st.session_state.task_to_edit = None
            st.session_state.show_task_form = True
            st.rerun()

    # Estatísticas
    tasks = get_tasks(st.session_state.current_user["id"])
    if tasks:
        pending_tasks = [t for t in tasks if not t['completed']]
        completed_tasks = [t for t in tasks if t['completed']]
        high_priority_tasks = [t for t in pending_tasks if t['priority'] == 'high']

        st.markdown('<p class="section-title">Seu Progresso</p>', unsafe_allow_html=True)
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{len(pending_tasks)}</div><div class="stats-label">Pendentes</div></div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{len(completed_tasks)}</div><div class="stats-label">Concluídas</div></div>', unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{len(high_priority_tasks)}</div><div class="stats-label">Prioridade Alta</div></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="section-title">Suas Tarefas</p>', unsafe_allow_html=True)

    # Filtros e Ordenação
    filter_cols = st.columns(3)
    with filter_cols[0]:
        st.session_state.filter_priority = st.selectbox(
            "Filtrar por Prioridade",
            options=['all', 'low', 'medium', 'high'],
            format_func=lambda x: {"all": "Todas", "low": "Baixa", "medium": "Média", "high": "Alta"}[x],
            key="filter_priority_select"
        )
    with filter_cols[1]:
        st.session_state.filter_sort = st.selectbox(
            "Ordenar por",
            options=['priority', 'due_date', 'created_at'],
            format_func=lambda x: {"priority": "Prioridade", "due_date": "Data de Entrega", "created_at": "Data de Criação"}[x],
            key="filter_sort_select"
        )
    with filter_cols[2]:
        st.session_state.filter_type = st.selectbox(
            "Filtrar por Tipo",
            options=['all', 'single', 'daily'],
            format_func=lambda x: {"all": "Todos", "single": "Única", "daily": "Diária"}[x],
            key="filter_type_select"
        )

    # Exibição de Tarefas
    if tasks:
        # Aplica filtros
        filtered_tasks = tasks
        if st.session_state.filter_priority != 'all':
            filtered_tasks = [t for t in filtered_tasks if t['priority'] == st.session_state.filter_priority]
        if st.session_state.filter_type != 'all':
            filtered_tasks = [t for t in filtered_tasks if t['type'] == st.session_state.filter_type]

        # Aplica ordenação
        priority_map = {'high': 1, 'medium': 2, 'low': 3}
        if st.session_state.filter_sort == 'priority':
            filtered_tasks.sort(key=lambda t: (t['completed'], priority_map.get(t['priority'], 4)))
        elif st.session_state.filter_sort == 'due_date':
            filtered_tasks.sort(key=lambda t: (t['completed'], t.get('due_date') or '9999-12-31'))
        elif st.session_state.filter_sort == 'created_at':
            filtered_tasks.sort(key=lambda t: (t['completed'], t['created_at']), reverse=True)

        # Separa em pendentes e concluídas
        pending_tasks = [t for t in filtered_tasks if not t['completed']]
        completed_tasks = [t for t in filtered_tasks if t['completed']]

        if not pending_tasks and not completed_tasks:
            st.info("Nenhuma tarefa encontrada com os filtros selecionados.")

        if pending_tasks:
            st.markdown("### 🎯 Pendentes")
            for tarefa in pending_tasks:
                display_task(tarefa)

        if completed_tasks:
            st.markdown("### ✅ Concluídas")
            for tarefa in completed_tasks:
                display_task(tarefa)
    else:
        st.info("Você ainda não tem tarefas. Adicione uma para começar!")

    # Formulário de Tarefa (Modal)
    if st.session_state.show_task_form:
        task_form()

def display_task(tarefa):
    priority_class = f"task-priority-{tarefa.get('priority', 'medium')}"
    completed_class = "task-completed" if tarefa['completed'] else ""
    
    with st.container():
        st.markdown(f'<div class="task-card {priority_class} {completed_class}">', unsafe_allow_html=True)
        
        # Conteúdo do Card
        col1, col2 = st.columns([0.08, 0.92])
        with col1:
            concluida = st.checkbox("", value=tarefa['completed'], key=f"chk_{tarefa['id']}", label_visibility="collapsed")
            if concluida != tarefa['completed']:
                update_task(tarefa["id"], {"completed": concluida})
                st.rerun()

        with col2:
            st.markdown(f'<div class="task-title">{tarefa["title"]}</div>', unsafe_allow_html=True)
            if tarefa.get("description"):
                st.markdown(f'<div class="task-description">{tarefa["description"]}</div>', unsafe_allow_html=True)

            # Meta-informações
            meta_html = '<div class="task-meta">'
            # Badge de Prioridade
            priority_display = tarefa.get('priority', 'medium')
            meta_html += f'<div class="task-meta-item"><span class="priority-badge priority-{priority_display}">{priority_display.capitalize()}</span></div>'
            
            # Data de Entrega
            if tarefa.get("due_date"):
                 meta_html += f'<div class="task-meta-item">🗓️ {tarefa["due_date"]}</div>'
            
            # Tipo de Tarefa
            task_type = tarefa.get('type', 'single')
            meta_html += f'<div class="task-meta-item">🔄 {task_type.capitalize()}</div>'
            meta_html += '</div>'
            st.markdown(meta_html, unsafe_allow_html=True)

        # Botões de Ação
        action_cols = st.columns(8)
        with action_cols[6]:
            if st.button("✏️", key=f"edit_{tarefa['id']}", use_container_width=True):
                st.session_state.task_to_edit = tarefa
                st.session_state.show_task_form = True
                st.rerun()
        with action_cols[7]:
            if st.button("🗑️", key=f"delete_{tarefa['id']}", use_container_width=True):
                delete_task(tarefa['id'])
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def task_form():
    is_edit = st.session_state.task_to_edit is not None
    task_data = st.session_state.task_to_edit if is_edit else {}
    
    st.markdown(f'<div class="page-header">{"Editar Tarefa" if is_edit else "Nova Tarefa"}</div>', unsafe_allow_html=True)
    
    with st.form("task_form_main", clear_on_submit=True):
        title = st.text_input("Título da Tarefa", value=task_data.get("title", ""), placeholder="O que precisa ser feito?")
        description = st.text_area("Descrição (Opcional)", value=task_data.get("description", ""), placeholder="Detalhes, sub-tarefas, notas...")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Data
            due_date_full = task_data.get("due_date")
            initial_date = None
            initial_time = None
            
            if due_date_full:
                try:
                    # Tenta parsear como datetime (com hora)
                    dt_obj = datetime.strptime(due_date_full, "%Y-%m-%d %H:%M")
                    initial_date = dt_obj.date()
                    initial_time = dt_obj.time()
                except ValueError:
                    try:
                        # Tenta parsear como date (sem hora)
                        initial_date = datetime.strptime(due_date_full, "%Y-%m-%d").date()
                    except ValueError:
                        pass
            
            due_date = st.date_input("Data Limite (Opcional)", value=initial_date)
            
        with col2:
            # Hora (Opcional)
            due_time = st.time_input("Hora (Opcional)", value=initial_time)
            
        with col3:
            priority_options = ["low", "medium", "high"]
            priority_labels = {"low": "Baixa", "medium": "Média", "high": "Alta"}
            current_priority = task_data.get("priority", "medium")
            try:
                default_priority_index = priority_options.index(current_priority)
            except ValueError:
                default_priority_index = priority_options.index("medium") # Fallback para 'medium' se o valor for inválido
            
            priority = st.selectbox(
                "Prioridade",
                options=priority_options,
                format_func=lambda x: priority_labels.get(x, x.capitalize()),
                index=default_priority_index,
                key="task_priority_select"
            )
            
        with col4:
            task_type = st.selectbox(
                "Tipo",
                options=["single", "daily"],
                format_func=lambda x: "Única" if x == "single" else "Diária",
                index=["single", "daily"].index(task_data.get("type", "single"))
            )
        
        submit_button = st.form_submit_button("Salvar Tarefa" if is_edit else "Adicionar Tarefa", use_container_width=True)
        
        if submit_button:
            if not title:
                st.error("O título da tarefa é obrigatório.")
                return
            due_date_str_final = ""
            if due_date:
                due_date_str_final = due_date.strftime("%Y-%m-%d")
                if due_time:
                    due_date_str_final += due_time.strftime(" %H:%M")
                    
            updates = {
                "title": title,
                "description": description,
                "due_date": due_date_str_final,
                "type": task_type,
                "priority": priority
            }
            
            if is_edit:
                update_task(task_data["id"], updates)
                st.success("Tarefa atualizada com sucesso!")
            else:
                add_task(st.session_state.current_user["id"], **updates)
                st.success("Tarefa adicionada com sucesso!")
            
            st.session_state.show_task_form = False
            st.session_state.task_to_edit = None
            st.rerun()
            
    if st.button("Cancelar", key="cancel_task_form_outside", use_container_width=True):
        st.session_state.show_task_form = False
        st.session_state.task_to_edit = None
        st.rerun()

from tutorial import mostrar_tutorial # Importa a função do tutorial

def filter_and_sort_tasks(tasks):
    """Aplica filtros e ordenação nas tarefas."""
    
    # 1. Filtragem
    filtered_tasks = tasks
    if st.session_state.filter_priority != 'all':
        filtered_tasks = [t for t in filtered_tasks if t['priority'] == st.session_state.filter_priority]
    if st.session_state.filter_type != 'all':
        filtered_tasks = [t for t in filtered_tasks if t['type'] == st.session_state.filter_type]

    # 2. Ordenação
    if st.session_state.filter_sort == 'priority':
        # Mapeia prioridades para valores numéricos para ordenação
        priority_map = {'high': 1, 'medium': 2, 'low': 3}
        filtered_tasks.sort(key=lambda t: (t['completed'], priority_map.get(t.get('priority', 'medium'), 4)))
    elif st.session_state.filter_sort == 'due_date':
        # Ordena por data de entrega, colocando tarefas sem data no final
        filtered_tasks.sort(key=lambda t: (t['completed'], t.get('due_date') or '9999-12-31'))
    elif st.session_state.filter_sort == 'created_at':
        # Ordena por data de criação (mais recentes primeiro)
        filtered_tasks.sort(key=lambda t: (t['completed'], t['created_at']), reverse=True)
        
    return filtered_tasks

def show_task_list():
    # Filtros e Ordenação
    filter_cols = st.columns(3)
    with filter_cols[0]:
        st.session_state.filter_priority = st.selectbox(
            "Filtrar por Prioridade",
            options=['all', 'low', 'medium', 'high'],
            format_func=lambda x: {"all": "Todas", "low": "Baixa", "medium": "Média", "high": "Alta"}[x],
            key="filter_priority_select_list"
        )
    with filter_cols[1]:
        st.session_state.filter_sort = st.selectbox(
            "Ordenar por",
            options=['priority', 'due_date', 'created_at'],
            format_func=lambda x: {"priority": "Prioridade", "due_date": "Data de Entrega", "created_at": "Data de Criação"}[x],
            key="filter_sort_select_list"
        )
    with filter_cols[2]:
        st.session_state.filter_type = st.selectbox(
            "Filtrar por Tipo",
            options=['all', 'single', 'daily'],
            format_func=lambda x: {"all": "Todos", "single": "Única", "daily": "Diária"}[x],
            key="filter_type_select_list"
        )

    tasks = get_tasks(st.session_state.current_user["id"])
    filtered_and_sorted_tasks = filter_and_sort_tasks(tasks)

    if not filtered_and_sorted_tasks:
        st.info("Nenhuma tarefa encontrada com os filtros selecionados.")
        return

    # Separa em pendentes e concluídas
    pending_tasks = [t for t in filtered_and_sorted_tasks if not t['completed']]
    completed_tasks = [t for t in filtered_and_sorted_tasks if t['completed']]

    if pending_tasks:
        st.markdown("### 🎯 Pendentes")
        for tarefa in pending_tasks:
            display_task(tarefa)

    if completed_tasks:
        st.markdown("### ✅ Concluídas")
        for tarefa in completed_tasks:
            display_task(tarefa)

def show_profile_screen():
    st.markdown('<h1 class="page-header">Meu Perfil</h1>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        
        user = st.session_state.current_user
        st.markdown(f'**Nome de usuário:** {user["username"]}')
        st.markdown(f'**Email:** {user["email"]}')
        st.markdown(f'**Membro desde:** {datetime.fromisoformat(user["created_at"]).strftime("%d/%m/%Y")}')

        st.markdown('<p class="section-title">Configurações</p>', unsafe_allow_html=True)

        # Configurações de Tema
        theme_names = {k: v['name'] for k, v in THEMES.items()}
        current_theme_name = theme_names[st.session_state.current_theme]
        selected_theme_name = st.selectbox("Tema da Interface", options=theme_names.values(), index=list(theme_names.values()).index(current_theme_name))
        
        if selected_theme_name != current_theme_name:
            new_theme_key = [k for k, v in theme_names.items() if v == selected_theme_name][0]
            st.session_state.current_theme = new_theme_key
            st.rerun()

        # Botões de Ação
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("Voltar para Tarefas", key="back_to_tasks", use_container_width=True):
            st.session_state.show_profile = False
            st.rerun()

        if st.button("Sair da Conta", key="logout_profile", use_container_width=True):
            st.session_state.current_user = None
            st.session_state.current_screen = "login"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# =============================
# Main App Logic
# =============================
def main():
    init_session_state()
    apply_theme_css()

    if not st.session_state.current_user:
        if st.session_state.current_screen == "register":
            show_register_screen()
        else:
            show_login_screen()
    else:
        # Sidebar
        with st.sidebar:
            st.markdown(f"### Olá, {st.session_state.current_user['username']}!")
            st.markdown("---_")
            if st.button("Ver Tarefas", key="sb_tasks", use_container_width=True):
                st.session_state.show_profile = False
                st.rerun()
            if st.button("Adicionar Tarefa", key="sb_add_task", use_container_width=True):
                st.session_state.task_to_edit = None
                st.session_state.show_task_form = True
                st.rerun()
            if st.button("Meu Perfil", key="sb_profile", use_container_width=True):
                st.session_state.show_profile = True
                st.rerun()
            st.markdown("---_")
            if st.button("Sair", key="sb_logout", use_container_width=True):
                st.session_state.current_user = None
                st.session_state.current_screen = "login"
                st.rerun()
        
        # Conteúdo Principal
        show_main_screen()

if __name__ == "__main__":
    main()

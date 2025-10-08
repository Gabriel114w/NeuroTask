import streamlit as st
import time
from datetime import datetime
from utils import (
    get_user_by_email, get_user_by_username, create_user, update_user, delete_user,
    get_tasks, add_task, update_task, delete_task,
    send_task_notification, verify_password, migrate_password
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
        st.session_state.current_theme = "light_calm"
    if 'layout_mode' not in st.session_state:
        st.session_state.layout_mode = "desktop"
    if 'sidebar_expanded' not in st.session_state:
        st.session_state.sidebar_expanded = True
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = False

# =============================
# Theme Configuration - Cores Suaves e Pastéis
# =============================
THEMES = {
    "light_calm": {
        "name": "Calmo Claro",
        "primary": "#E3F2FD",
        "secondary": "#BBDEFB", 
        "accent": "#64B5F6",
        "background": "#FAFAFA",
        "surface": "#FFFFFF",
        "text": "#37474F",
        "text_secondary": "#78909C",
        "success": "#A5D6A7",
        "warning": "#FFE082",
        "error": "#EF9A9A",
        "border": "#E0E0E0",
        "shadow": "rgba(0, 0, 0, 0.08)",
        "hover": "#F5F5F5"
    },
    "light_warm": {
        "name": "Suave Claro",
        "primary": "#FFF3E0",
        "secondary": "#FFE0B2",
        "accent": "#FFB74D",
        "background": "#FAFAFA",
        "surface": "#FFFFFF",
        "text": "#4E342E",
        "text_secondary": "#8D6E63",
        "success": "#C5E1A5",
        "warning": "#FFCC80",
        "error": "#FFAB91",
        "border": "#E0E0E0",
        "shadow": "rgba(0, 0, 0, 0.08)",
        "hover": "#FFF8F0"
    },
    "dark_calm": {
        "name": "Calmo Escuro",
        "primary": "#263238",
        "secondary": "#37474F",
        "accent": "#64B5F6",
        "background": "#1A1A1A",
        "surface": "#263238",
        "text": "#ECEFF1",
        "text_secondary": "#B0BEC5",
        "success": "#81C784",
        "warning": "#FFD54F",
        "error": "#E57373",
        "border": "#37474F",
        "shadow": "rgba(0, 0, 0, 0.3)",
        "hover": "#2C393F"
    },
    "dark_warm": {
        "name": "Suave Escuro",
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
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-sizing: border-box;
    }}
    
    .main {{
        background-color: {theme['background']};
        padding: 0;
    }}
    
    .block-container {{
        padding: 2rem 1rem;
        max-width: 1400px;
    }}
    
    /* Task Cards - Blocos Visuais Dinâmicos */
    .task-card {{
        background: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px {theme['shadow']};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .task-card::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: {theme['accent']};
        transition: width 0.3s ease;
    }}
    
    .task-card:hover {{
        box-shadow: 0 6px 20px {theme['shadow']};
        transform: translateY(-2px);
        border-color: {theme['accent']};
    }}
    
    .task-card:hover::before {{
        width: 6px;
    }}
    
    .task-completed {{
        opacity: 0.65;
        background: {theme['primary']};
    }}
    
    .task-completed::before {{
        background: {theme['success']} !important;
    }}
    
    .task-priority-high::before {{
        background: {theme['error']} !important;
    }}
    
    .task-priority-medium::before {{
        background: {theme['warning']} !important;
    }}
    
    .task-priority-low::before {{
        background: {theme['success']} !important;
    }}
    
    .task-title {{
        font-size: 18px;
        font-weight: 600;
        color: {theme['text']};
        margin: 0 0 8px 0;
        line-height: 1.4;
    }}
    
    .task-description {{
        font-size: 14px;
        color: {theme['text_secondary']};
        margin: 8px 0;
        line-height: 1.6;
    }}
    
    .task-meta {{
        font-size: 13px;
        color: {theme['text_secondary']};
        margin-top: 12px;
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }}
    
    .task-meta-item {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }}
    
    /* Priority Badges */
    .priority-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .priority-high {{
        background: {theme['error']};
        color: white;
    }}
    
    .priority-medium {{
        background: {theme['warning']};
        color: {theme['text']};
    }}
    
    .priority-low {{
        background: {theme['success']};
        color: white;
    }}
    
    /* Stats Cards */
    .stats-card {{
        background: {theme['surface']};
        border: 1px solid {theme['border']};
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px {theme['shadow']};
        transition: all 0.3s ease;
    }}
    
    .stats-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 6px 16px {theme['shadow']};
    }}
    
    .stats-number {{
        font-size: 36px;
        font-weight: 700;
        color: {theme['accent']};
        line-height: 1;
        margin-bottom: 8px;
    }}
    
    .stats-label {{
        font-size: 12px;
        color: {theme['text_secondary']};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Page Headers */
    .page-header {{
        font-size: 32px;
        font-weight: 700;
        color: {theme['text']};
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }}
    
    .page-subtitle {{
        font-size: 16px;
        color: {theme['text_secondary']};
        margin-bottom: 32px;
    }}
    
    .section-title {{
        font-size: 14px;
        font-weight: 600;
        color: {theme['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 32px 0 16px 0;
    }}
    
    /* Profile Card */
    .profile-card {{
        background: {theme['surface']};
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 2px 8px {theme['shadow']};
        border: 1px solid {theme['border']};
    }}
    
    /* Buttons */
    .stButton button {{
        background-color: {theme['accent']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.2s ease;
        width: 100%;
    }}
    
    .stButton button:hover {{
        background-color: {theme['accent']};
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px {theme['shadow']};
    }}
    
    /* Sidebar */
    div[data-testid="stSidebarContent"] {{
        background-color: {theme['surface']};
        border-right: 1px solid {theme['border']};
    }}
    
    /* Forms */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {{
        border-radius: 8px;
        border: 1px solid {theme['border']};
        background-color: {theme['surface']};
        color: {theme['text']};
        padding: 12px;
        font-size: 14px;
    }}
    
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {theme['accent']};
        box-shadow: 0 0 0 2px {theme['primary']};
    }}
    
    /* Checkbox */
    .stCheckbox {{
        margin-top: 8px;
    }}
    
    /* Mobile Responsive */
    @media (max-width: 768px) {{
        .block-container {{
            padding: 1rem 0.5rem;
        }}
        
        .task-card {{
            padding: 16px;
            margin: 12px 0;
        }}
        
        .task-title {{
            font-size: 16px;
        }}
        
        .stats-number {{
            font-size: 28px;
        }}
        
        .page-header {{
            font-size: 24px;
        }}
    }}
    
    /* Notification */
    .notification-popup {{
        position: fixed;
        top: 24px;
        right: 24px;
        background: {theme['surface']};
        color: {theme['text']};
        padding: 16px 20px;
        border-radius: 12px;
        border-left: 4px solid {theme['accent']};
        box-shadow: 0 6px 24px {theme['shadow']};
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    /* Empty State */
    .empty-state {{
        text-align: center;
        padding: 64px 32px;
        color: {theme['text_secondary']};
    }}
    
    .empty-state-icon {{
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.5;
    }}
    
    /* Divider */
    hr {{
        border: none;
        border-top: 1px solid {theme['border']};
        margin: 24px 0;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# =============================
# Utility Functions
# =============================
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
    <div class="notification-popup">
        <strong>{notificacao['title']}</strong><br>
        {notificacao['description']}
    </div>
    """, unsafe_allow_html=True)

def get_user_stats(user_id):
    """Calcula estatísticas do usuário"""
    tasks = get_tasks(user_id)
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get("completed", False)])
    pending_tasks = total_tasks - completed_tasks
    
    return {
        "total": total_tasks,
        "completed": completed_tasks, 
        "pending": pending_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }

# =============================
# Authentication Screens
# =============================
def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="page-header" style="text-align: center; margin-top: 80px;">NeuroTask</div>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle" style="text-align: center;">Organize suas tarefas com foco e clareza</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            identificador = st.text_input("Email ou Nome de Usuário", placeholder="Digite seu email ou usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            
            botao_login = st.form_submit_button("Entrar", use_container_width=True)
            
            if botao_login:
                if not identificador or not senha:
                    st.error("Preencha todos os campos")
                    return
                
                user = get_user_by_email(identificador.lower()) or get_user_by_username(identificador)
                if user and verify_password(senha, user["password"]):
                    # Migrar senha antiga se necessário
                    old_hash = user["password"]
                    if not (old_hash.startswith('$2b$') or old_hash.startswith('$2a$')):
                        migrate_password(user["id"], user["email"], senha, old_hash)
                    
                    st.session_state.current_user = user
                    st.session_state.current_screen = "dashboard"
                    st.success("Login realizado com sucesso!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
        
        st.markdown("---")
        if st.button("Criar Nova Conta", use_container_width=True):
            st.session_state.current_screen = "register"
            st.rerun()

def tela_registro():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="page-header" style="text-align: center; margin-top: 80px;">NeuroTask</div>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle" style="text-align: center;">Criar Nova Conta</p>', unsafe_allow_html=True)
        
        with st.form("register_form"):
            usuario = st.text_input("Nome de Usuário", placeholder="Escolha um nome de usuário")
            email = st.text_input("Email", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="Escolha uma senha")
            confirmar_senha = st.text_input("Confirmar Senha", type="password", placeholder="Digite a senha novamente")
            
            botao_registro = st.form_submit_button("Registrar", use_container_width=True)
            
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
                
                try:
                    novo = create_user(usuario, email.lower(), senha)
                    if novo:
                        st.success("Registro bem-sucedido! Faça login.")
                        time.sleep(0.5)
                        st.session_state.current_screen = "login"
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar conta: {str(e)}")
        
        st.markdown("---")
        if st.button("Voltar", use_container_width=True):
            st.session_state.current_screen = "login"
            st.rerun()

# =============================
# Sidebar Menu
# =============================
def mostrar_menu_lateral():
    with st.sidebar:
        # Header do usuário
        user = st.session_state.current_user
        st.markdown(f'<div class="page-header" style="font-size: 20px; margin-bottom: 8px;">Olá, {user.get("username", "Usuário")}</div>', unsafe_allow_html=True)
        
        # Estatísticas rápidas
        stats = get_user_stats(user["id"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["pending"]}</div><div class="stats-label">Pendentes</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["completed"]}</div><div class="stats-label">Concluídas</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title" style="margin-top: 32px;">Menu</div>', unsafe_allow_html=True)
        
        # Menu de navegação
        if st.button("Nova Tarefa", use_container_width=True, key="btn_nova_tarefa"):
            st.session_state.show_task_form = True
            st.session_state.task_to_edit = None
            st.session_state.current_screen = "dashboard"
            st.rerun()
        
        if st.button("Dashboard", use_container_width=True, key="btn_dashboard"):
            st.session_state.show_task_form = False
            st.session_state.show_profile = False
            st.session_state.current_screen = "dashboard"
            st.rerun()
        
        if st.button("Tarefas Pendentes", use_container_width=True, key="btn_pendentes"):
            st.session_state.show_task_form = False
            st.session_state.show_profile = False
            st.session_state.current_screen = "pending_tasks"
            st.rerun()
        
        if st.button("Perfil", use_container_width=True, key="btn_perfil"):
            st.session_state.show_profile = True
            st.session_state.show_task_form = False
            st.session_state.current_screen = "dashboard"
            st.rerun()
        
        if st.button("Configurações", use_container_width=True, key="btn_config"):
            st.session_state.show_task_form = False
            st.session_state.show_profile = False
            st.session_state.current_screen = "settings"
            st.rerun()
        
        st.markdown("---")
        
        # Layout toggle
        layout_text = "Modo Mobile" if st.session_state.layout_mode == "desktop" else "Modo Desktop"
        
        if st.button(layout_text, use_container_width=True, key="btn_layout"):
            st.session_state.layout_mode = "mobile" if st.session_state.layout_mode == "desktop" else "desktop"
            st.rerun()
        
        # Logout
        if st.button("Sair", use_container_width=True, key="btn_sair"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session_state()
            st.rerun()

# =============================
# Profile Screen
# =============================
def mostrar_perfil():
    st.markdown('<div class="page-header">Perfil do Usuário</div>', unsafe_allow_html=True)
    
    user = st.session_state.current_user
    stats = get_user_stats(user["id"])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown(f"### {user.get('username', 'Usuário')}")
        st.markdown(f"**Email:** {user.get('email', 'N/A')}")
        st.markdown(f"**Membro desde:** {user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A'}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown("### Estatísticas")
        st.markdown(f"**Total de Tarefas:** {stats['total']}")
        st.markdown(f"**Tarefas Concluídas:** {stats['completed']}")
        st.markdown(f"**Tarefas Pendentes:** {stats['pending']}")
        st.markdown(f"**Taxa de Conclusão:** {stats['completion_rate']:.1f}%")
        
        if stats['total'] > 0:
            st.progress(stats['completion_rate'] / 100)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Zona de perigo
    st.markdown("### Zona de Perigo")
    st.warning("**Atenção:** Esta ação é irreversível!")
    
    if st.button("Excluir Conta Permanentemente"):
        st.session_state.confirm_delete = True
    
    if st.session_state.get('confirm_delete', False):
        st.error("Tem certeza que deseja excluir sua conta? Todos os seus dados serão perdidos!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sim, excluir"):
                delete_user(user['email'])
                st.success("Conta excluída com sucesso!")
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                init_session_state()
                st.rerun()
        
        with col2:
            if st.button("Cancelar"):
                st.session_state.confirm_delete = False
                st.rerun()
    
    if st.button("Voltar ao Dashboard"):
        st.session_state.show_profile = False
        st.session_state.current_screen = "dashboard"
        st.rerun()

# =============================
# Settings Screen
# =============================
def tela_configuracoes():
    st.markdown('<div class="page-header">Configurações</div>', unsafe_allow_html=True)
    
    st.markdown("### Escolher Tema")
    
    # Temas claros
    st.markdown("#### Temas Claros")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(THEMES["light_calm"]["name"], use_container_width=True):
            st.session_state.current_theme = "light_calm"
            st.rerun()
    
    with col2:
        if st.button(THEMES["light_warm"]["name"], use_container_width=True):
            st.session_state.current_theme = "light_warm"
            st.rerun()
    
    # Temas escuros
    st.markdown("#### Temas Escuros")
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button(THEMES["dark_calm"]["name"], use_container_width=True):
            st.session_state.current_theme = "dark_calm"
            st.rerun()
    
    with col4:
        if st.button(THEMES["dark_warm"]["name"], use_container_width=True):
            st.session_state.current_theme = "dark_warm"
            st.rerun()
    
    st.markdown("---")
    
    st.markdown(f"**Tema Atual:** {THEMES[st.session_state.current_theme]['name']}")
    st.markdown(f"**Modo de Layout:** {st.session_state.layout_mode.title()}")
    
    if st.button("Voltar ao Dashboard"):
        st.session_state.current_screen = "dashboard"
        st.rerun()

# =============================
# Task Management
# =============================
def render_task_card(tarefa, container_type="normal"):
    """Renderiza um card de tarefa com visual otimizado"""
    
    priority_class = ""
    if tarefa.get("priority") == "high":
        priority_class = "task-priority-high"
    elif tarefa.get("priority") == "medium":
        priority_class = "task-priority-medium"
    else:
        priority_class = "task-priority-low"
    
    completed_class = "task-completed" if tarefa.get("completed", False) else ""
    
    card_class = f"task-card {priority_class} {completed_class}"
    
    with st.container():
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([0.5, 5, 1.5])
        
        with col1:
            # Checkbox para marcar como concluída
            concluida = st.checkbox(
                "✓", 
                value=tarefa.get("completed", False), 
                key=f"task_check_{tarefa['id']}_{container_type}",
                label_visibility="collapsed"
            )
            
            if concluida != tarefa.get("completed", False):
                update_task(tarefa["id"], {"completed": concluida})
                st.rerun()
        
        with col2:
            # Título e descrição
            title_style = "text-decoration: line-through; opacity: 0.6;" if tarefa.get("completed", False) else ""
            st.markdown(f'<div class="task-title" style="{title_style}">{tarefa["title"]}</div>', unsafe_allow_html=True)
            
            if tarefa.get('description'):
                st.markdown(f'<div class="task-description" style="{title_style}">{tarefa["description"]}</div>', unsafe_allow_html=True)
            
            # Informações adicionais
            meta_items = []
            if tarefa.get('due_date'):
                meta_items.append(f'<span class="task-meta-item">Horário: {tarefa["due_date"]}</span>')
            if tarefa.get('priority'):
                priority_text = {"high": "Alta", "medium": "Média", "low": "Baixa"}.get(tarefa['priority'], "")
                priority_class_badge = f"priority-{tarefa['priority']}"
                meta_items.append(f'<span class="priority-badge {priority_class_badge}">{priority_text}</span>')
            if tarefa.get('type') == 'daily':
                meta_items.append('<span class="task-meta-item">Diária</span>')
            
            if meta_items:
                st.markdown(f'<div class="task-meta">{" ".join(meta_items)}</div>', unsafe_allow_html=True)
        
        with col3:
            # Botões de ação
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("Editar", key=f"edit_{tarefa['id']}_{container_type}", help="Editar tarefa", use_container_width=True):
                    st.session_state.task_to_edit = tarefa
                    st.session_state.show_task_form = True
                    st.rerun()
            
            with col_delete:
                if st.button("Excluir", key=f"delete_{tarefa['id']}_{container_type}", help="Excluir tarefa", use_container_width=True):
                    delete_task(tarefa["id"])
                    st.success("Tarefa excluída!")
                    time.sleep(0.5)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def formulario_tarefa():
    """Formulário para adicionar/editar tarefa"""
    tarefa = st.session_state.task_to_edit or {}
    titulo_form = "Editar Tarefa" if tarefa else "Nova Tarefa"
    
    st.markdown(f'<div class="page-header">{titulo_form}</div>', unsafe_allow_html=True)
    
    # Usar inputs diretos fora do form para melhor controle
    col1, col2 = st.columns(2)
    
    with col1:
        titulo = st.text_input("Título da Tarefa", value=tarefa.get("title", ""), key="input_titulo")
        horario = st.text_input("Horário (HH:MM)", value=tarefa.get("due_date", ""), key="input_horario", placeholder="Ex: 14:30")
    
    with col2:
        prioridade = st.selectbox(
            "Prioridade",
            options=["low", "medium", "high"],
            index=["low", "medium", "high"].index(tarefa.get("priority", "low")),
            format_func=lambda x: {"low": "Baixa", "medium": "Média", "high": "Alta"}[x],
            key="input_prioridade"
        )
        diaria = st.checkbox("Tarefa Diária", value=tarefa.get("type") == "daily", key="input_diaria")
    
    descricao = st.text_area("Descrição", value=tarefa.get("description", ""), key="input_descricao", height=100)
    
    st.markdown("---")
    
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        if st.button("Salvar Tarefa", use_container_width=True, type="primary"):
            if not titulo.strip():
                st.error("O título é obrigatório!")
            else:
                try:
                    if tarefa.get("id"):
                        # Atualização
                        dados = {
                            "title": titulo.strip(),
                            "description": descricao.strip(),
                            "due_date": horario.strip(),
                            "priority": prioridade,
                            "type": "daily" if diaria else "single",
                            "completed": tarefa.get("completed", False)
                        }
                        update_task(tarefa["id"], dados)
                        st.success("Tarefa atualizada com sucesso!")
                    else:
                        # Criação
                        add_task(
                            st.session_state.current_user["id"],
                            title=titulo.strip(),
                            description=descricao.strip(),
                            due_date=horario.strip(),
                            type="daily" if diaria else "single",
                            priority=prioridade
                        )
                        st.success("Tarefa criada com sucesso!")
                    
                    # Limpar estado e recarregar
                    time.sleep(0.5)
                    st.session_state.task_to_edit = None
                    st.session_state.show_task_form = False
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro ao salvar tarefa: {str(e)}")
    
    with col_cancel:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.task_to_edit = None
            st.session_state.show_task_form = False
            st.rerun()

def tela_dashboard():
    """Dashboard principal com visualização de tarefas em blocos"""
    
    # Header
    st.markdown('<div class="page-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Visão geral das suas tarefas</div>', unsafe_allow_html=True)
    
    # Estatísticas rápidas
    stats = get_user_stats(st.session_state.current_user["id"])
    
    if st.session_state.layout_mode == "mobile":
        # Layout mobile - cards empilhados
        st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["total"]}</div><div class="stats-label">Total de Tarefas</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["pending"]}</div><div class="stats-label">Pendentes</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["completed"]}</div><div class="stats-label">Concluídas</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["completion_rate"]:.1f}%</div><div class="stats-label">Taxa de Conclusão</div></div>', unsafe_allow_html=True)
    else:
        # Layout desktop - cards em linha
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["total"]}</div><div class="stats-label">Total</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["pending"]}</div><div class="stats-label">Pendentes</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["completed"]}</div><div class="stats-label">Concluídas</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["completion_rate"]:.1f}%</div><div class="stats-label">Conclusão</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Buscar tarefas
    tasks = get_tasks(st.session_state.current_user["id"])
    
    if not tasks:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <h3>Nenhuma tarefa encontrada</h3>
            <p>Comece criando sua primeira tarefa usando o botão "Nova Tarefa" no menu lateral.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Filtros e ordenação
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        filtro_status = st.selectbox(
            "Status", 
            ["todas", "pendentes", "concluidas"],
            format_func=lambda x: {"todas": "Todas", "pendentes": "Pendentes", "concluidas": "Concluídas"}[x],
            key="filtro_status"
        )
    
    with col_filter2:
        filtro_prioridade = st.selectbox(
            "Prioridade",
            ["todas", "high", "medium", "low"],
            format_func=lambda x: {"todas": "Todas", "high": "Alta", "medium": "Média", "low": "Baixa"}[x],
            key="filtro_prioridade"
        )
    
    with col_filter3:
        ordenacao = st.selectbox(
            "Ordenar por",
            ["priority", "due_date", "title", "created_at"],
            format_func=lambda x: {"due_date": "Horário", "priority": "Prioridade", "title": "Título", "created_at": "Criação"}[x],
            key="ordenacao"
        )
    
    # Aplicar filtros
    filtered_tasks = tasks
    
    if filtro_status == "pendentes":
        filtered_tasks = [t for t in filtered_tasks if not t.get("completed", False)]
    elif filtro_status == "concluidas":
        filtered_tasks = [t for t in filtered_tasks if t.get("completed", False)]
    
    if filtro_prioridade != "todas":
        filtered_tasks = [t for t in filtered_tasks if t.get("priority") == filtro_prioridade]
    
    # Ordenar tarefas
    if ordenacao == "priority":
        priority_order = {"high": 3, "medium": 2, "low": 1}
        filtered_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "low"), 1), reverse=True)
    elif ordenacao == "due_date":
        filtered_tasks.sort(key=lambda t: t.get("due_date", "99:99"))
    elif ordenacao == "title":
        filtered_tasks.sort(key=lambda t: t.get("title", "").lower())
    else:
        filtered_tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    
    # Exibir tarefas em blocos visuais
    st.markdown(f'<div class="section-title">{len(filtered_tasks)} tarefa(s) encontrada(s)</div>', unsafe_allow_html=True)
    
    if not filtered_tasks:
        st.info("Nenhuma tarefa corresponde aos filtros selecionados.")
    else:
        for i, tarefa in enumerate(filtered_tasks):
            render_task_card(tarefa, f"dashboard_{i}")

def tela_tarefas_pendentes():
    """Tela específica para tarefas pendentes"""
    st.markdown('<div class="page-header">Tarefas Pendentes</div>', unsafe_allow_html=True)
    
    tasks = get_tasks(st.session_state.current_user["id"])
    pending_tasks = [t for t in tasks if not t.get("completed", False)]
    
    if not pending_tasks:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">✓</div>
            <h3>Parabéns!</h3>
            <p>Você não tem tarefas pendentes no momento.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Voltar ao Dashboard", use_container_width=True):
            st.session_state.current_screen = "dashboard"
            st.rerun()
        return
    
    st.markdown(f'<div class="page-subtitle">Você tem {len(pending_tasks)} tarefa(s) pendente(s)</div>', unsafe_allow_html=True)
    
    # Ordenar por prioridade e horário
    priority_order = {"high": 3, "medium": 2, "low": 1}
    pending_tasks.sort(key=lambda t: (
        -priority_order.get(t.get("priority", "low"), 1),
        t.get("due_date", "99:99")
    ))
    
    for i, tarefa in enumerate(pending_tasks):
        render_task_card(tarefa, f"pending_{i}")
    
    st.markdown("---")
    
    if st.button("Voltar ao Dashboard", use_container_width=True):
        st.session_state.current_screen = "dashboard"
        st.rerun()

# =============================
# Main Application
# =============================
def main():
    # Configuração inicial
    st.set_page_config(
        page_title="NeuroTask - Organize suas tarefas com foco",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    apply_theme_css()
    
    # Verificar notificações
    if st.session_state.current_user:
        notificacoes = verificar_notificacoes()
        for notif in notificacoes:
            mostrar_notificacao_popup(notif)
    
    # Routing baseado no estado atual
    if not st.session_state.current_user:
        # Usuário não logado
        if st.session_state.current_screen == "register":
            tela_registro()
        else:
            tela_login()
    else:
        # Usuário logado - mostrar sidebar
        mostrar_menu_lateral()
        
        # Verificar se deve mostrar formulário de tarefa
        if st.session_state.show_task_form:
            formulario_tarefa()
        elif st.session_state.show_profile:
            mostrar_perfil()
        elif st.session_state.current_screen == "settings":
            tela_configuracoes()
        elif st.session_state.current_screen == "pending_tasks":
            tela_tarefas_pendentes()
        else:
            # Dashboard padrão
            tela_dashboard()

if __name__ == "__main__":
    main()

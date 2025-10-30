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
        "text": "#b582b5",
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
        "text": "#FFFFFF",
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
    "primary": "#145A1A",
    "secondary": "#1C7A2A",
    "accent": "#81C784",
    "background": "#121212",
    "surface": "#1E272C",
    "text": "#FFFFFF",
    "text_secondary": "#B2DFDB",
    "success": "#66BB6A",
    "warning": "#FFD54F",
    "error": "#E57373",
    "border": "#37474F",
    "shadow": "rgba(0, 0, 0, 0.5)",
    "hover": "#263238"
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
    
    /* Cores de Prioridade Suaves - Bordas */
    .task-priority-high::before {{
        background: {theme['error']} !important; /* Vermelho Suave */
    }}
    
    .task-priority-medium::before {{
        background: {theme['warning']} !important; /* Amarelo Suave */
    }}
    
    .task-priority-low::before {{
        background: {theme['success']} !important; /* Verde Suave */
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
    
    /* Cores de Prioridade Suaves - Badges */
    .priority-high {{
        background: {theme['error']};
        color: {theme['text']}; /* Texto escuro para contraste suave */
    }}
    
    .priority-medium {{
        background: {theme['warning']};
        color: {theme['text']};
    }}
    
    .priority-low {{
        background: {theme['success']};
        color: {theme['text']}; /* Texto escuro para contraste suave */
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
        bottom: 20px;
        right: 20px;
        background-color: {theme['surface']};
        color: {theme['text']};
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px {theme['shadow']};
        border-left: 5px solid {theme['accent']};
        z-index: 1000;
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.3s ease-out, transform 0.3s ease-out;
    }}
    
    .notification-popup.show {{
        opacity: 1;
        transform: translateY(0);
    }}
    
    .notification-title {{
        font-weight: 600;
        margin-bottom: 5px;
    }}
    
    .notification-time {{
        font-size: 12px;
        color: {theme['text_secondary']};
    }}
    
    /* Login Screen Specific Styles */
    .login-container {{
        background-color: transparent; /* Fundo transparente para não criar uma caixa branca */
        padding: 40px;
        border-radius: 16px;
        box-shadow: none; /* Sem sombra */
        max-width: 500px;
        margin: 80px auto;
        border: none; /* Sem borda */
    }}
    
    .login-header {{
        font-size: 40px;
        font-weight: 800;
        color: {theme['accent']}; /* Destaque com a cor de acento */
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px {theme['shadow']};
    }}
    
    .login-slogan {{
        font-size: 18px;
        font-weight: 500;
        color: {theme['text_secondary']};
        text-align: center;
        margin-bottom: 30px;
        line-height: 1.4;
    }}
    
    /* Streamlit Overrides */
    div[data-testid="stAppViewBlockContainer"] {{
        background-color: {theme['background']};
    }}
    
    /* Fix for Streamlit's default header/footer */
    header {{
        background-color: transparent !important;
    }}
    
    footer {{
        visibility: hidden;
    }}
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# =============================
# Helper Functions
# =============================
def get_user_stats(user_id):
    tasks = get_tasks(user_id)
    total = len(tasks)
    completed = len([t for t in tasks if t.get("completed", False)])
    pending = total - completed
    completion_rate = (completed / total * 100) if total > 0 else 0
    return {"total": total, "completed": completed, "pending": pending, "completion_rate": completion_rate}

# =============================
# Screen Functions
# =============================
def tela_login():
    apply_theme_css() 
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header">NeuroTask</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-slogan">Organize suas tarefas com foco e clareza</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="Sua senha secreta")
            
            botao_login = st.form_submit_button("Entrar", use_container_width=True)
            
            if botao_login:
                if not all([email, senha]):
                    st.error("Preencha todos os campos")
                    return
                
                user = get_user_by_email(email.lower())
                
                if user and verify_password(senha, user.get("password", "")):
                    if not user.get("password", "").startswith('$2b$'):
                        migrate_password(user["id"], email.lower(), senha, user.get("password", ""))
                    
                    st.session_state.current_user = user
                    
                    saved_theme = user.get("theme_settings", {}).get("current_theme")
                    if saved_theme and saved_theme in THEMES:
                        st.session_state.current_theme = saved_theme
                    
                    st.success("Login bem-sucedido!")
                    time.sleep(0.5)
                    st.session_state.current_screen = "dashboard"
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos")
        
        st.markdown("--")
        if st.button("Criar Nova Conta", use_container_width=True):
            st.session_state.current_screen = "register"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def tela_registro():
    apply_theme_css()
    
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
                    novo = create_user(usuario, email.lower(), senha, theme="light_lavender")
                    if novo:
                        st.success("Registro bem-sucedido! Faça login.")
                        time.sleep(0.5)
                        st.session_state.current_screen = "login"
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar conta: {str(e)}")
        
        st.markdown("--")
        if st.button("Voltar", use_container_width=True):
            st.session_state.current_screen = "login"
            st.rerun()

# =============================
# Sidebar Menu
# =============================
def mostrar_menu_lateral():
    with st.sidebar:
        user = st.session_state.current_user
        st.markdown(f'<div class="page-header" style="font-size: 20px; margin-bottom: 8px;">Olá, {user.get("username", "Usuário")}</div>', unsafe_allow_html=True)
        
        stats = get_user_stats(user["id"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["pending"]}</div><div class="stats-label">Pendentes</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["completed"]}</div><div class="stats-label">Concluídas</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title" style="margin-top: 32px;">Menu</div>', unsafe_allow_html=True)
        
        if st.button("Nova Tarefa", use_container_width=True, key="btn_nova_tarefa"):
            st.session_state.show_task_form = True
            st.session_state.task_to_edit = None
            st.session_state.current_screen = "dashboard"
            st.rerun()
        
        if st.button("Início", use_container_width=True, key="btn_dashboard"):
            st.session_state.show_task_form = False
            st.session_state.show_profile = False
            st.session_state.current_screen = "dashboard"
            st.rerun()
        
        if st.button("Tarefas Pendentes", use_container_width=True, key="btn_pending"):
            st.session_state.show_task_form = False
            st.session_state.show_profile = False
            st.session_state.current_screen = "pending_tasks"
            st.rerun()
            
        if st.button("Tarefas Concluídas", use_container_width=True, key="btn_completed"):
            st.session_state.show_task_form = False
            st.session_state.show_profile = False
            st.session_state.current_screen = "completed_tasks"
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
        
        st.markdown("--")
        
        if st.button("Guia de Foco Rápido", use_container_width=True, key="btn_tutorial"):
            st.session_state.show_tutorial = True
            st.session_state.current_screen = "dashboard"
            st.rerun()
        
        if st.button("Sair", use_container_width=True, key="btn_sair"):
            if st.session_state.current_user:
                update_user(st.session_state.current_user["email"], {"theme_settings": {"current_theme": st.session_state.current_theme}})
            
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
    
    st.markdown("--")
    
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
    
    if st.button("Voltar ao Início"):
        st.session_state.show_profile = False
        st.session_state.current_screen = "dashboard"
        st.rerun()

# =============================
# Settings Screen
# =============================
def tela_configuracoes():
    st.markdown('<div class="page-header">Configurações</div>', unsafe_allow_html=True)
    
    st.markdown("### Escolher Tema")
    
    st.markdown("#### Temas Claros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(THEMES["light_lavender"]["name"], use_container_width=True):
            st.session_state.current_theme = "light_lavender"
            if st.session_state.current_user:
                update_user(st.session_state.current_user["email"], {"theme_settings": {"current_theme": "light_lavender"}})
            st.rerun()
    
    with col2:
        if st.button(THEMES["light_mint"]["name"], use_container_width=True):
            st.session_state.current_theme = "light_mint"
            if st.session_state.current_user:
                update_user(st.session_state.current_user["email"], {"theme_settings": {"current_theme": "light_mint"}})
            st.rerun()
            
    with col3:
        if st.button(THEMES["light_peach"]["name"], use_container_width=True):
            st.session_state.current_theme = "light_peach"
            if st.session_state.current_user:
                update_user(st.session_state.current_user["email"], {"theme_settings": {"current_theme": "light_peach"}})
            st.rerun()
    
    st.markdown("#### Temas Escuros")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button(THEMES["dark_lavender"]["name"], use_container_width=True):
            st.session_state.current_theme = "dark_lavender"
            if st.session_state.current_user:
                update_user(st.session_state.current_user["email"], {"theme_settings": {"current_theme": "dark_lavender"}})
            st.rerun()
    
    with col5:
        if st.button(THEMES["dark_mint"]["name"], use_container_width=True):
            st.session_state.current_theme = "dark_mint"
            if st.session_state.current_user:
                update_user(st.session_state.current_user["email"], {"theme_settings": {"current_theme": "dark_mint"}})
            st.rerun()
            
    with col6:
        if st.button(THEMES["dark_brown"]["name"], use_container_width=True):
            st.session_state.current_theme = "dark_brown"
            if st.session_state.current_user:
                update_user(st.session_state.current_user["email"], {"theme_settings": {"current_theme": "dark_brown"}})
            st.rerun()
    
    st.markdown("--")
    
    st.markdown(f"**Tema Atual:** {THEMES[st.session_state.current_theme]['name']}")
    st.markdown(f"**Modo de Layout:** {st.session_state.layout_mode.title()}")
    
    if st.button("Voltar ao Início"):
        st.session_state.current_screen = "dashboard"
        st.rerun()

# =============================
# Task Management
# =============================
def render_task_card(tarefa, container_type="normal"):
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
            concluida = st.checkbox(
                "✓", 
                value=tarefa.get("completed", False), 
                key=f"task_check_{tarefa['id']}_{container_type}",
                label_visibility="collapsed"
            )
            
            if concluida != tarefa.get("completed", False):
                update_task(tarefa["id"], {"completed": concluida})
                # Adiciona uma notificação de sucesso para a conclusão
                if concluida:
                    st.toast(f"🎉 Tarefa '{tarefa['title']}' concluída! Ótimo trabalho!", icon="✅")
                else:
                    st.toast(f"🔄 Tarefa '{tarefa['title']}' reativada.", icon="↩️")
                time.sleep(0.1) # Pequeno delay para garantir que o toast apareça antes do rerun
                st.rerun()
        
        with col2:
            st.markdown(f'<div class="task-title">{tarefa["title"]}</div>', unsafe_allow_html=True)
            if tarefa.get("description"):
                st.markdown(f'<div class="task-description">{tarefa["description"]}</div>', unsafe_allow_html=True)
            
            meta_items = []
            if tarefa.get("due_date"):
                try:
                    # Tenta parsear como datetime (com hora)
                    if len(tarefa["due_date"]) > 10:
                        date_obj = datetime.strptime(tarefa["due_date"], "%Y-%m-%d %H:%M")
                        formatted_date = date_obj.strftime("%d/%m/%Y %H:%M")
                    # Tenta parsear como date (sem hora)
                    else:
                        date_obj = datetime.strptime(tarefa["due_date"], "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%d/%m/%Y")
                        
                    meta_items.append(f'<span class="task-meta-item">📅 {formatted_date}</span>')
                except ValueError:
                    meta_items.append(f'<span class="task-meta-item">📅 {tarefa["due_date"]}</span>')
            
            priority_map = {
                "high": f'<span class="priority-badge priority-high">Alta</span>',
                "medium": f'<span class="priority-badge priority-medium">Média</span>',
                "low": f'<span class="priority-badge priority-low">Baixa</span>'
            }
            
            # Adiciona a data de criação
            created_at_str = tarefa.get("created_at", "")
            if created_at_str:
                try:
                    # O created_at vem do banco com formato ISO (ex: 2024-01-01T10:00:00.000000+00:00)
                    created_date_obj = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    formatted_created_date = created_date_obj.strftime("%d/%m/%Y")
                    meta_items.append(f'<span class="task-meta-item">Criada em: {formatted_created_date}</span>')
                except ValueError:
                    pass # Ignora se não conseguir formatar
            
            meta_items.append(priority_map.get(tarefa.get("priority", "medium"), ""))
            
            st.markdown(f'<div class="task-meta">{"".join(meta_items)}</div>', unsafe_allow_html=True)
            
        with col3:
            col_edit, col_delete = st.columns(2)
            
            with col_edit:
                if st.button("Editar", key=f"edit_{tarefa['id']}_{container_type}", use_container_width=True):
                    st.session_state.task_to_edit = tarefa
                    st.session_state.show_task_form = True
                    st.rerun()
            
            with col_delete:
                if st.button("Excluir", key=f"delete_{tarefa['id']}_{container_type}", use_container_width=True):
                    delete_task(tarefa["id"])
                    st.success("Tarefa excluída!")
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
            priority = st.selectbox(
                "Prioridade",
                options=priority_options,
                format_func=lambda x: priority_labels.get(x, x.capitalize()),
                index=priority_options.index(task_data.get("priority", "medium")), key="priority_select"
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
    
    # Filtro por Prioridade
    if st.session_state.filter_priority != "all":
        filtered_tasks = [t for t in filtered_tasks if t.get("priority") == st.session_state.filter_priority]
        
    # Filtro por Tipo (opcional, usando o que já existe)
    if st.session_state.filter_type != "all":
        filtered_tasks = [t for t in filtered_tasks if t.get("type") == st.session_state.filter_type]
        
    # 2. Ordenação
    sort_key = st.session_state.filter_sort
    
    if sort_key == "priority":
        # Prioridade (Alta > Média > Baixa) e Data de Vencimento (mais próxima primeiro)
        priority_order = {"high": 3, "medium": 2, "low": 1}
        sorted_tasks = sorted(filtered_tasks, 
                              key=lambda x: (priority_order.get(x.get("priority", "medium"), 0), x.get("due_date", "9999-12-31")), 
                              reverse=True)
    elif sort_key == "creation_date":
        # Data de Criação (mais antiga primeiro)
        sorted_tasks = sorted(filtered_tasks, 
                              key=lambda x: x.get("created_at", "0000-01-01"), 
                              reverse=False)
    elif sort_key == "due_date":
        # Data de Vencimento (mais próxima primeiro)
        sorted_tasks = sorted(filtered_tasks, 
                              key=lambda x: x.get("due_date", "9999-12-31"), 
                              reverse=False)
    else:
        # Default: Prioridade
        priority_order = {"high": 3, "medium": 2, "low": 1}
        sorted_tasks = sorted(filtered_tasks, 
                              key=lambda x: (priority_order.get(x.get("priority", "medium"), 0), x.get("due_date", "9999-12-31")), 
                              reverse=True)
        
    return sorted_tasks

def task_list_filters():
    """Renderiza os filtros de lista de tarefas."""
    st.markdown('<div class="section-title">Filtros de Tarefas</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    priority_options = {"all": "Todas", "high": "Alta", "medium": "Média", "low": "Baixa"}
    sort_options = {"priority": "Prioridade", "creation_date": "Data de Criação (Antigas Primeiro)", "due_date": "Data de Vencimento (Próximas Primeiro)"}
    type_options = {"all": "Todos", "single": "Única", "daily": "Diária"}
    
    with col1:
        selected_priority = st.selectbox(
            "Filtrar por Prioridade",
            options=list(priority_options.keys()),
            format_func=lambda x: priority_options[x],
            key="filter_priority_select",
            index=list(priority_options.keys()).index(st.session_state.filter_priority)
        )
        if selected_priority != st.session_state.filter_priority:
            st.session_state.filter_priority = selected_priority
            st.rerun()
            
    with col2:
        selected_sort = st.selectbox(
            "Ordenar por",
            options=list(sort_options.keys()),
            format_func=lambda x: sort_options[x],
            key="filter_sort_select",
            index=list(sort_options.keys()).index(st.session_state.filter_sort)
        )
        if selected_sort != st.session_state.filter_sort:
            st.session_state.filter_sort = selected_sort
            st.rerun()
            
    with col3:
        selected_type = st.selectbox(
            "Filtrar por Tipo",
            options=list(type_options.keys()),
            format_func=lambda x: type_options[x],
            key="filter_type_select",
            index=list(type_options.keys()).index(st.session_state.filter_type)
        )
        if selected_type != st.session_state.filter_type:
            st.session_state.filter_type = selected_type
            st.rerun()
    
    st.markdown("---")

def dashboard_screen():
    apply_theme_css()
    
    user = st.session_state.current_user
    
    if st.session_state.show_tutorial:
        mostrar_tutorial()
        if st.button("Voltar ao Início", key="btn_tutorial_back"):
            st.session_state.show_tutorial = False
            st.rerun()
        return
    
    if st.session_state.show_task_form:
        task_form()
        return
    
    if st.session_state.show_profile:
        mostrar_perfil()
        return
    
    if st.session_state.current_screen == "settings":
        tela_configuracoes()
        return
    
    st.markdown(f'<div class="page-header">Início</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Bem-vindo(a) de volta, {user.get("username", "Usuário")}!</div>', unsafe_allow_html=True)
    
    stats = get_user_stats(user["id"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["total"]}</div><div class="stats-label">Total de Tarefas</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["completed"]}</div><div class="stats-label">Concluídas</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stats-card"><div class="stats-number">{stats["pending"]}</div><div class="stats-label">Pendentes</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">Tarefas Pendentes</div>', unsafe_allow_html=True)
    
    task_list_filters()
    
    pending_tasks = get_pending_tasks(user["id"])
    
    if pending_tasks:
        sorted_tasks = filter_and_sort_tasks(pending_tasks)
        
        if sorted_tasks:
            for task in sorted_tasks:
                render_task_card(task, container_type="dashboard")
        else:
            st.info("Nenhuma tarefa pendente encontrada com os filtros atuais.")
    else:
        st.info("Parabéns! Nenhuma tarefa pendente. Que tal adicionar uma nova?")
        if st.button("Adicionar Primeira Tarefa", key="btn_add_first_task"):
            st.session_state.show_task_form = True
            st.rerun()

def pending_tasks_screen():
    apply_theme_css()
    
    user = st.session_state.current_user
    
    st.markdown(f'<div class="page-header">Tarefas Pendentes</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Foque no que é mais importante.</div>', unsafe_allow_html=True)
    
    task_list_filters()
    
    pending_tasks = get_pending_tasks(user["id"])
    
    if pending_tasks:
        sorted_tasks = filter_and_sort_tasks(pending_tasks)
        
        if sorted_tasks:
            for task in sorted_tasks:
                render_task_card(task, container_type="pending")
        else:
            st.info("Nenhuma tarefa pendente encontrada com os filtros atuais.")
    else:
        st.info("Nenhuma tarefa pendente. Ótimo trabalho!")
        if st.button("Voltar ao Início"):
            st.session_state.current_screen = "dashboard"
            st.rerun()

def completed_tasks_screen():
    apply_theme_css()
    
    user = st.session_state.current_user
    
    st.markdown(f'<div class="page-header">Tarefas Concluídas</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Seu histórico de sucesso.</div>', unsafe_allow_html=True)
    
    task_list_filters()
    
    # Importa a função get_completed_tasks do utils.py
    from utils import get_completed_tasks
    completed_tasks = get_completed_tasks(user["id"])
    
    if completed_tasks:
        # Ordena as concluídas por data de conclusão (mais recente primeiro)
        sorted_tasks = sorted(completed_tasks, key=lambda x: x.get("updated_at", "0000-01-01"), reverse=True)
        
        # Aplica filtros (exceto o de conclusão, claro)
        sorted_tasks = filter_and_sort_tasks(sorted_tasks)
        
        if sorted_tasks:
            for task in sorted_tasks:
                render_task_card(task, container_type="completed")
        else:
            st.info("Nenhuma tarefa concluída encontrada com os filtros atuais.")
    else:
        st.info("Nenhuma tarefa concluída ainda. Comece a riscar a lista!")
        if st.button("Voltar ao Início"):
            st.session_state.current_screen = "dashboard"
            st.rerun()

# =============================
# Main Application Flow
# =============================
def main():
    st.set_page_config(layout="wide", page_title="NeuroTask - Foco e Clareza")
    
    # Inclusão do Manifest e Service Worker para PWA
    st.markdown("""
        <link rel="manifest" href="/static/manifest.json">
        <script>
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                    navigator.serviceWorker.register('/static/service-worker.js').then(function(registration) {
                        console.log('ServiceWorker registration successful with scope: ', registration.scope);
                    }, function(err) {
                        console.log('ServiceWorker registration failed: ', err);
                    });
                });
            }
        </script>
    """, unsafe_allow_html=True)
    init_session_state()
    
    if st.session_state.current_user is None:
        if 'current_theme' not in st.session_state:
            st.session_state.current_theme = "light_lavender"
        apply_theme_css()
        
        if st.session_state.current_screen == "login":
            tela_login()
        elif st.session_state.current_screen == "register":
            tela_registro()
    else:
        apply_theme_css()
        mostrar_menu_lateral()
        
        if st.session_state.current_screen == "dashboard":
            dashboard_screen()
        elif st.session_state.current_screen == "pending_tasks":
            pending_tasks_screen()
        elif st.session_state.current_screen == "completed_tasks":
            completed_tasks_screen()
        elif st.session_state.current_screen == "settings":
            tela_configuracoes()
        else:
            dashboard_screen()

if __name__ == "__main__":
    main()

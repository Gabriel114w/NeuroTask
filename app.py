import streamlit as st
import threading
import time
import os
from datetime import datetime
from utils import load_data, save_data, send_task_notification

# Caminhos dos arquivos
USERS_FILE = "users.json"
SESSION_FILE = "session.json"
SETTINGS_FILE = "settings.json"

# Inicializar o estado da sessão
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
if 'last_check_date' not in st.session_state:
    st.session_state.last_check_date = datetime.now().date()
if 'theme_settings' not in st.session_state:
    default_theme = {
        "primary_color": "#FFD6BA",
        "background_color": "#FFFFFF", 
        "secondary_color": "#A1C3D1",
        "text_color": "#FFFFFF",
        "success_color": "#A8D5BA",
        "warning_color": "#FFE7A0",
        "error_color": "#F4A6A6"
    }
    st.session_state.theme_settings = default_theme
if 'show_profile' not in st.session_state:
    st.session_state.show_profile = False
if 'menu_open' not in st.session_state:
    st.session_state.menu_open = False
if 'pending_notifications' not in st.session_state:
    st.session_state.pending_notifications = []

# Configuração da página
st.set_page_config(
    page_title="NeuroTask - Organizador de Tarefas para TDAH",
    page_icon="🧠",
    layout="centered"
)

# CSS personalizado para design amigável para TDAH com tema dinâmico
def apply_custom_css():
    theme = st.session_state.theme_settings
    st.markdown(f"""
    <style>
        .main > div {{
            padding-top: 2rem;
            background-color: {theme['background_color']};
            color: {theme['text_color']};
        }}
        .stButton > button {{
            width: 100%;
            background-color: {theme['primary_color']};
            color: white;
            border: none;
            border-radius: 5px;
        }}
        .stButton > button:hover {{
            background-color: {theme['secondary_color']};
            color: {theme['text_color']};
        }}
        .task-item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border: 1px solid #ddd;
            background-color: {theme['background_color']};
            color: {theme['text_color']};
        }}
        .task-completed {{
            background-color: {theme['success_color']}33;
            opacity: 0.7;
        }}
        .task-pending {{
            background-color: {theme['warning_color']}33;
        }}
        h1, h2, h3 {{
            color: {theme['primary_color']};
            text-align: center;
        }}
        .notification-popup {{
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: {theme['warning_color']};
            color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            z-index: 9999;
            max-width: 300px;
            animation: slideIn 0.5s ease-out;
        }}
        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        .settings-panel {{
            background-color: {theme['secondary_color']};
            padding: 20px;
            border-radius: 10px;
            border: 1px solid {theme['primary_color']};
        }}
        .menu-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: {theme['primary_color']};
            color: {theme['text_color']};
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 20px;
            z-index: 1000;
        }}
        .profile-avatar {{
            position: fixed;
            top: 20px;
            right: 80px;
            background: {theme['secondary_color']};
            color: {theme['text_color']};
            border: 2px solid {theme['primary_color']};
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 20px;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .dropdown-menu {{
            position: fixed;
            top: 75px;
            right: 20px;
            background: {theme['background_color']};
            border: 1px solid {theme['primary_color']};
            border-radius: 8px;
            padding: 10px 0;
            z-index: 1001;
            min-width: 180px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .dropdown-item {{
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            width: 100%;
            text-align: left;
            color: {theme['text_color']};
        }}
        .dropdown-item:hover {{
            background-color: {theme['secondary_color']};
        }}
    </style>
    """, unsafe_allow_html=True)

# Aplicar CSS personalizado
apply_custom_css()

def verificar_notificacoes():
    """Verifica se há tarefas que precisam de notificação"""
    if not st.session_state.current_user or "tasks" not in st.session_state.current_user:
        return []
    
    agora = datetime.now()
    hora_atual = agora.strftime("%H:%M")
    notificacoes = []
    
    for tarefa in st.session_state.current_user["tasks"]:
        if (tarefa.get("due_date") == hora_atual and 
            not tarefa.get("completed", False) and 
            not tarefa.get("notified_today", False)):
            
            # Marca como notificada hoje
            tarefa["notified_today"] = True
            notificacoes.append({
                "title": tarefa.get("title", "Tarefa"),
                "description": tarefa.get("description", "Hora de começar!")
            })
    
    # Resetar notificações à meia-noite
    if agora.date() != st.session_state.last_check_date:
        st.session_state.last_check_date = agora.date()
        for tarefa in st.session_state.current_user.get("tasks", []):
            tarefa.pop("notified_today", None)
    
    return notificacoes

def mostrar_notificacao_popup(notificacao):
    """Mostra notificação popup na tela"""
    st.markdown(f"""
    <div class="notification-popup" id="notification-{int(time.time())}">
        <strong>🔔 {notificacao['title']}</strong><br>
        {notificacao['description']}
        <button onclick="this.parentElement.style.display='none'" style="float: right; background: none; border: none; color: white; cursor: pointer;">×</button>
    </div>
    <script>
        setTimeout(function() {{
            var notification = document.getElementById('notification-{int(time.time())}');
            if (notification) {{
                notification.style.display = 'none';
            }}
        }}, 10000);
        
        // Notificação do navegador se permitido
        if (Notification.permission === "granted") {{
            new Notification("{notificacao['title']}", {{
                body: "{notificacao['description']}",
                icon: "🧠"
            }});
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(function (permission) {{
                if (permission === "granted") {{
                    new Notification("{notificacao['title']}", {{
                        body: "{notificacao['description']}",
                        icon: "🧠"
                    }});
                }}
            }});
        }}
    </script>
    """, unsafe_allow_html=True)

def carregar_tema_usuario():
    """Carrega tema específico do usuário"""
    if st.session_state.current_user:
        user_theme = st.session_state.current_user.get("theme_settings")
        if user_theme:
            st.session_state.theme_settings = user_theme
        else:
            # Aplicar tema padrão se usuário não tem tema personalizado
            default_theme = {
                "primary_color": "#FFD6BA",
                "background_color": "#FFF8F4", 
                "secondary_color": "#A1C3D1",
                "text_color": "#FFFFFF",
                "success_color": "#A8D5BA",
                "warning_color": "#FFE7A0",
                "error_color": "#F4A6A6"
            }
            st.session_state.theme_settings = default_theme

def verificar_sessao():
    """Verifica se existe sessão ativa"""
    sessao = load_data(SESSION_FILE, {})
    email = sessao.get("active_user_email")
    if email:
        usuarios = load_data(USERS_FILE, [])
        usuario = next((u for u in usuarios if u["email"] == email), None)
        if usuario:
            st.session_state.current_user = usuario
            carregar_tema_usuario()
            st.session_state.current_screen = "task_list"
            return True
    return False

def tela_login():
    """Exibir tela de login"""
    st.title("NeuroTask 🧠")
    st.subheader("Entre na sua conta")

    with st.form("login_form"):
        identificador = st.text_input("Email ou Nome de Usuário", key="login_identifier")
        senha = st.text_input("Senha", type="password", key="login_password")
        lembrar = st.checkbox("Lembrar-se de mim", key="remember_me")

        botao_login = st.form_submit_button("LOGIN")

        if botao_login:
            if not identificador or not senha:
                st.error("Preencha todos os campos")
                return

            usuarios = load_data(USERS_FILE, [])
            usuario = next((u for u in usuarios if 
                        (u["username"].lower() == identificador.lower() or 
                         u["email"].lower() == identificador.lower()) and 
                        u["password"] == senha), None)

            if usuario:
                st.session_state.current_user = usuario
                carregar_tema_usuario()
                if lembrar:
                    save_data(SESSION_FILE, {"active_user_email": usuario["email"]})
                st.session_state.current_screen = "task_list"
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")

    if st.button("Não tem conta ? Registre-se"):
        st.session_state.current_screen = "register"
        st.rerun()

def tela_registro():
    """Exibir tela de registro"""
    st.title("NeuroTask 🧠")
    st.subheader("Criar Conta")

    with st.form("register_form"):
        usuario = st.text_input("Nome de Usuário", key="reg_username")
        email = st.text_input("Email", key="reg_email")
        senha = st.text_input("Senha", type="password", key="reg_password")
        confirmar_senha = st.text_input("Confirmar Senha", type="password", key="reg_confirm")

        botao_registro = st.form_submit_button("REGISTRAR")

        if botao_registro:
            if not all([usuario, email, senha, confirmar_senha]):
                st.error("Todos os campos são obrigatórios")
                return

            if senha != confirmar_senha:
                st.error("Senhas não coincidem")
                return

            usuarios = load_data(USERS_FILE, [])

            if any(u["email"].lower() == email.lower() for u in usuarios):
                st.error("Email já cadastrado")
                return

            if any(u["username"].lower() == usuario.lower() for u in usuarios):
                st.error("Nome de usuário já em uso")
                return

            novo_usuario = {
                "user_id": len(usuarios) + 1,
                "username": usuario,
                "email": email.lower(),
                "password": senha,
                "tasks": []
            }

            usuarios.append(novo_usuario)
            save_data(USERS_FILE, usuarios)

            st.success("Registro bem-sucedido! Faça login.")
            st.session_state.current_screen = "login"
            st.rerun()

    if st.button("Já tem conta ? Faça login"):
        st.session_state.current_screen = "login"
        st.rerun()

def mostrar_menu_navegacao():
    """Mostrar menu de navegação no topo"""
    # Criar container para o menu
    with st.container():
        # Criar colunas para posicionamento do menu
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.write(f"Olá, **{st.session_state.current_user.get('username', 'Usuário')}**! 👋")
        
        # Avatar do perfil
        with col3:
            avatar_initial = st.session_state.current_user.get("username", "U")
            if st.button(f"👤 {avatar_initial}", key="profile_avatar", help="Perfil"):
                st.session_state.show_profile = True
                st.session_state.menu_open = False
                st.rerun()
        
        # Menu com 3 pontos
        with col4:
            if st.button("≡", key="menu_button", help="Menu"):
                st.session_state.menu_open = not st.session_state.menu_open
                st.rerun()
    
    # Dropdown do menu
    if st.session_state.menu_open:
        with st.expander("Menu", expanded=True):
            col_menu = st.columns(1)[0]
            with col_menu:
                if st.button("➕ Nova Tarefa", key="menu_new_task", use_container_width=True):
                    st.session_state.show_task_form = True
                    st.session_state.task_to_edit = None
                    st.session_state.menu_open = False
                    st.rerun()
                
                if st.button("⚙️ Configurações", key="menu_settings", use_container_width=True):
                    st.session_state.show_settings = True
                    st.session_state.menu_open = False
                    st.rerun()
                
                if st.button("🔔 Verificar Notificações", key="menu_notifications", use_container_width=True):
                    notificacoes = verificar_notificacoes()
                    if notificacoes:
                        for notif in notificacoes:
                            mostrar_notificacao_popup(notif)
                        salvar_dados_usuario()
                        st.success(f"{len(notificacoes)} notificação(ões) encontrada(s)!")
                    else:
                        st.info("Nenhuma notificação pendente.")
                    st.session_state.menu_open = False
                    st.rerun()
                
                if st.button("🚪 Sair", key="menu_logout", use_container_width=True):
                    st.session_state.current_user = None
                    if os.path.exists(SESSION_FILE):
                        os.remove(SESSION_FILE)
                    st.session_state.current_screen = "login"
                    st.session_state.menu_open = False
                    st.rerun()

def tela_perfil():
    """Exibir página de configurações do perfil"""
    st.title("👤 Perfil do Usuário")
    
    user = st.session_state.current_user
    
    with st.form("profile_form"):
        st.subheader("Informações Básicas")
        
        novo_username = st.text_input(
            "Nome de Usuário", 
            value=user.get("username", ""),
            help="Digite o novo nome de usuário"
        )
        
        # Mostrar email (apenas leitura)
        st.text_input(
            "Email", 
            value=user.get("email", ""),
            disabled=True,
            help="Email não pode ser alterado"
        )
        
        # Estatísticas do usuário
        st.subheader("📊 Estatísticas")
        total_tasks = len(user.get("tasks", []))
        completed_tasks = len([t for t in user.get("tasks", []) if t.get("completed", False)])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Tarefas", total_tasks)
        with col2:
            st.metric("Concluídas", completed_tasks)
        with col3:
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.metric("Taxa de Conclusão", f"{completion_rate:.1f}%")
        
        # Botões de ação
        col_save, col_back = st.columns(2)
        
        with col_save:
            salvar_perfil = st.form_submit_button("💾 Salvar Alterações")
        
        with col_back:
            voltar = st.form_submit_button("← Voltar")
        
        if salvar_perfil:
            novo_username_clean = novo_username.strip() if novo_username else ""
            if novo_username_clean:
                # Verificar se o novo username já existe
                usuarios = load_data(USERS_FILE, [])
                username_existe = any(
                    u.get("username", "").lower() == novo_username_clean.lower() and 
                    u["email"] != user["email"] 
                    for u in usuarios
                )
                
                if username_existe:
                    st.error("Nome de usuário já está em uso!")
                else:
                    # Atualizar username
                    st.session_state.current_user["username"] = novo_username_clean
                    
                    # Salvar no arquivo
                    for idx, u in enumerate(usuarios):
                        if u["email"] == user["email"]:
                            usuarios[idx] = st.session_state.current_user
                            break
                    
                    save_data(USERS_FILE, usuarios)
                    st.success("Perfil atualizado com sucesso!")
                    st.rerun()
            else:
                st.error("Nome de usuário não pode estar vazio!")
        
        if voltar:
            st.session_state.show_profile = False
            st.rerun()

    # Delete Account Section - Outside the form
    st.markdown("---")
    st.subheader("Excluir Conta")
    
    if st.button("🗑️ Deletar Conta Permanentemente", type="secondary", use_container_width=True):
        # Show confirmation dialog
        @st.dialog("Confirmar Exclusão de Conta")
        def confirm_delete_account():
            st.warning("⚠️ **ATENÇÃO!**")
            st.write("Sua conta será excluída permanentemente, você tem certeza de que deseja continuar com esta ação ?")
            st.write("Esta ação **NÃO PODE** ser desfeita!")
            st.write("- Todas as suas tarefas serão perdidas")
            st.write("- Seu perfil será completamente removido")
            st.write("- Você não poderá recuperar estes dados")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("🗑️ Sim, Deletar Conta", type="primary", use_container_width=True):
                    delete_user_account()
                    st.rerun()
        
        confirm_delete_account()

def delete_user_account():
    """Permanently delete the current user's account"""
    if not st.session_state.current_user:
        return
    
    current_email = st.session_state.current_user["email"]
    
    # Load users data
    usuarios = load_data(USERS_FILE, [])
    
    # Remove the current user from the list
    usuarios = [u for u in usuarios if u["email"] != current_email]
    
    # Save updated users list
    save_data(USERS_FILE, usuarios)
    
    # Clear session
    st.session_state.current_user = None
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    
    # Redirect to login
    st.session_state.current_screen = "login"
    st.session_state.show_profile = False
    
    st.success("Conta deletada com sucesso. Você será redirecionado para a tela de login.")
    st.rerun()

def tela_tarefas():
    """Exibir lista de tarefas"""
    # Mostrar menu de navegação
    mostrar_menu_navegacao()
    
    st.markdown("---")
    st.title("📋 Minhas Tarefas")

    if not st.session_state.current_user or "tasks" not in st.session_state.current_user:
        st.info("Nenhuma tarefa encontrada. Adicione sua primeira!")
        return

    tarefas = sorted(st.session_state.current_user["tasks"], key=lambda t: t.get("due_date", "99:99"))

    if not tarefas:
        st.info("Nenhuma tarefa encontrada. Adicione sua primeira!")
        return

    for idx, tarefa in enumerate(tarefas):
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 3, 1, 0.5])
            with col1:
                concluida = st.checkbox("Concluída", value=tarefa.get("completed", False), key=f"task_complete_{idx}", label_visibility="collapsed")
                if concluida != tarefa.get("completed", False):
                    tarefa["completed"] = concluida
                    salvar_dados_usuario()
                    st.rerun()
            with col2:
                classe = "task-completed" if tarefa.get("completed") else "task-pending"
                texto = f"**{tarefa.get('title', '')}**"
                if tarefa.get('description'):
                    texto += f"\n{tarefa.get('description')}"
                if tarefa.get('due_date'):
                    texto += f"\n⏰ {tarefa.get('due_date')}"
                if tarefa.get('type') == 'daily':
                    texto += " 🔄"
                st.markdown(f'<div class="task-item {classe}">{texto}</div>', unsafe_allow_html=True)
            with col3:
                if st.button("✏️", key=f"edit_{idx}"):
                    st.session_state.task_to_edit = tarefa
                    st.session_state.show_task_form = True
                    st.rerun()
            with col4:
                if st.button("🗑️", key=f"delete_{idx}", help="Excluir tarefa"):
                    st.session_state.current_user["tasks"].remove(tarefa)
                    salvar_dados_usuario()
                    st.success("Tarefa excluída!")
                    st.rerun()

def mostrar_dialogo_tarefa():
    """Exibir formulário de criação/edição de tarefa"""
    st.subheader("➕ Adicionar/Editar Tarefa")
    tarefa = st.session_state.task_to_edit or {}
    with st.form("task_form"):
        titulo = st.text_input("Título", value=tarefa.get("title", ""))
        descricao = st.text_area("Descrição (opcional)", value=tarefa.get("description", ""))
        horario = st.text_input("Horário (HH:MM)", value=tarefa.get("due_date", ""), help="Ex: 14:30 para 2:30 PM")
        diaria = st.checkbox("Tarefa Diária", value=tarefa.get("type") == "daily")
        col1, col2 = st.columns(2)
        with col1:
            salvar = st.form_submit_button("💾 Salvar")
        with col2:
            cancelar = st.form_submit_button("❌ Cancelar")
        if salvar:
            titulo_clean = titulo.strip() if titulo else ""
            if not titulo_clean:
                st.error("Título obrigatório")
                return
            if horario and not validar_horario(horario):
                st.error("Formato inválido. Use HH:MM (ex: 14:30)")
                return
            dados_tarefa = {
                "title": titulo_clean,
                "description": descricao.strip() if descricao else "",
                "due_date": horario.strip() if horario else "",
                "type": "daily" if diaria else "single",
                "completed": tarefa.get("completed", False)
            }
            if st.session_state.task_to_edit:
                # Find the task index and update it
                task_found = False
                for i, t in enumerate(st.session_state.current_user["tasks"]):
                    if (t.get("title") == st.session_state.task_to_edit.get("title") and 
                        t.get("description") == st.session_state.task_to_edit.get("description") and
                        t.get("due_date") == st.session_state.task_to_edit.get("due_date")):
                        st.session_state.current_user["tasks"][i] = dados_tarefa
                        task_found = True
                        break
                if not task_found:
                    st.error("Erro: não foi possível encontrar a tarefa para editar")
                    return
            else:
                st.session_state.current_user["tasks"].append(dados_tarefa)
            salvar_dados_usuario()
            st.session_state.task_to_edit = None
            st.session_state.show_task_form = False
            st.success("Tarefa salva com sucesso!")
            st.rerun()
        if cancelar:
            st.session_state.task_to_edit = None
            st.session_state.show_task_form = False
            st.rerun()


def salvar_dados_usuario():
    """Salvar dados atuais do usuário"""
    usuarios = load_data(USERS_FILE, [])
    for idx, u in enumerate(usuarios):
        if u["email"] == st.session_state.current_user["email"]:
            usuarios[idx] = st.session_state.current_user
            break
    save_data(USERS_FILE, usuarios)

def tela_configuracoes():
    """Exibir tela de configurações"""
    st.title("⚙️ Configurações")
    
    with st.container():
        st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
        
        st.subheader("🎨 Personalização do Tema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            primary_color = st.color_picker(
                "Cor Principal", 
                value=st.session_state.theme_settings["primary_color"],
                key="primary_color_picker"
            )
            
            background_color = st.color_picker(
                "Cor de Fundo", 
                value=st.session_state.theme_settings["background_color"],
                key="bg_color_picker"
            )
            
            secondary_color = st.color_picker(
                "Cor Secundária", 
                value=st.session_state.theme_settings["secondary_color"],
                key="sec_color_picker"
            )
            
            text_color = st.color_picker(
                "Cor do Texto", 
                value=st.session_state.theme_settings["text_color"],
                key="text_color_picker"
            )
        
        with col2:
            success_color = st.color_picker(
                "Cor de Sucesso", 
                value=st.session_state.theme_settings["success_color"],
                key="success_color_picker"
            )
            
            warning_color = st.color_picker(
                "Cor de Aviso", 
                value=st.session_state.theme_settings["warning_color"],
                key="warning_color_picker"
            )
            
            error_color = st.color_picker(
                "Cor de Erro", 
                value=st.session_state.theme_settings["error_color"],
                key="error_color_picker"
            )
        
        st.markdown("---")
        
        # Cores customizadas com entrada manual
        st.subheader("🖌️ Cores Customizadas (Hex/RGB)")
        
        col_custom1, col_custom2 = st.columns(2)
        with col_custom1:
            custom_hex = st.text_input("Código Hex (ex: #FF5733)", placeholder="#FF5733")
            if custom_hex and custom_hex.startswith("#") and len(custom_hex) == 7:
                st.color_picker("Preview Hex", value=custom_hex, disabled=True)
        
        with col_custom2:
            rgb_r = st.number_input("Vermelho (0-255)", 0, 255, value=74)
            rgb_g = st.number_input("Verde (0-255)", 0, 255, value=144)
            rgb_b = st.number_input("Azul (0-255)", 0, 255, value=226)
            rgb_hex = f"#{rgb_r:02x}{rgb_g:02x}{rgb_b:02x}"
            st.color_picker("Preview RGB", value=rgb_hex, disabled=True)
        
        st.markdown("---")
        
        col_save, col_reset, col_back = st.columns(3)
        
        with col_save:
            if st.button("💾 Salvar Configurações"):
                # Atualizar configurações do tema
                st.session_state.theme_settings = {
                    "primary_color": primary_color,
                    "background_color": background_color,
                    "secondary_color": secondary_color,
                    "text_color": text_color,
                    "success_color": success_color,
                    "warning_color": warning_color,
                    "error_color": error_color
                }
                
                # Salvar tema no perfil do usuário
                st.session_state.current_user["theme_settings"] = st.session_state.theme_settings
                salvar_dados_usuario()
                
                st.success("Configurações salvas com sucesso!")
                st.rerun()
        
        with col_reset:
            if st.button("🔄 Restaurar Padrão"):
                st.session_state.theme_settings = {
                    "primary_color": "#FFD6BA",
                    "background_color": "#FFF8F4", 
                    "secondary_color": "#A1C3D1",
                    "text_color": "#333333",
                    "success_color": "#A8D5BA",
                    "warning_color": "#FFE7A0",
                    "error_color": "#F4A6A6"
                }
                st.session_state.current_user["theme_settings"] = st.session_state.theme_settings
                salvar_dados_usuario()
                st.success("Tema restaurado para o padrão!")
                st.rerun()
        
        with col_back:
            if st.button("← Voltar"):
                st.session_state.show_settings = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def validar_horario(hora):
    """Valida formato HH:MM"""
    try:
        partes = hora.split(":")
        if len(partes) != 2:
            return False
        h, m = int(partes[0]), int(partes[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except ValueError:
        return False

def main():
    # Verificar sessão no startup
    if st.session_state.current_user is None and st.session_state.current_screen == "login":
        if verificar_sessao():
            st.rerun()
    
    # Verificar notificações automaticamente se usuário logado
    if st.session_state.current_user:
        notificacoes = verificar_notificacoes()
        if notificacoes:
            for notif in notificacoes:
                mostrar_notificacao_popup(notif)
            salvar_dados_usuario()
    
    # Navegação principal
    if st.session_state.current_screen == "login":
        tela_login()
    elif st.session_state.current_screen == "register":
        tela_registro()
    elif st.session_state.current_screen == "task_list":
        if st.session_state.current_user:
            # Verificar se deve mostrar perfil
            if st.session_state.show_profile:
                tela_perfil()
            # Verificar se deve mostrar configurações
            elif st.session_state.show_settings:
                tela_configuracoes()
            # Verificar se deve mostrar formulário de tarefa
            elif st.session_state.show_task_form:
                mostrar_dialogo_tarefa()
            # Mostrar lista de tarefas
            else:
                tela_tarefas()
        else:
            st.session_state.current_screen = "login"
            st.rerun()

if __name__ == "__main__":
    main()
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
        "primary_color": "#4A90E2",
        "background_color": "#FFFFFF", 
        "secondary_color": "#F0F4F8",
        "text_color": "#333333",
        "success_color": "#28A745",
        "warning_color": "#FFC107",
        "error_color": "#DC3545"
    }
    st.session_state.theme_settings = load_data(SETTINGS_FILE, {"theme": default_theme}).get("theme", default_theme)
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

def verificar_sessao():
    """Verifica se existe sessão ativa"""
    sessao = load_data(SESSION_FILE, {})
    email = sessao.get("active_user_email")
    if email:
        usuarios = load_data(USERS_FILE, [])
        usuario = next((u for u in usuarios if u["email"] == email), None)
        if usuario:
            st.session_state.current_user = usuario
            st.session_state.current_screen = "task_list"
            return True
    return False

def tela_login():
    """Exibir tela de login"""
    st.title("🧠 NeuroTask")
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
                if lembrar:
                    save_data(SESSION_FILE, {"active_user_email": usuario["email"]})
                st.session_state.current_screen = "task_list"
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")

    if st.button("Não tem conta? Registre-se"):
        st.session_state.current_screen = "register"
        st.rerun()

def tela_registro():
    """Exibir tela de registro"""
    st.title("🧠 NeuroTask")
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

    if st.button("Já tem conta? Faça login"):
        st.session_state.current_screen = "login"
        st.rerun()

def tela_tarefas():
    """Exibir lista de tarefas"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📋 Minhas Tarefas")
    with col2:
        if st.button("Sair"):
            st.session_state.current_user = None
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            st.session_state.current_screen = "login"
            st.rerun()

    # Botões de navegação
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("➕ Nova Tarefa"):
            st.session_state.show_task_form = True
            st.session_state.task_to_edit = None
            st.rerun()
    with col_btn2:
        if st.button("⚙️ Configurações"):
            st.session_state.show_settings = True
            st.rerun()
    with col_btn3:
        if st.button("🔔 Verificar Notificações"):
            notificacoes = verificar_notificacoes()
            if notificacoes:
                for notif in notificacoes:
                    mostrar_notificacao_popup(notif)
                salvar_dados_usuario()
            else:
                st.info("Nenhuma notificação pendente.")
            st.rerun()

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
                concluida = st.checkbox("", value=tarefa.get("completed", False), key=f"task_complete_{idx}")
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
                if st.button("🗑️", key=f"delete_{idx}"):
                    confirmar_exclusao(tarefa, idx)
                    return

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
                for i, t in enumerate(st.session_state.current_user["tasks"]):
                    if t == st.session_state.task_to_edit:
                        st.session_state.current_user["tasks"][i] = dados_tarefa
                        break
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

def confirmar_exclusao(tarefa, idx):
    """Confirmação de exclusão"""
    st.subheader("⚠️ Confirmar Exclusão")
    st.warning(f"Tem certeza que deseja excluir '{tarefa.get('title')}'?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Sim, excluir"):
            st.session_state.current_user["tasks"].remove(tarefa)
            salvar_dados_usuario()
            st.success("Tarefa excluída com sucesso!")
            st.rerun()
    with col2:
        if st.button("❌ Cancelar"):
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
                
                # Salvar no arquivo
                settings_data = {"theme": st.session_state.theme_settings}
                save_data(SETTINGS_FILE, settings_data)
                
                st.success("Configurações salvas com sucesso!")
                st.rerun()
        
        with col_reset:
            if st.button("🔄 Restaurar Padrão"):
                st.session_state.theme_settings = {
                    "primary_color": "#4A90E2",
                    "background_color": "#FFFFFF", 
                    "secondary_color": "#F0F4F8",
                    "text_color": "#333333",
                    "success_color": "#28A745",
                    "warning_color": "#FFC107",
                    "error_color": "#DC3545"
                }
                save_data(SETTINGS_FILE, {"theme": st.session_state.theme_settings})
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
            # Verificar se deve mostrar configurações
            if st.session_state.show_settings:
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

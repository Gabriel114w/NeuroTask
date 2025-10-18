import streamlit as st
from datetime import datetime
from utils import (
    get_tasks,
    add_task,
    update_task,
    delete_task,
    get_user_by_email,
)
from supabase_client import sign_in_user, sign_up_user

# ---------------------------------------------------------
# Configuração inicial
# ---------------------------------------------------------
st.set_page_config(page_title="Tarefas", layout="wide")

# ---------------------------------------------------------
# Tema CSS com cores suaves (pastel)
# ---------------------------------------------------------
def apply_theme_css():
    st.markdown(
        f"""
        <style>
        .priority-high {{
            background: rgba(239,154,154,0.35); /* vermelho suave */
            color: #7a1f1f;
            border: 1px solid rgba(239,154,154,0.6);
            padding: 4px 8px;
            border-radius: 8px;
        }}
        .priority-medium {{
            background: rgba(255,224,130,0.35); /* amarelo suave */
            color: #7a5a00;
            border: 1px solid rgba(255,224,130,0.6);
            padding: 4px 8px;
            border-radius: 8px;
        }}
        .priority-low {{
            background: rgba(165,214,167,0.35); /* verde suave */
            color: #1b5e20;
            border: 1px solid rgba(165,214,167,0.6);
            padding: 4px 8px;
            border-radius: 8px;
        }}
        .task-card {{
            border: 1px solid #ccc;
            border-radius: 12px;
            padding: 10px 16px;
            margin-bottom: 10px;
            background-color: white;
        }}
        .completed {{
            opacity: 0.6;
            text-decoration: line-through;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Inicialização do estado da sessão
# ---------------------------------------------------------
def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "tasks_filter" not in st.session_state:
        st.session_state.tasks_filter = "all"
    if "tasks_sort" not in st.session_state:
        st.session_state.tasks_sort = "created_at"
    if "tasks_search" not in st.session_state:
        st.session_state.tasks_search = ""


# ---------------------------------------------------------
# Login / Cadastro
# ---------------------------------------------------------
def login_screen():
    st.title("Entrar no sistema")

    email = st.text_input("E-mail")
    password = st.text_input("Senha", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar"):
            user = sign_in_user(email, password)
            if user:
                st.session_state.user = user
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")
    with col2:
        if st.button("Cadastrar"):
            user = sign_up_user(email, password)
            if user:
                st.session_state.user = user
                st.success("Cadastro realizado com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao cadastrar.")


# ---------------------------------------------------------
# Exibir perfil do usuário
# ---------------------------------------------------------
def mostrar_perfil(user):
    st.sidebar.markdown("### Perfil do Usuário")
    st.sidebar.write(f"**Email:** {user.get('email', 'N/A')}")
    created = user.get("created_at")
    if created:
        try:
            created_fmt = datetime.strptime(created[:19], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y")
        except Exception:
            created_fmt = created[:10]
    else:
        created_fmt = "N/A"
    st.sidebar.markdown(f"**Membro desde:** {created_fmt}")


# ---------------------------------------------------------
# Formulário de criação de tarefa
# ---------------------------------------------------------
def task_form(user_id):
    st.markdown("### Nova Tarefa")

    title = st.text_input("Título da tarefa")
    description = st.text_area("Descrição")
    due_date = st.date_input("Data limite", datetime.now()).strftime("%Y-%m-%d")

    prioridade_map = {"Baixa": "low", "Média": "medium", "Alta": "high"}
    prioridade_escolhida = st.selectbox("Prioridade", list(prioridade_map.keys()), index=1)

    if st.button("Adicionar Tarefa"):
        if not title.strip():
            st.warning("Por favor, insira um título.")
            return
        add_task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=prioridade_map[prioridade_escolhida],
        )
        st.success("Tarefa adicionada com sucesso!")
        st.rerun()


# ---------------------------------------------------------
# Renderizar um card de tarefa
# ---------------------------------------------------------
def render_task_card(tarefa):
    prioridade_pt = {"low": "Baixa", "medium": "Média", "high": "Alta"}
    prioridade_class = f"priority-{tarefa.get('priority', 'medium')}"
    data_fmt = ""
    if tarefa.get("due_date"):
        try:
            data_fmt = datetime.strptime(tarefa["due_date"][:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            data_fmt = tarefa["due_date"]

    concluida = tarefa.get("completed", False)
    classe_completada = "completed" if concluida else ""

    with st.container():
        st.markdown(
            f"""
            <div class="task-card {classe_completada}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>{tarefa['title']}</strong><br>
                        <small>{tarefa.get('description','')}</small><br>
                        <small>Data limite: {data_fmt or 'Sem data'}</small>
                    </div>
                    <span class="{prioridade_class}">{prioridade_pt.get(tarefa.get('priority','medium'),'Média')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            marcado = st.checkbox("Concluída", value=concluida, key=f"chk_{tarefa['id']}")
            if marcado != tarefa.get("completed", False):
                update_task(tarefa["id"], {"completed": marcado})
                tarefa["completed"] = marcado  # atualização local sem sumir
        with col2:
            if st.button("Excluir", key=f"del_{tarefa['id']}"):
                delete_task(tarefa["id"])
                st.rerun()


# ---------------------------------------------------------
# Tela principal (Dashboard)
# ---------------------------------------------------------
def dashboard_screen(user):
    apply_theme_css()
    st.title("Minhas Tarefas")

    mostrar_perfil(user)

    all_tasks = get_tasks(user["id"])

    # Toggle para exibir tarefas concluídas
    show_completed = st.checkbox("Mostrar tarefas concluídas", value=False)
    if show_completed:
        filtered_tasks = all_tasks[:]
    else:
        filtered_tasks = [t for t in all_tasks if not t.get("completed", False)]

    # ----------------------------
    # Filtros
    # ----------------------------
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    priority_options_pt = ["Todas", "Baixa", "Média", "Alta"]
    priority_map_en = {"Baixa": "low", "Média": "medium", "Alta": "high", "Todas": "all"}
    current_filter_pt = "Todas" if st.session_state.tasks_filter == "all" else {
        "low": "Baixa",
        "medium": "Média",
        "high": "Alta",
    }.get(st.session_state.tasks_filter, "Todas")

    selected_priority_pt = col_filter1.selectbox(
        "Filtrar por Prioridade", priority_options_pt, index=priority_options_pt.index(current_filter_pt)
    )
    st.session_state.tasks_filter = priority_map_en[selected_priority_pt]

    sort_options = {
        "priority": "Prioridade (Alta primeiro)",
        "created_at": "Criação (Mais antiga primeiro)",
        "due_date": "Data Limite (Mais próxima primeiro)",
    }
    selected_sort_pt = col_filter2.selectbox(
        "Ordenar por",
        list(sort_options.values()),
        index=list(sort_options.keys()).index(st.session_state.tasks_sort),
    )
    st.session_state.tasks_sort = [k for k, v in sort_options.items() if v == selected_sort_pt][0]

    st.session_state.tasks_search = col_filter3.text_input(
        "Pesquisar por título ou descrição", value=st.session_state.tasks_search
    )

    # ----------------------------
    # Aplicar filtros
    # ----------------------------
    if st.session_state.tasks_filter != "all":
        filtered_tasks = [t for t in filtered_tasks if t.get("priority") == st.session_state.tasks_filter]

    # Pesquisa textual
    if st.session_state.tasks_search:
        txt = st.session_state.tasks_search.lower()
        filtered_tasks = [
            t for t in filtered_tasks if txt in t.get("title", "").lower() or txt in t.get("description", "").lower()
        ]

    # Ordenação
    if st.session_state.tasks_sort == "priority":
        order = {"high": 1, "medium": 2, "low": 3}
        filtered_tasks.sort(key=lambda x: order.get(x.get("priority", "medium")))
    elif st.session_state.tasks_sort == "created_at":
        filtered_tasks.sort(key=lambda x: x.get("created_at", ""))
    elif st.session_state.tasks_sort == "due_date":
        filtered_tasks.sort(key=lambda x: x.get("due_date") or "")

    st.divider()
    st.markdown("### Lista de Tarefas")

    if not filtered_tasks:
        st.info("Nenhuma tarefa encontrada.")
    else:
        for tarefa in filtered_tasks:
            render_task_card(tarefa)

    st.divider()
    task_form(user["id"])


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    init_session_state()
    user = st.session_state.user

    if not user:
        login_screen()
    else:
        dashboard_screen(user)


if __name__ == "__main__":
    main()

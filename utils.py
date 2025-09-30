import streamlit as st
from datetime import datetime

def validar_horario(hora):
    try:
        partes = hora.split(":")
        if len(partes) != 2:
            return False
        h, m = int(partes[0]), int(partes[1])
        return 0 <= h <= 23 and 0 <= m <= 59
    except ValueError:
        return False

def aplicar_css(theme):
    st.markdown(f"""
    <style>
        .main > div {{ padding-top:2rem; background-color:{theme['background_color']}; color:{theme['text_color']}; }}
        .stButton > button {{ width:100%; background-color:{theme['primary_color']}; color:white; border:none; border-radius:5px; }}
        .stButton > button:hover {{ background-color:{theme['secondary_color']}; color:{theme['text_color']}; }}
        .task-item {{ padding:10px; margin:5px 0; border-radius:5px; border:1px solid #ddd; background-color:{theme['background_color']}; color:{theme['text_color']}; }}
        .task-completed {{ background-color:{theme['success_color']}33; opacity:0.7; }}
        .task-pending {{ background-color:{theme['warning_color']}33; }}
        h1,h2,h3 {{ color:{theme['primary_color']}; text-align:center; }}
        .notification-popup {{ position: fixed; top: 20px; right: 20px; background-color: {theme['warning_color']}; color: white; padding: 15px; border-radius: 10px; z-index:9999; max-width:300px; animation: slideIn 0.5s ease-out; }}
        @keyframes slideIn {{ from {{ transform: translateX(100%); opacity:0; }} to {{ transform: translateX(0); opacity:1; }} }}
        .settings-panel {{ background-color:{theme['secondary_color']}; padding:20px; border-radius:10px; border:1px solid {theme['primary_color']}; }}
    </style>
    """, unsafe_allow_html=True)

def verificar_notificacoes(tarefas, last_check_date):
    agora = datetime.now()
    hora_atual = agora.strftime("%H:%M")
    notificacoes = []
    for t in tarefas:
        if t.get("due_date") == hora_atual and not t.get("completed", False) and not t.get("notified_today", False):
            t["notified_today"] = True
            notificacoes.append({"title": t.get("title"), "description": t.get("description") or "Hora de começar!"})
    # Reset daily notifications
    if agora.date() != last_check_date:
        last_check_date = agora.date()
        for t in tarefas:
            t.pop("notified_today", None)
    return notificacoes, last_check_date

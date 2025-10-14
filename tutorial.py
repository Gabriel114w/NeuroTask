import streamlit as st

def tutorial_step(step_number, title, content, image_path=None):
    """Renderiza um passo do tutorial."""
    st.markdown(f"### Passo {step_number}: {title}")
    st.markdown(content)
    if image_path:
        st.image(image_path, use_column_width=True)
    st.markdown("---")

def mostrar_tutorial():
    """Exibe o tutorial interativo para usuários com TDAH."""
    st.markdown('<div class="page-header">Guia de Foco Rápido (Para Mentes Brilhantes)</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Este guia foi feito para você. Vamos direto ao ponto!</div>', unsafe_allow_html=True)

    st.warning("🚨 **Lembrete Rápido:** Não se sinta obrigado(a) a ler tudo de uma vez. Salve este guia e volte quando precisar de um 're-foco'!")
    
    st.markdown("## 1. O Painel (Dashboard)")
    tutorial_step(
        1,
        "Visão Geral Rápida",
        "O painel inicial mostra apenas as **Tarefas Pendentes**. Tarefas concluídas saem da sua frente para reduzir a sobrecarga visual. Se precisar vê-las, use o menu lateral 'Tarefas Concluídas'."
    )
    
    st.markdown("## 2. Cores e Prioridades (Sem Ansiedade)")
    tutorial_step(
        2,
        "O Código de Cores Suave",
        "Usamos cores pastéis e suaves para prioridades. Elas são um **sinal**, não um alarme de incêndio. \n\n"
        "- 🟢 **Baixa (Verde Suave):** Coisas que podem esperar. Faça quando estiver com energia extra.\n"
        "- 🟡 **Média (Amarelo Suave):** Importante, mas não urgente. Tente encaixar no seu dia.\n"
        "- 🔴 **Alta (Vermelho Suave):** Urgente ou muito importante. Tente começar esta primeiro, mas lembre-se: **pequenos passos**."
    )
    
    st.markdown("## 3. Adicionando e Editando Tarefas")
    tutorial_step(
        3,
        "O Mínimo Essencial",
        "Ao criar uma tarefa, o **Título** é o mais importante. Mantenha-o curto e acionável (ex: 'Ligar para o banco', não 'Resolver problema do banco'). A **Descrição** é opcional, use-a para quebrar a tarefa em 1-3 sub-passos se a tarefa for grande."
    )
    
    st.markdown("## 4. O Filtro Mágico (Foco Instantâneo)")
    tutorial_step(
        4,
        "Use o Filtro para 'Desligar o Ruído'",
        "Na tela principal, use o filtro de **Prioridade** para ver **apenas** as tarefas de prioridade Alta. Isso elimina o resto da lista e permite que você se concentre em uma coisa de cada vez. Quando terminar, volte para 'Todas' ou filtre por Média."
    )
    
    st.markdown("## 5. Conclusão (A Recompensa)")
    tutorial_step(
        5,
        "O Prazer de Concluir",
        "Ao marcar a caixa de seleção, a tarefa é concluída e sai da sua lista principal. Se você a marcou por engano, ela estará na lista de 'Tarefas Concluídas' e pode ser reativada de lá. **Celebre cada conclusão!**"
    )
    
    st.markdown("---")
    st.success("🎉 **Pronto!** Você tem as ferramentas. Agora, respire fundo e escolha seu primeiro pequeno passo.")

if __name__ == '__main__':
    # Exemplo de como seria usado no app principal
    st.set_page_config(layout="wide")
    mostrar_tutorial()

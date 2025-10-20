from supabase_client import supabase
from datetime import datetime

# ---------------------------------------------------------
# Funções utilitárias do Supabase (tarefas e usuários)
# ---------------------------------------------------------

def get_tasks(user_id: str):
    """Busca todas as tarefas de um usuário."""
    if not supabase:
        return []

    try:
        result = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .execute()
        )

        tasks = result.data or []

        # Garantir compatibilidade retroativa
        for task in tasks:
            if "priority" not in task or not task["priority"]:
                task["priority"] = "medium"
            if "completed" not in task:
                task["completed"] = False

        return tasks

    except Exception as e:
        print(f"[get_tasks] Erro: {e}")
        return []


def get_pending_tasks(user_id: str):
    """Busca apenas tarefas não concluídas."""
    all_tasks = get_tasks(user_id)
    return [t for t in all_tasks if not t.get("completed", False)]


def add_task(
    user_id: str,
    title: str,
    description: str = "",
    due_date: str = "",
    type: str = "single",
    priority: str = "medium",
):
    """Adiciona nova tarefa ao banco."""
    if not supabase:
        return None

    try:
        data = {
            "user_id": user_id,
            "title": title.strip(),
            "description": description.strip(),
            "due_date": due_date,
            "type": type,
            "completed": False,
            "priority": priority or "medium",
        }

        result = supabase.table("tasks").insert(data).execute()
        return result.data[0] if result.data else None

    except Exception as e:
        print(f"[add_task] Erro ao adicionar tarefa: {e}")
        return None


def update_task(task_id: str, updates: dict):
    """Atualiza uma tarefa existente."""
    if not supabase:
        return None

    try:
        # Sanitizar dados
        if "title" in updates:
            updates["title"] = updates["title"].strip()
        if "description" in updates:
            updates["description"] = updates["description"].strip()

        result = supabase.table("tasks").update(updates).eq("id", task_id).execute()
        return result.data[0] if result.data else None

    except Exception as e:
        print(f"[update_task] Erro: {e}")
        return None


def delete_task(task_id: str):
    """Remove uma tarefa pelo ID."""
    if not supabase:
        return False

    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
        return True
    except Exception as e:
        print(f"[delete_task] Erro: {e}")
        return False

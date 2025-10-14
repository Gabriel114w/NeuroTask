"""
NeuroTask - Utilities Module
Adaptado para a estrutura real do Supabase
"""
import hashlib
import bcrypt
from supabase import create_client, Client

# =============================
# Supabase Configuration
# =============================
SUPABASE_URL = "https://ngcinsfttwpaxzloexbx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5nY2luc2Z0dHdwYXh6bG9leGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NDI2OTIsImV4cCI6MjA3NTMxODY5Mn0.As8CabSnXkOlaxqR-eMHMMNgMX_Hhuse877KLDva_8M"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Conectado ao Supabase")
except Exception as e:
    print(f"✗ Erro ao conectar ao Supabase: {e}")
    supabase = None

# =============================
# Password Utilities
# =============================
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def hash_password_sha256(password: str) -> str:
    """Legacy SHA256 hash"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password - suporta bcrypt, SHA256 e plaintext"""
    if not stored_hash:
        return False
    
    # Try bcrypt first
    if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            return False
    
    # Try SHA256
    sha256_hash = hash_password_sha256(password)
    if stored_hash == sha256_hash:
        return True
    
    # Plaintext (para compatibilidade com dados existentes)
    if stored_hash == password:
        return True
    
    return False

def migrate_password(user_id: str, email: str, password: str, old_hash: str) -> bool:
    """Migrate old password to bcrypt"""
    try:
        if verify_password(password, old_hash):
            new_hash = hash_password(password)
            update_user(email, {"password": new_hash})
            return True
        return False
    except Exception as e:
        print(f"Erro ao migrar senha: {e}")
        return False

# =============================
# User Management Functions
# =============================
def create_user(username: str, email: str, password: str, theme: str = "light_lavender") -> dict:
    """Create a new user"""
    if not supabase:
        raise Exception("Banco de dados não disponível")
    
    try:
        hashed_password = hash_password(password)
        data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "theme_settings": {"current_theme": theme}
        }
        
        result = supabase.table("users").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        raise

def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def get_user_by_username(username: str) -> dict:
    """Get user by username"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").select("*").eq("username", username).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def update_user(email: str, updates: dict) -> dict:
    """Update user information"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").update(updates).eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        return None

def delete_user(email: str) -> bool:
    """Delete user and all tasks"""
    if not supabase:
        return False
    
    try:
        user = get_user_by_email(email)
        if not user:
            return False
        
        # Delete tasks first
        supabase.table("tasks").delete().eq("user_id", user["id"]).execute()
        
        # Delete user
        supabase.table("users").delete().eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return False

# =============================
# Task Management Functions
# =============================
def get_tasks(user_id: str) -> list:
    """Get all tasks for a user"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
        tasks = result.data or []
        
        # Adicionar priority como 'medium' para compatibilidade com o app
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas: {e}")
        return []

def add_task(user_id: str, title: str, description: str = "", due_date: str = "", 
             type: str = "single", priority: str = "medium") -> dict:
    """Add a new task (priority é ignorado pois não existe no banco)"""
    if not supabase:
        return None
    
    try:
        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "type": type,
            "completed": False
        }
        
        result = supabase.table("tasks").insert(data).execute()
        
        if result.data:
            task = result.data[0]
            # Adicionar priority para compatibilidade
            task['priority'] = priority
            return task
        return None
    except Exception as e:
        print(f"Erro ao adicionar tarefa: {e}")
        return None

def update_task(task_id: str, updates: dict) -> dict:
    """Update a task"""
    if not supabase:
        return None
    
    try:
        # Remover priority dos updates pois não existe no banco
        updates_clean = {k: v for k, v in updates.items() if k != 'priority'}
        
        result = supabase.table("tasks").update(updates_clean).eq("id", task_id).execute()
        
        if result.data:
            task = result.data[0]
            # Adicionar priority para compatibilidade
            if 'priority' not in task:
                task['priority'] = updates.get('priority', 'medium')
            return task
        return None
    except Exception as e:
        print(f"Erro ao atualizar tarefa: {e}")
        return None

def delete_task(task_id: str) -> bool:
    """Delete a task"""
    if not supabase:
        return False
    
    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao deletar tarefa: {e}")
        return False

def get_pending_tasks(user_id: str) -> list:
    """Get pending tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", False).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas pendentes: {e}")
        return []

def get_completed_tasks(user_id: str) -> list:
    """Get completed tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", True).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas concluídas: {e}")
        return []

def get_tasks_by_priority(user_id: str, priority: str) -> list:
    """Get tasks by priority (retorna todas pois não há coluna priority)"""
    return get_tasks(user_id)

def get_daily_tasks(user_id: str) -> list:
    """Get daily tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("type", "daily").execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas diárias: {e}")
        return []

# =============================
# Notification Functions
# =============================
def send_task_notification(title: str, description: str = "", app_context=None) -> None:
    """Send notification (log only)"""
    print(f"🔔 Notificação: {title}")
    if description:
        print(f"   {description}")

def get_due_tasks(user_id: str) -> list:
    """Get tasks due now"""
    if not supabase:
        return []
    
    try:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("due_date", current_time).eq("completed", False).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas vencidas: {e}")
        return []

# =============================
# Analytics Functions  
# =============================
def get_user_analytics(user_id: str) -> dict:
    """Get user analytics"""
    try:
        tasks = get_tasks(user_id)
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("completed", False)])
        pending_tasks = total_tasks - completed_tasks
        
        priority_stats = {
            "high": len([t for t in tasks if t.get("priority") == "high"]),
            "medium": len([t for t in tasks if t.get("priority") == "medium"]), 
            "low": len([t for t in tasks if t.get("priority") == "low"])
        }
        
        task_types = {
            "daily": len([t for t in tasks if t.get("type") == "daily"]),
            "single": len([t for t in tasks if t.get("type") == "single"])
        }
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "priority_breakdown": priority_stats,
            "task_types": task_types,
            "average_tasks_per_day": total_tasks / 30 if total_tasks > 0 else 0
        }
    except Exception as e:
        print(f"Erro ao buscar analytics: {e}")
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_rate": 0,
            "priority_breakdown": {"high": 0, "medium": 0, "low": 0},
            "task_types": {"daily": 0, "single": 0},
            "average_tasks_per_day": 0
        }

# =============================
# Database Health Check
# =============================
def test_connection() -> bool:
    """Test database connection"""
    try:
        if not supabase:
            return False
        
        result = supabase.table("users").select("count", count="exact").execute()
        return True
    except Exception as e:
        print(f"Teste de conexão falhou: {e}")
        return False"""
NeuroTask - Utilities Module
Adaptado para a estrutura real do Supabase
"""
import hashlib
import bcrypt
from supabase import create_client, Client

# =============================
# Supabase Configuration
# =============================
SUPABASE_URL = "https://ngcinsfttwpaxzloexbx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5nY2luc2Z0dHdwYXh6bG9leGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NDI2OTIsImV4cCI6MjA3NTMxODY5Mn0.As8CabSnXkOlaxqR-eMHMMNgMX_Hhuse877KLDva_8M"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Conectado ao Supabase")
except Exception as e:
    print(f"✗ Erro ao conectar ao Supabase: {e}")
    supabase = None

# =============================
# Password Utilities
# =============================
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def hash_password_sha256(password: str) -> str:
    """Legacy SHA256 hash"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password - suporta bcrypt, SHA256 e plaintext"""
    if not stored_hash:
        return False
    
    # Try bcrypt first
    if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            return False
    
    # Try SHA256
    sha256_hash = hash_password_sha256(password)
    if stored_hash == sha256_hash:
        return True
    
    # Plaintext (para compatibilidade com dados existentes)
    if stored_hash == password:
        return True
    
    return False

def migrate_password(user_id: str, email: str, password: str, old_hash: str) -> bool:
    """Migrate old password to bcrypt"""
    try:
        if verify_password(password, old_hash):
            new_hash = hash_password(password)
            update_user(email, {"password": new_hash})
            return True
        return False
    except Exception as e:
        print(f"Erro ao migrar senha: {e}")
        return False

# =============================
# User Management Functions
# =============================
def create_user(username: str, email: str, password: str, theme: str = "light_lavender") -> dict:
    """Create a new user"""
    if not supabase:
        raise Exception("Banco de dados não disponível")
    
    try:
        hashed_password = hash_password(password)
        data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "theme_settings": {"current_theme": theme}
        }
        
        result = supabase.table("users").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        raise

def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def get_user_by_username(username: str) -> dict:
    """Get user by username"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").select("*").eq("username", username).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def update_user(email: str, updates: dict) -> dict:
    """Update user information"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").update(updates).eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        return None

def delete_user(email: str) -> bool:
    """Delete user and all tasks"""
    if not supabase:
        return False
    
    try:
        user = get_user_by_email(email)
        if not user:
            return False
        
        # Delete tasks first
        supabase.table("tasks").delete().eq("user_id", user["id"]).execute()
        
        # Delete user
        supabase.table("users").delete().eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return False

# =============================
# Task Management Functions
# =============================
def get_tasks(user_id: str) -> list:
    """Get all tasks for a user"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
        tasks = result.data or []
        
        # Adicionar priority como 'medium' para compatibilidade com o app
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas: {e}")
        return []

def add_task(user_id: str, title: str, description: str = "", due_date: str = "", 
             type: str = "single", priority: str = "medium") -> dict:
    """Add a new task (priority é ignorado pois não existe no banco)"""
    if not supabase:
        return None
    
    try:
        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "type": type,
            "completed": False
        }
        
        result = supabase.table("tasks").insert(data).execute()
        
        if result.data:
            task = result.data[0]
            # Adicionar priority para compatibilidade
            task['priority'] = priority
            return task
        return None
    except Exception as e:
        print(f"Erro ao adicionar tarefa: {e}")
        return None

def update_task(task_id: str, updates: dict) -> dict:
    """Update a task"""
    if not supabase:
        return None
    
    try:
        # Remover priority dos updates pois não existe no banco
        updates_clean = {k: v for k, v in updates.items() if k != 'priority'}
        
        result = supabase.table("tasks").update(updates_clean).eq("id", task_id).execute()
        
        if result.data:
            task = result.data[0]
            # Adicionar priority para compatibilidade
            if 'priority' not in task:
                task['priority'] = updates.get('priority', 'medium')
            return task
        return None
    except Exception as e:
        print(f"Erro ao atualizar tarefa: {e}")
        return None

def delete_task(task_id: str) -> bool:
    """Delete a task"""
    if not supabase:
        return False
    
    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao deletar tarefa: {e}")
        return False

def get_pending_tasks(user_id: str) -> list:
    """Get pending tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", False).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas pendentes: {e}")
        return []

def get_completed_tasks(user_id: str) -> list:
    """Get completed tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", True).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas concluídas: {e}")
        return []

def get_tasks_by_priority(user_id: str, priority: str) -> list:
    """Get tasks by priority (retorna todas pois não há coluna priority)"""
    return get_tasks(user_id)

def get_daily_tasks(user_id: str) -> list:
    """Get daily tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("type", "daily").execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas diárias: {e}")
        return []

# =============================
# Notification Functions
# =============================
def send_task_notification(title: str, description: str = "", app_context=None) -> None:
    """Send notification (log only)"""
    print(f"🔔 Notificação: {title}")
    if description:
        print(f"   {description}")

def get_due_tasks(user_id: str) -> list:
    """Get tasks due now"""
    if not supabase:
        return []
    
    try:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("due_date", current_time).eq("completed", False).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas vencidas: {e}")
        return []

# =============================
# Analytics Functions  
# =============================
def get_user_analytics(user_id: str) -> dict:
    """Get user analytics"""
    try:
        tasks = get_tasks(user_id)
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("completed", False)])
        pending_tasks = total_tasks - completed_tasks
        
        priority_stats = {
            "high": len([t for t in tasks if t.get("priority") == "high"]),
            "medium": len([t for t in tasks if t.get("priority") == "medium"]), 
            "low": len([t for t in tasks if t.get("priority") == "low"])
        }
        
        task_types = {
            "daily": len([t for t in tasks if t.get("type") == "daily"]),
            "single": len([t for t in tasks if t.get("type") == "single"])
        }
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "priority_breakdown": priority_stats,
            "task_types": task_types,
            "average_tasks_per_day": total_tasks / 30 if total_tasks > 0 else 0
        }
    except Exception as e:
        print(f"Erro ao buscar analytics: {e}")
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_rate": 0,
            "priority_breakdown": {"high": 0, "medium": 0, "low": 0},
            "task_types": {"daily": 0, "single": 0},
            "average_tasks_per_day": 0
        }

# =============================
# Database Health Check
# =============================
def test_connection() -> bool:
    """Test database connection"""
    try:
        if not supabase:
            return False
        
        result = supabase.table("users").select("count", count="exact").execute()
        return True
    except Exception as e:
        print(f"Teste de conexão falhou: {e}")
        return False
"""
NeuroTask - Utilities Module
Adaptado para a estrutura real do Supabase
"""
import hashlib
import bcrypt
from supabase import create_client, Client

# =============================
# Supabase Configuration
# =============================
SUPABASE_URL = "https://ngcinsfttwpaxzloexbx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5nY2luc2Z0dHdwYXh6bG9leGJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NDI2OTIsImV4cCI6MjA3NTMxODY5Mn0.As8CabSnXkOlaxqR-eMHMMNgMX_Hhuse877KLDva_8M"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Conectado ao Supabase")
except Exception as e:
    print(f"✗ Erro ao conectar ao Supabase: {e}")
    supabase = None

# =============================
# Password Utilities
# =============================
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def hash_password_sha256(password: str) -> str:
    """Legacy SHA256 hash"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password - suporta bcrypt, SHA256 e plaintext"""
    if not stored_hash:
        return False
    
    # Try bcrypt first
    if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            return False
    
    # Try SHA256
    sha256_hash = hash_password_sha256(password)
    if stored_hash == sha256_hash:
        return True
    
    # Plaintext (para compatibilidade com dados existentes)
    if stored_hash == password:
        return True
    
    return False

def migrate_password(user_id: str, email: str, password: str, old_hash: str) -> bool:
    """Migrate old password to bcrypt"""
    try:
        if verify_password(password, old_hash):
            new_hash = hash_password(password)
            update_user(email, {"password": new_hash})
            return True
        return False
    except Exception as e:
        print(f"Erro ao migrar senha: {e}")
        return False

# =============================
# User Management Functions
# =============================
def create_user(username: str, email: str, password: str, theme: str = "light_lavender") -> dict:
    """Create a new user"""
    if not supabase:
        raise Exception("Banco de dados não disponível")
    
    try:
        hashed_password = hash_password(password)
        data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "theme_settings": {"current_theme": theme}
        }
        
        result = supabase.table("users").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        raise

def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def get_user_by_username(username: str) -> dict:
    """Get user by username"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").select("*").eq("username", username).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def update_user(email: str, updates: dict) -> dict:
    """Update user information"""
    if not supabase:
        return None
    
    try:
        result = supabase.table("users").update(updates).eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        return None

def delete_user(email: str) -> bool:
    """Delete user and all tasks"""
    if not supabase:
        return False
    
    try:
        user = get_user_by_email(email)
        if not user:
            return False
        
        # Delete tasks first
        supabase.table("tasks").delete().eq("user_id", user["id"]).execute()
        
        # Delete user
        supabase.table("users").delete().eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return False

# =============================
# Task Management Functions
# =============================
def get_tasks(user_id: str) -> list:
    """Get all tasks for a user"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
        tasks = result.data or []
        
        # Adicionar priority como 'medium' para compatibilidade com o app
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas: {e}")
        return []

def add_task(user_id: str, title: str, description: str = "", due_date: str = "", 
             type: str = "single", priority: str = "medium") -> dict:
    """Add a new task (priority é ignorado pois não existe no banco)"""
    if not supabase:
        return None
    
    try:
        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "type": type,
            "completed": False
        }
        
        result = supabase.table("tasks").insert(data).execute()
        
        if result.data:
            task = result.data[0]
            # Adicionar priority para compatibilidade
            task['priority'] = priority
            return task
        return None
    except Exception as e:
        print(f"Erro ao adicionar tarefa: {e}")
        return None

def update_task(task_id: str, updates: dict) -> dict:
    """Update a task"""
    if not supabase:
        return None
    
    try:
        # Remover priority dos updates pois não existe no banco
        updates_clean = {k: v for k, v in updates.items() if k != 'priority'}
        
        result = supabase.table("tasks").update(updates_clean).eq("id", task_id).execute()
        
        if result.data:
            task = result.data[0]
            # Adicionar priority para compatibilidade
            if 'priority' not in task:
                task['priority'] = updates.get('priority', 'medium')
            return task
        return None
    except Exception as e:
        print(f"Erro ao atualizar tarefa: {e}")
        return None

def delete_task(task_id: str) -> bool:
    """Delete a task"""
    if not supabase:
        return False
    
    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao deletar tarefa: {e}")
        return False

def get_pending_tasks(user_id: str) -> list:
    """Get pending tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", False).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas pendentes: {e}")
        return []

def get_completed_tasks(user_id: str) -> list:
    """Get completed tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", True).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas concluídas: {e}")
        return []

def get_tasks_by_priority(user_id: str, priority: str) -> list:
    """Get tasks by priority (retorna todas pois não há coluna priority)"""
    return get_tasks(user_id)

def get_daily_tasks(user_id: str) -> list:
    """Get daily tasks"""
    if not supabase:
        return []
    
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("type", "daily").execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas diárias: {e}")
        return []

# =============================
# Notification Functions
# =============================
def send_task_notification(title: str, description: str = "", app_context=None) -> None:
    """Send notification (log only)"""
    print(f"🔔 Notificação: {title}")
    if description:
        print(f"   {description}")

def get_due_tasks(user_id: str) -> list:
    """Get tasks due now"""
    if not supabase:
        return []
    
    try:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("due_date", current_time).eq("completed", False).execute()
        tasks = result.data or []
        
        for task in tasks:
            if 'priority' not in task:
                task['priority'] = 'medium'
        
        return tasks
    except Exception as e:
        print(f"Erro ao buscar tarefas vencidas: {e}")
        return []

# =============================
# Analytics Functions  
# =============================
def get_user_analytics(user_id: str) -> dict:
    """Get user analytics"""
    try:
        tasks = get_tasks(user_id)
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("completed", False)])
        pending_tasks = total_tasks - completed_tasks
        
        priority_stats = {
            "high": len([t for t in tasks if t.get("priority") == "high"]),
            "medium": len([t for t in tasks if t.get("priority") == "medium"]), 
            "low": len([t for t in tasks if t.get("priority") == "low"])
        }
        
        task_types = {
            "daily": len([t for t in tasks if t.get("type") == "daily"]),
            "single": len([t for t in tasks if t.get("type") == "single"])
        }
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "priority_breakdown": priority_stats,
            "task_types": task_types,
            "average_tasks_per_day": total_tasks / 30 if total_tasks > 0 else 0
        }
    except Exception as e:
        print(f"Erro ao buscar analytics: {e}")
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_rate": 0,
            "priority_breakdown": {"high": 0, "medium": 0, "low": 0},
            "task_types": {"daily": 0, "single": 0},
            "average_tasks_per_day": 0
        }

# =============================
# Database Health Check
# =============================
def test_connection() -> bool:
    """Test database connection"""
    try:
        if not supabase:
            return False
        
        result = supabase.table("users").select("count", count="exact").execute()
        return True
    except Exception as e:
        print(f"Teste de conexão falhou: {e}")
        return False

import os
import hashlib
import bcrypt
from supabase import create_client, Client
from datetime import datetime

# =============================
# Supabase Configuration
# =============================
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().strip('"')
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip().strip('"')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL and SUPABASE_KEY environment variables are not set!")
    supabase = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully connected to Supabase")
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        supabase = None

# =============================
# Password Utilities
# =============================
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def hash_password_sha256(password: str) -> str:
    """Legacy SHA256 hash (for migration)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against hash with backward compatibility"""
    if not stored_hash:
        return False
    
    # Try bcrypt first (new format)
    if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            return False
    
    # Fallback to SHA256 (legacy) or plaintext (very legacy)
    sha256_hash = hash_password_sha256(password)
    if stored_hash == sha256_hash:
        return True
    
    # Last resort: check plaintext (for very old accounts)
    if stored_hash == password:
        return True
    
    return False

def migrate_password(user_id: int, email: str, password: str, old_hash: str) -> bool:
    """Migrate old password to new bcrypt hash"""
    try:
        # Only migrate if verification succeeds
        if verify_password(password, old_hash):
            new_hash = hash_password(password)
            update_user(email, {"password": new_hash})
            return True
        return False
    except Exception as e:
        print(f"Error migrating password: {e}")
        return False

# =============================
# User Management Functions
# =============================
def create_user(username: str, email: str, password: str) -> dict:
    """Create a new user with hashed password"""
    if not supabase:
        raise Exception("Banco de dados não disponível. Verifique as configurações do Supabase.")
    
    try:
        hashed_password = hash_password(password)
        data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now().isoformat(),
            "theme_settings": {
                "current_theme": "light_blue",
                "layout_mode": "desktop"
            }
        }
        
        result = supabase.table("users").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        raise

def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    try:
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_username(username: str) -> dict:
    """Get user by username"""
    try:
        result = supabase.table("users").select("*").eq("username", username).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user by username: {e}")
        return None

def update_user(email: str, updates: dict) -> dict:
    """Update user information"""
    try:
        updates["updated_at"] = datetime.now().isoformat()
        result = supabase.table("users").update(updates).eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error updating user: {e}")
        return None

def delete_user(email: str) -> bool:
    """Delete user and all associated tasks"""
    try:
        # First, get the user to find their ID
        user = get_user_by_email(email)
        if not user:
            return False
        
        # Delete all user's tasks first
        supabase.table("tasks").delete().eq("user_id", user["id"]).execute()
        
        # Then delete the user
        result = supabase.table("users").delete().eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

# =============================
# Task Management Functions
# =============================
def get_tasks(user_id: int) -> list:
    """Get all tasks for a user"""
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting tasks: {e}")
        return []

def add_task(user_id: int, title: str, description: str = "", due_date: str = "", 
             type: str = "single", priority: str = "medium") -> dict:
    """Add a new task"""
    try:
        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "type": type,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("tasks").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error adding task: {e}")
        return None

def update_task(task_id: int, updates: dict) -> dict:
    """Update an existing task"""
    try:
        updates["updated_at"] = datetime.now().isoformat()
        result = supabase.table("tasks").update(updates).eq("id", task_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error updating task: {e}")
        return None

def delete_task(task_id: int) -> bool:
    """Delete a task"""
    try:
        result = supabase.table("tasks").delete().eq("id", task_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False

def get_pending_tasks(user_id: int) -> list:
    """Get all pending tasks for a user"""
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", False).execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting pending tasks: {e}")
        return []

def get_completed_tasks(user_id: int) -> list:
    """Get all completed tasks for a user"""
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("completed", True).execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting completed tasks: {e}")
        return []

def get_tasks_by_priority(user_id: int, priority: str) -> list:
    """Get tasks filtered by priority"""
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("priority", priority).execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting tasks by priority: {e}")
        return []

def get_daily_tasks(user_id: int) -> list:
    """Get all daily recurring tasks"""
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("type", "daily").execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting daily tasks: {e}")
        return []

# =============================
# Notification Functions
# =============================
def send_task_notification(title: str, description: str = "", app_context=None) -> None:
    """Send a task notification (logging implementation)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🔔 NOTIFICATION: {title}")
    if description:
        print(f"[{timestamp}] 📝 Description: {description}")

def get_due_tasks(user_id: int) -> list:
    """Get tasks that are due at current time"""
    try:
        current_time = datetime.now().strftime("%H:%M")
        result = supabase.table("tasks").select("*").eq("user_id", user_id).eq("due_date", current_time).eq("completed", False).execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting due tasks: {e}")
        return []

# =============================
# Analytics Functions  
# =============================
def get_user_analytics(user_id: int) -> dict:
    """Get comprehensive user analytics"""
    try:
        tasks = get_tasks(user_id)
        
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("completed", False)])
        pending_tasks = total_tasks - completed_tasks
        
        # Priority breakdown
        priority_stats = {
            "high": len([t for t in tasks if t.get("priority") == "high"]),
            "medium": len([t for t in tasks if t.get("priority") == "medium"]), 
            "low": len([t for t in tasks if t.get("priority") == "low"])
        }
        
        # Daily vs single tasks
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
            "average_tasks_per_day": total_tasks / 30 if total_tasks > 0 else 0  # Rough estimate
        }
    except Exception as e:
        print(f"Error getting user analytics: {e}")
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
        
        # Try to query the users table
        result = supabase.table("users").select("count", count="exact").execute()
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def initialize_database() -> bool:
    """Initialize database tables if they don't exist"""
    # Note: In Supabase, tables should be created through the dashboard
    # This function is more for documentation of required schema
    print("Database initialization should be done through Supabase dashboard")
    print("Required tables:")
    print("1. users (id, username, email, password, created_at, updated_at, theme_settings)")
    print("2. tasks (id, user_id, title, description, due_date, priority, type, completed, created_at, updated_at)")
    return test_connection()

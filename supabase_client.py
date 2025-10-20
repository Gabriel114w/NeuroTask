import os
from supabase import create_client, Client
from dotenv import load_dotenv

# ---------------------------------------------------------
# Carregar variáveis de ambiente (.env)
# ---------------------------------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = None

# ---------------------------------------------------------
# Inicializar cliente Supabase
# ---------------------------------------------------------
def init_supabase():
    """Inicializa o cliente Supabase global."""
    global supabase
    try:
        if SUPABASE_URL and SUPABASE_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("[Supabase] ✅ Conexão inicializada com sucesso.")
        else:
            print("[Supabase] ⚠️ Variáveis de ambiente ausentes (URL/KEY).")
            supabase = None
    except Exception as e:
        print(f"[Supabase] ❌ Erro ao inicializar: {e}")
        supabase = None


# Inicializa automaticamente ao importar
init_supabase()

# ---------------------------------------------------------
# Autenticação: Login e Cadastro
# ---------------------------------------------------------
def sign_in_user(email: str, password: str):
    """Autentica o usuário existente (login)."""
    if not supabase:
        print("[sign_in_user] Supabase não inicializado.")
        return None

    try:
        # A função sign_in_with_password lança uma exceção se as credenciais forem inválidas.
        # Se for bem-sucedida, retorna um objeto com 'user' e 'session'.
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user_data = result.user
        if not user_data:
            # Isso é um caso de falha, mas a exceção já teria sido lançada.
            # Mantemos o retorno None por segurança.
            print("[sign_in_user] Falha ao obter dados do usuário após login.")
            return None

        return {
            "id": user_data.id,
            "email": user_data.email,
            "created_at": getattr(user_data, "created_at", None),
        }

    except Exception as e:
        # A biblioteca do Supabase lança uma exceção em caso de falha de autenticação (e-mail/senha incorretos)
        print(f"[sign_in_user] Erro de autenticação: {e}")
        return None

def sign_up_user(email: str, password: str):
    """Cria um novo usuário (cadastro)."""
    if not supabase:
        print("[sign_up_user] Supabase não inicializado.")
        return None

    try:
        # O Supabase Auth lida com o hashing da senha automaticamente.
        # A função sign_up lança uma exceção se o e-mail já estiver em uso.
        result = supabase.auth.sign_up({"email": email, "password": password})
        # O método sign_up retorna um objeto com 'user' e 'session'
        user_data = result.user
        if not user_data:
            print("[sign_up_user] Falha ao criar usuário.")
            return None

        return {
            "id": user_data.id,
            "email": user_data.email,
            "created_at": getattr(user_data, "created_at", None),
        }

    except Exception as e:
        # A biblioteca do Supabase lança uma exceção em caso de falha de cadastro (e-mail já existe, etc.)
        print(f"[sign_up_user] Erro de cadastro: {e}")
        return None

def get_current_user():
    """Obtém o usuário logado atual."""
    if not supabase:
        return None

    try:
        session = supabase.auth.get_session()
        if session and session.user:
            user = session.user
            return {
                "id": user.id,
                "email": user.email,
                "created_at": getattr(user, "created_at", None),
            }
        return None
    except Exception as e:
        print(f"[get_current_user] Erro: {e}")
        return None


def sign_out_user():
    """Desloga o usuário atual."""
    if not supabase:
        return False

    try:
        supabase.auth.sign_out()
        return True
    except Exception as e:
        print(f"[sign_out_user] Erro: {e}")
        return False

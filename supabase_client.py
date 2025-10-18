from supabase import create_client
import os

# Lê as credenciais do Supabase a partir das variáveis de ambiente configuradas no Streamlit Cloud
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Cria o cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

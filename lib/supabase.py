import os
from supabase import create_client, Client
from supabase.client import ClientOptions
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase_options = ClientOptions().replace(flow_type='pkce')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, supabase_options)
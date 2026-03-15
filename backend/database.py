from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Validate credentials
if not supabase_url or not supabase_key:
    print("⚠️  WARNING: Supabase credentials not set!")
    print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
    print("Copy .env.example to .env and fill in your credentials from Supabase")
    print("")
    print("For testing without Supabase, using mock mode...")
    supabase = None
else:
    supabase = create_client(supabase_url, supabase_key)

def get_db():
    if supabase is None:
        raise Exception("Supabase not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env")
    return supabase

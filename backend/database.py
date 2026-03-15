import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
MOCK_MODE = False
supabase = None

# Use mock database if Supabase credentials not provided
if not supabase_url or not supabase_key or supabase_url == "https://your-project-id.supabase.co" or supabase_url == "":
    print("⚠️  Supabase credentials not found - Using MOCK MODE")
    print("📝 To use real database, set SUPABASE_URL and SUPABASE_KEY in .env")
    from mock_database import get_mock_db
    supabase = get_mock_db()
    MOCK_MODE = True
else:
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        MOCK_MODE = False
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"⚠️  Could not connect to Supabase: {e}")
        print("📝 Falling back to MOCK MODE")
        from mock_database import get_mock_db
        supabase = get_mock_db()
        MOCK_MODE = True

def get_db():
    return supabase

def is_mock_mode():
    return MOCK_MODE

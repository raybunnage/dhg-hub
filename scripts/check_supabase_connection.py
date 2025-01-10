import os
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path


def check_supabase_connection():
    # Get the directory containing the script
    script_dir = Path(__file__).parent.parent
    # Load .env from the backend directory
    env_path = script_dir / "backend" / ".env"

    # Debug information
    print("\n=== Environment Debug Info ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    print(f"Looking for .env at: {env_path}")
    print(f"Does .env file exist? {env_path.exists()}")

    # Load the .env file
    load_dotenv(env_path)

    # Use standard Supabase environment variables (no VITE prefix)
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

        # Get and check credentials
    # supabase_url = os.getenv("VITE_SUPABASE_URL")
    # supabase_key = os.getenv("VITE_SUPABASE_ANON_KEY")


    print("\n=== Environment Variables Debug ===")
    print(f"Looking for .env at: {env_path}")
    print(f"File exists: {env_path.exists()}")
    print(f"SUPABASE_URL: {supabase_url if supabase_url else '[NOT SET]'}")
    print(f"SUPABASE_KEY: {'[SET]' if supabase_key else '[NOT SET]'}")

    # If variables aren't set, let's read the .env file directly to see what's in it
    if not all([supabase_url, supabase_key]):
        print("\n=== .env File Contents (sanitized) ===")
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        var_name = line.split("=")[0].strip()
                        print(f"Found variable: {var_name}")
        except Exception as e:
            print(f"Error reading .env file: {e}")

    print(f"Loading .env from: {env_path}")
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase Key: {'[REDACTED]' if supabase_key else 'None'}")

    if not all([supabase_url, supabase_key]):
        print("❌ Error: Missing Supabase credentials in environment variables")
        return False

    try:
        # Initialize Supabase client with only required arguments
        supabase = create_client(supabase_url, supabase_key)

        # Try a simple query to verify connection
        response = supabase.table("experts").select("*").limit(1).execute()

        print("✅ Supabase connection successful!")
        return True

    except Exception as e:
        print(f"\n❌ Supabase connection failed: {str(e)}")
        return False


if __name__ == "__main__":
    check_supabase_connection()

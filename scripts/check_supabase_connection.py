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

    # Get and check credentials
    supabase_url = os.getenv("VITE_SUPABASE_URL")
    supabase_key = os.getenv("VITE_SUPABASE_ANON_KEY")

    print("\n=== Environment Variables ===")
    print(f"SUPABASE_URL: {'[SET]' if supabase_url else '[NOT SET]'}")
    print(f"SUPABASE_KEY: {'[SET]' if supabase_key else '[NOT SET]'}")

    # If variables aren't set, try to read the file directly
    if not all([supabase_url, supabase_key]):
        print("\n=== Attempting to read .env file directly ===")
        try:
            with open(env_path, "r") as f:
                print("First few lines of .env (with sensitive data redacted):")
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key = line.split("=")[0] if "=" in line else "INVALID_FORMAT"
                        print(f"{key}=[REDACTED]")
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

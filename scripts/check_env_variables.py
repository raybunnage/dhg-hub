import os
from dotenv import load_dotenv


def check_required_env_vars():
    load_dotenv()

    # Define required environment variables
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "DEBUG",
        "SECRET_KEY",
        # Add other required variables
    ]

    missing_vars = []
    weak_values = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif var == "SECRET_KEY" and (len(value) < 32 or value == "your-secret-key"):
            weak_values.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")

    if weak_values:
        print("⚠️ Weak or default values detected:")
        for var in weak_values:
            print(f"  - {var}")

    if not missing_vars and not weak_values:
        print("✅ All required environment variables are set!")

    return len(missing_vars) == 0

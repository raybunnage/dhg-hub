from check_supabase_connection import check_supabase_connection
from verify_logging_setup import verify_logging_setup
from check_env_variables import check_required_env_vars
from check_migrations import check_migrations_status


def verify_backend_setup():
    print("🔍 Verifying backend setup...")
    print("\n1. Checking environment variables...")
    env_check = check_required_env_vars()

    print("\n2. Verifying Supabase connection...")
    supabase_check = check_supabase_connection()

    print("\n3. Checking logging configuration...")
    logging_check = verify_logging_setup()

    print("\n4. Checking database migrations...")
    check_migrations_status()

    # Summary
    print("\n=== Summary ===")
    print(f"Environment Variables: {'✅' if env_check else '❌'}")
    print(f"Supabase Connection: {'✅' if supabase_check else '❌'}")
    print(f"Logging Setup: {'✅' if logging_check else '❌'}")


if __name__ == "__main__":
    verify_backend_setup()

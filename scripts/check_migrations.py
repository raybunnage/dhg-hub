import subprocess
from pathlib import Path


def check_migrations_status():
    try:
        # Check for unmigrated changes
        result = subprocess.run(
            ["python", "manage.py", "showmigrations"], capture_output=True, text=True
        )

        if "[ ]" in result.stdout:
            print("⚠️ Warning: You have pending migrations!")
            print("\nUnmigrated changes:")
            print(result.stdout)
        else:
            print("✅ All migrations are up to date!")

        # Check for migration files without __init__.py
        migrations_dirs = Path(".").rglob("migrations")
        for dir in migrations_dirs:
            init_file = dir / "__init__.py"
            if not init_file.exists():
                print(f"⚠️ Warning: Missing __init__.py in {dir}")

    except Exception as e:
        print(f"❌ Error checking migrations: {str(e)}")

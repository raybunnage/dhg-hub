from pathlib import Path
import sys


def verify_directory_structure():
    base_dir = Path(__file__).parent
    required_paths = [
        "src/your_project_name/__init__.py",
        "src/your_project_name/api/__init__.py",
        "src/your_project_name/core/__init__.py",
        "src/your_project_name/services/__init__.py",
        "src/your_project_name/utils/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
    ]

    missing_paths = []
    for path in required_paths:
        if not (base_dir / path).exists():
            missing_paths.append(path)

    if missing_paths:
        print("❌ Missing required files/directories:")
        for path in missing_paths:
            print(f"  - {path}")
        return False

    print("✅ All required directories and files are present!")
    return True


if __name__ == "__main__":
    success = verify_directory_structure()
    sys.exit(0 if success else 1)

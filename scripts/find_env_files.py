from pathlib import Path
import os
from dotenv import load_dotenv


def find_env_files(start_path=None):
    if start_path is None:
        # Get the directory containing the script and go up one level to project root
        start_path = Path(__file__).parent.parent

    start_path = Path(start_path).resolve()  # Convert to absolute path

    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    print(f"Searching for .env files starting from: {start_path}\n")
    print("Found .env files:")
    print("-" * 50)

    env_files = []

    # Walk through directory tree
    for root, dirs, files in os.walk(start_path):
        # Skip .git and node_modules directories
        if ".git" in dirs:
            dirs.remove(".git")
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".env") or file == ".env":
                full_path = Path(root) / file
                relative_path = full_path.relative_to(start_path)
                env_files.append(
                    {
                        "full_path": str(full_path),
                        "relative_path": str(relative_path),
                        "size": full_path.stat().st_size,
                        "modified": full_path.stat().st_mtime,
                    }
                )

    # Sort by modification time (most recent first)
    env_files.sort(key=lambda x: x["modified"], reverse=True)

    if not env_files:
        print("No .env files found!")
        return

    for i, env_file in enumerate(env_files, 1):
        print(f"{i}. {env_file['relative_path']}")
        print(f"   Full path: {env_file['full_path']}")
        print(f"   Size: {env_file['size']} bytes")
        print(f"   Last modified: {os.path.getmtime(env_file['full_path'])}")
        print("-" * 50)


if __name__ == "__main__":
    find_env_files()

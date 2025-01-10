from pathlib import Path
import os


def find_gitignore_files(root_dir: str = ".") -> list:
    gitignore_files = []

    for path in Path(root_dir).rglob(".gitignore"):
        gitignore_files.append(
            {
                "path": str(path),
                "content": path.read_text() if path.is_file() else "",
                "directory": str(path.parent),
            }
        )

    return gitignore_files


def analyze_gitignore():
    gitignore_files = find_gitignore_files()

    print(f"Found {len(gitignore_files)} .gitignore file(s):")
    print("-" * 50)

    for file in gitignore_files:
        print(f"\nLocation: {file['path']}")
        print(f"Parent Directory: {file['directory']}")
        print("Contents:")
        print(file["content"])
        print("-" * 50)


if __name__ == "__main__":
    analyze_gitignore()

from pathlib import Path


def check_dsstore_rules():
    root_gitignore = Path(".gitignore")

    if not root_gitignore.exists():
        print("Error: No .gitignore found in root directory")
        return

    # Common DS_Store patterns to check for
    ds_patterns = {".DS_Store", "**/.DS_Store", "._.DS_Store", "**/._.DS_Store"}

    # Read current rules
    current_rules = set(root_gitignore.read_text().splitlines())

    # Find which DS_Store patterns are missing
    missing_patterns = ds_patterns - current_rules

    if missing_patterns:
        print("Missing DS_Store patterns in .gitignore:")
        for pattern in missing_patterns:
            print(f"  {pattern}")
        print("\nWould you like to add these patterns? (y/n)")
        if input().lower() == "y":
            with root_gitignore.open("a") as f:
                f.write("\n# macOS system files\n")
                for pattern in missing_patterns:
                    f.write(f"{pattern}\n")
            print("Patterns added to .gitignore")
    else:
        print("All DS_Store patterns are already present in .gitignore")


if __name__ == "__main__":
    check_dsstore_rules()

from pathlib import Path
import shutil
import os


def consolidate_gitignore():
    # Path to root .gitignore
    root_gitignore = Path(".gitignore")

    # Ensure we're in the project root
    if not root_gitignore.exists():
        print("Error: Must run this script from project root containing .gitignore")
        return

    # Keep track of all unique ignore rules
    all_rules = set()

    # First, collect all unique rules from all .gitignore files
    for gitignore in Path(".").rglob(".gitignore"):
        if gitignore == root_gitignore:
            continue

        print(f"Processing: {gitignore}")
        try:
            rules = gitignore.read_text().splitlines()
            # Filter out empty lines and comments
            rules = [r for r in rules if r and not r.startswith("#")]
            all_rules.update(rules)

            # Backup the file before removing
            backup_path = gitignore.with_suffix(".gitignore.bak")
            shutil.copy2(gitignore, backup_path)

            # Remove the .gitignore file
            gitignore.unlink()
            print(f"Removed: {gitignore} (backup created at {backup_path})")

        except Exception as e:
            print(f"Error processing {gitignore}: {e}")

    # Update root .gitignore with all unique rules
    current_rules = set(root_gitignore.read_text().splitlines())
    new_rules = all_rules - current_rules

    if new_rules:
        print("\nAdding the following rules to root .gitignore:")
        for rule in new_rules:
            print(f"  {rule}")

        with root_gitignore.open("a") as f:
            f.write("\n# Consolidated rules from removed .gitignore files\n")
            for rule in sorted(new_rules):
                f.write(f"{rule}\n")

    print(
        "\nDone! All .gitignore files have been consolidated into the root .gitignore"
    )
    print("Backups of removed files have been created with .gitignore.bak extension")
    print("\nTo complete the process:")
    print("1. Review the updated root .gitignore")
    print("2. git add .")
    print("3. git commit -m 'Consolidate .gitignore files'")
    print("4. Once satisfied, you can remove the .gitignore.bak files")


if __name__ == "__main__":
    consolidate_gitignore()

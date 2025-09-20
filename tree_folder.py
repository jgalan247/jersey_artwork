import os

def print_directory_structure(path, exclude_env=True, exclude_pycache=True, indent=0):
    for root, dirs, files in os.walk(path):
        # Skip Python environment directories (like venv, env)
        if exclude_env and any(env in root for env in ['venv', 'env']):
            continue

        # Exclude __pycache__ directories from traversal
        if exclude_pycache and '__pycache__' in dirs:
            dirs.remove('__pycache__')

        # Calculate indentation level
        level = root.replace(path, "").count(os.sep)

        # Print the directory name
        indent_str = "    " * level
        print(f"{indent_str}[{os.path.basename(root) or root}]")

        # Print files with indentation
        for file in files:
            print(f"{indent_str}    {file}")


# Run on current folder
if __name__ == "__main__":
    main_folder = "."
    print_directory_structure(main_folder)

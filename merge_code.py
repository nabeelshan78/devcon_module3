import os

# --- CONFIGURATION ---
# The file where all code will be saved
OUTPUT_FILE = "codebase_dump.txt"

# Directories to ignore (add more if needed)
IGNORE_DIRS = {
    "venv", "env", ".venv", "__pycache__", ".git", ".idea", ".vscode", 
    "node_modules", "build", "dist", "migrations", "bin", "obj"
}

# File extensions to include (add more if needed)
# If you want EVERYTHING that isn't binary, you can modify the logic below.
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss",
    ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".php", ".rb",
    ".json", ".yaml", ".yml", ".xml", ".md", ".txt", ".sql", ".sh", ".bat"
}

def merge_code_files(start_dir):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
            # Walk the directory tree
            for root, dirs, files in os.walk(start_dir):
                # 1. Prune the search: Remove ignored directories from the list
                # modifying 'dirs' in-place prevents os.walk from entering them
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

                for filename in files:
                    # 2. Check file extension
                    if not any(filename.endswith(ext) for ext in CODE_EXTENSIONS):
                        continue
                    
                    # Skip the output file itself if it's in the same directory
                    if filename == OUTPUT_FILE or filename == "merge_code.py":
                        continue

                    filepath = os.path.join(root, filename)
                    
                    # 3. Write to the output file
                    try:
                        with open(filepath, "r", encoding="utf-8") as infile:
                            content = infile.read()
                            
                            # Write a clearly visible header for each file
                            outfile.write("=" * 50 + "\n")
                            outfile.write(f"FILE PATH: {filepath}\n")
                            outfile.write("=" * 50 + "\n\n")
                            outfile.write(content)
                            outfile.write("\n\n")
                            
                            print(f"✅ Processed: {filepath}")
                            
                    except UnicodeDecodeError:
                        print(f"⚠️  Skipped (Binary/Encoding Error): {filepath}")
                    except Exception as e:
                        print(f"❌ Error reading {filepath}: {e}")

        print(f"\n🎉 Done! All code saved to: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    # Uses the current directory where the script is located
    current_directory = os.getcwd()
    merge_code_files(current_directory)
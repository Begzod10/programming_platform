import os
import re

def migrate_imports(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Replace 'from app.' with 'from backend.app.'
                    # Negative lookbehind to avoid 'backend.app.'
                    new_content = re.sub(r'(?<!backend\.)from app\.', 'from backend.app.', content)
                    # Replace 'import app.' with 'import backend.app.'
                    new_content = re.sub(r'(?<!backend\.)import app\.', 'import backend.app.', new_content)
                    
                    # Handle 'from app import' or 'import app' (exact)
                    new_content = re.sub(r'(?<!backend\.)from app\s+(import)', r'from backend.app \1', new_content)
                    new_content = re.sub(r'(?<!backend\.)import app\s*$', r'import backend.app', new_content, flags=re.MULTILINE)

                    if content != new_content:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        print(f"Updated {path}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    migrate_imports("backend/app")
    migrate_imports("backend/alembic")

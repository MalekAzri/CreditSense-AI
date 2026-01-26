import os
import sys

# Set stdout to utf-8 to avoid encoding errors
sys.stdout.reconfigure(encoding='utf-8')

skip_dirs = {'.git', 'node_modules', '__pycache__', '.next', '.vercel', 'huggingface_cache', 'torch_cache', '.ipynb_checkpoints', 'venv', 'env', '.idea', '.vscode'}

root_dir = r'd:\CreditSense Ai'

with open(r'd:\CreditSense Ai\tree.txt', 'w', encoding='utf-8') as outfile:
    outfile.write(f"Architecture of {root_dir}\n")
    outfile.write("=========================================\n")

    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        outfile.write(f"{indent}{os.path.basename(root)}/\n")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith('.pyc') or f == 'temp_tree.py' or f == 'tree.txt': continue
            outfile.write(f"{subindent}{f}\n")

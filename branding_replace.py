import os

def replace_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content.replace('AI', 'Phạm Tiến Dũng Gia Sư')
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {file_path}")
    except Exception as e:
        print(f"Error in {file_path}: {e}")

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        # Skip .git and node_modules
        if '.git' in dirs:
            dirs.remove('.git')
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
            
        for file in files:
            if file.endswith(('.html', '.js', '.py', '.css', '.json')):
                # Skip the replacement script itself
                if file == 'branding_replace.py':
                    continue
                file_path = os.path.join(root, file)
                replace_in_file(file_path)

if __name__ == "__main__":
    target_dir = os.getcwd()
    print(f"Starting branding replacement in: {target_dir}")
    process_directory(target_dir)
    print("Branding replacement completed.")

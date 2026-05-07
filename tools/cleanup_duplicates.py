import os
import json
import hashlib

def get_vocab_fingerprint(filepath):
    """Extracts the set of words to compare similarity."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            qid = data.get('id', 'unknown')
            v_type = data.get('type', 'vocabulary')
            # Get list of words, lowercase for comparison
            words = set(item['word'].lower().strip() for item in data.get('vocab', []))
            return qid, v_type, words
    except:
        return None, None, None

def cleanup_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    print(f"--- Intelligent Cleanup: {folder_path} ---")
    # Structure: { (qid, type): [set_of_words_from_file1, set_of_words_from_file2, ...] }
    history = {} 
    deleted_count = 0
    total_files = 0

    # Sort by filename to process older files first (usually lower timestamp)
    filenames = sorted(os.listdir(folder_path))

    for filename in filenames:
        if not filename.endswith('.json'):
            continue
        
        total_files += 1
        filepath = os.path.join(folder_path, filename)
        qid, v_type, words = get_vocab_fingerprint(filepath)
        
        if not qid or not words:
            continue

        key = (qid, v_type)
        if key not in history:
            history[key] = []
            history[key].append(words)
            continue

        # Check for overlap with any existing file for this question
        is_duplicate = False
        for existing_words in history[key]:
            if not existing_words: continue
            
            # Calculate intersection
            intersection = words.intersection(existing_words)
            overlap_percent = len(intersection) / len(words) if len(words) > 0 else 0
            
            # If more than 50% of words are identical, it's a duplicate
            if overlap_percent >= 0.5:
                is_duplicate = True
                break
        
        if is_duplicate:
            print(f"  [DELETE] {filename} (Overlapping content detected)")
            try:
                os.remove(filepath)
            except:
                pass
            deleted_count += 1
        else:
            history[key].append(words)

    print(f"Finished. Scanned {total_files} files. Deleted {deleted_count} duplicates.\n")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Folders to clean
    folders = [
        os.path.join(base_dir, "ai_vocab"),
        os.path.join(base_dir, "ai_suggestions")
    ]
    
    for folder in folders:
        cleanup_folder(folder)

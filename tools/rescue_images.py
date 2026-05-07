import os
import re
import glob

BASE_DIR = r"d:\Ton_nhi\ielts_splits"
IMAGE_DIR = os.path.join(BASE_DIR, "public", "image")

def rescue():
    files = glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))
    print(f"Total files in image dir: {len(files)}")
    
    renamed_count = 0
    for fpath in files:
        fname = os.path.basename(fpath)
        
        # 1. Simple rename for html_word_ and html_note_
        if fname.startswith("html_word_") or fname.startswith("html_note_"):
            new_name = fname.replace("html_", "", 1)
            new_path = os.path.join(IMAGE_DIR, new_name)
            if not os.path.exists(new_path):
                os.rename(fpath, new_path)
                renamed_count += 1
                # print(f"Renamed: {fname} -> {new_name}")
            else:
                # If target exists, just delete the html_ version to clean up
                os.remove(fpath)
        
    print(f"Phase 1: Renamed/Cleaned {renamed_count} word/note images.")

    # Phase 2: Handle sentences (heuristic)
    # This is harder because the old naming had fname and indices.
    # We might not be able to do this perfectly without mapping.
    # But let's at least fix the words/notes first.

if __name__ == "__main__":
    rescue()

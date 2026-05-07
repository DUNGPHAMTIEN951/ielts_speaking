import os
import re

DATA_DIR = r"d:\ietls_wrrting\data\ai_output"
SUBDIRS = ["vocab", "guides", "samples", "suggestions"]

def rename_files():
    for subdir in SUBDIRS:
        dir_path = os.path.join(DATA_DIR, subdir)
        if not os.path.exists(dir_path):
            continue
        
        print(f"Processing {subdir}...")
        files = os.listdir(dir_path)
        for filename in files:
            if not filename.endswith(".json"):
                continue
            
            # Pattern to match {id}_{type}_{timestamp}.json or {id}_band{band}_{timestamp}.json
            # Example: task2_14_vocab_vocabulary_1777492772.json -> task2_14_vocab_vocabulary.json
            # Example: S1_band8_1777493481.json -> S1_band8.json (Note: I changed sample name to sample_band8.json in server, but existing files might be band8)
            
            new_filename = filename
            
            # Remove the last 10 digits (timestamp) before .json
            # We look for _[10 digits].json
            match = re.search(r'_(\d{10})\.json$', filename)
            if match:
                timestamp_part = match.group(1)
                new_filename = filename.replace(f"_{timestamp_part}.json", ".json")
                
                # Special case for samples which I just changed to sample_band{band}.json
                if subdir == "samples" and "_band" in new_filename and "sample_" not in new_filename:
                    new_filename = "sample_" + new_filename
                
                old_path = os.path.join(dir_path, filename)
                new_path = os.path.join(dir_path, new_filename)
                
                if os.path.exists(new_path):
                    # If new path exists, maybe compare timestamps or just keep the newer one
                    # For now, let's just overwrite to ensure the "latest" logic
                    os.remove(new_path)
                
                os.rename(old_path, new_path)
                print(f"  Renamed: {filename} -> {new_filename}")

if __name__ == "__main__":
    rename_files()

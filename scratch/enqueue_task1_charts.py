import json
import requests
import re
import os
import sys

# Configuration
DATA_FILE = r"d:\ietls_wrrting\data\task1_practice_data.js"
SERVER_URL = "http://127.0.0.1:5678/enqueue_task1_chart"

def extract_json_from_js(file_path, var_name):
    print(f"Extracting {var_name} from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    pattern = rf'const\s+{var_name}\s*=\s*(\[[\s\S]*?\])\s*;'
    match = re.search(pattern, content)
    if match:
        json_str = match.group(1)
        # Try to clean common JS-only syntax like trailing commas
        clean_json = re.sub(r',\s*]', ']', json_str)
        clean_json = re.sub(r',\s*}', '}', clean_json)
        # Also handle property names without quotes if any (not perfect)
        # clean_json = re.sub(r'(\w+):', r'"\1":', clean_json) 
        
        try:
            return json.loads(clean_json)
        except Exception as e:
            print(f"JSON load failed: {e}")
            # Fallback to a simpler but riskier evaluation if needed, 
            # but for now let's just fail or try another regex
            return []
    print(f"Pattern for {var_name} not found.")
    return []

def main():
    print("--- IELTS Task 1 Chart Enqueuer ---")
    new_samples = extract_json_from_js(DATA_FILE, "TASK1_NEW_SAMPLES")
    
    if not new_samples:
        print("No items found to process.")
        return

    print(f"Found {len(new_samples)} items. Sending to {SERVER_URL}...")
    
    success_count = 0
    for item in new_samples:
        qid = item.get("id")
        question = item.get("question")
        sample = item.get("sample") or item.get("modelAnswerEn")
        
        if not qid or not question or not sample:
            print(f"Skipping {qid}: missing data")
            continue
            
        print(f"Enqueuing {qid}...", end=" ", flush=True)
        try:
            payload = {"id": qid, "question": question, "sample": sample}
            res = requests.post(SERVER_URL, json=payload, timeout=10)
            if res.status_code == 200:
                print("OK")
                success_count += 1
            else:
                print(f"FPhạm Tiến Dũng Gia SưLED ({res.status_code}) - {res.text}")
        except Exception as e:
            print(f"ERROR: {e}")
            # Don't break, try next one
            
    print(f"\nCompleted. Successfully enqueued: {success_count}/{len(new_samples)}")

if __name__ == "__main__":
    main()

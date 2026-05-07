import json
import re
import requests
import time

DATA_FILE = r"d:\ietls_wrrting\data\task1_practice_data.js"
SERVER_URL = "http://127.0.0.1:5678/enqueue_task1_chart"

def main():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Find all occurrences of { "id": "...", ... }
    objects = []
    stack = 0
    start = -1
    for i, char in enumerate(content):
        if char == '{':
            if stack == 0:
                start = i
            stack += 1
        elif char == '}':
            stack -= 1
            if stack == 0 and start != -1:
                objects.append(content[start:i+1])
                start = -1
    
    items = []
    for obj in objects:
        id_m = re.search(r'["\']id["\']\s*:\s*["\'](.*?)["\']', obj)
        sample_m = re.search(r'["\']modelAnswerEn["\']\s*:\s*["\'](.*?)["\']', obj, re.DOTALL)
        if not sample_m:
            sample_m = re.search(r'["\']sample["\']\s*:\s*["\'](.*?)["\']', obj, re.DOTALL)
        
        guide_m = re.search(r'["\']guide["\']\s*:\s*["\'](.*?)["\']', obj, re.DOTALL)
        title_m = re.search(r'["\']title["\']\s*:\s*["\'](.*?)["\']', obj)
        type_m = re.search(r'["\']type["\']\s*:\s*["\'](.*?)["\']', obj)

        if id_m and sample_m:
            items.append({
                'id': id_m.group(1),
                'sample': sample_m.group(1),
                'guide': guide_m.group(1) if guide_m else '',
                'title': title_m.group(1) if title_m else '',
                'type': type_m.group(1) if type_m else ''
            })

    print(f"Found {len(items)} Task 1 candidates.")
    
    skip_ids = [f"T1-New-{i:02d}" for i in range(1, 11)]
    
    count = 0
    for item in items:
        if item['id'] in skip_ids:
            continue
        
        if item.get('type') and item['type'].lower() in ['diagram', 'map', 'process']:
            print(f"Skipping {item['id']} (type: {item['type']})")
            continue

        payload = {
            "id": item['id'],
            "question": item.get('title', ''),
            "sample": item['sample'],
            "guide": item.get('guide', '')
        }
        
        try:
            print(f"Enqueuing {item['id']}...")
            res = requests.post(SERVER_URL, json=payload, timeout=10)
            if res.status_code == 200:
                count += 1
                print(f"  - OK")
            else:
                print(f"  - FPhạm Tiến Dũng Gia SưLED: {res.text}")
        except Exception as e:
            print(f"  - ERROR: {e}")
        
        time.sleep(0.02)

    print(f"Successfully enqueued {count} questions.")

if __name__ == "__main__":
    main()

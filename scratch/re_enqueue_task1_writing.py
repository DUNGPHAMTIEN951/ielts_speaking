import json
import re
import requests
import time

DATA_FILE = r"d:\ietls_wrrting\data\task1_practice_data.js"
SERVER_URL = "http://127.0.0.1:5678/enqueue_writing"

def main():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

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
        title_m = re.search(r'["\']title["\']\s*:\s*["\'](.*?)["\']', obj)
        sample_m = re.search(r'["\']modelAnswerEn["\']\s*:\s*["\'](.*?)["\']', obj, re.DOTALL)
        if not sample_m:
            sample_m = re.search(r'["\']sample["\']\s*:\s*["\'](.*?)["\']', obj, re.DOTALL)

        if id_m and title_m:
            items.append({
                'id': id_m.group(1),
                'title': title_m.group(1),
                'task_type_num': 1
            })

    print(f"Found {len(items)} Task 1 items to re-enqueue.")
    
    count = 0
    for item in items:
        payload = {
            "id": item['id'],
            "question": item['title'],
            "task_type_num": 1,
            "band": 8 # Default band
        }
        
        try:
            print(f"Enqueuing Writing Suite (Guide/Vocab/Sample) for {item['id']}...")
            res = requests.post(SERVER_URL, json=payload, timeout=10)
            if res.status_code == 200:
                count += 1
            else:
                print(f"  - FPhạm Tiến Dũng Gia SưLED: {res.text}")
        except Exception as e:
            print(f"  - ERROR: {e}")
        
        time.sleep(0.01)

    print(f"Successfully enqueued {count} writing suites.")

if __name__ == "__main__":
    main()

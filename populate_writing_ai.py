
import json
import re
import requests
import os

SERVER_URL = "http://localhost:5678/enqueue_writing"

def extract_json_array(content, var_name):
    print(f"Extracting {var_name}...")
    start_marker = var_name + " = ["
    start_idx = content.find(start_marker)
    if start_idx == -1:
        # Try with different spacing
        start_marker = var_name + "=["
        start_idx = content.find(start_marker)
        if start_idx == -1:
            # Try with 'const' or 'var'
            match = re.search(var_name + r'\s*=\s*\[', content)
            if match:
                start_idx = match.start()
                # Find the actual '['
                bracket_idx = content.find('[', start_idx)
            else:
                return None
        else:
            bracket_idx = start_idx + len(start_marker) - 1
    else:
        bracket_idx = start_idx + len(start_marker) - 1
        
    # Find the matching closing bracket
    bracket_count = 0
    json_str = ""
    for i in range(bracket_idx, len(content)):
        char = content[i]
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
        
        if bracket_count == 0:
            json_str = content[bracket_idx:i+1]
            break
            
    if not json_str:
        return None
        
    # Clean up JS-isms
    # 1. Remove comments
    json_str = re.sub(r'//.*', '', json_str)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    # 2. Remove trailing commas
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"JSON load failed for {var_name}: {e}")
        # Last ditch: try to fix common issues
        return None

def process_task2():
    path = r'd:\ietls_wrrting\data\units_data.js'
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return 0
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    units = extract_json_array(content, 'UNITS_DATA')
    if not units: return 0
    
    count = 0
    for unit in units:
        for q in unit.get('questions', []):
            payload = {
                "id": q.get('id', 'unknown'),
                "question": q.get('question', ''),
                "task_type_num": 2,
                "band": 8
            }
            try:
                r = requests.post(SERVER_URL, json=payload, timeout=5)
                if r.status_code == 200:
                    count += 1
                    print(f"[T2] Enqueued: {payload['id']}")
            except Exception as e:
                print(f"[ERROR] Connection failed: {e}")
    return count

def process_task1():
    path = r'd:\ietls_wrrting\data\task1_practice_data.js'
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return 0
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    count = 0
    # TASK1_NEW_SAMPLES
    t1_new = extract_json_array(content, 'TASK1_NEW_SAMPLES')
    if t1_new:
        for q in t1_new:
            payload = {
                "id": q.get('id', 'unknown'),
                "question": q.get('question', ''),
                "task_type_num": 1,
                "band": 8
            }
            try:
                r = requests.post(SERVER_URL, json=payload, timeout=5)
                if r.status_code == 200:
                    count += 1
                    print(f"[T1-NEW] Enqueued: {payload['id']}")
            except: pass
            
    # TASK1_PRACTICE_DATA
    t1_prac = extract_json_array(content, 'TASK1_PRACTICE_DATA')
    if t1_prac:
        for q in t1_prac:
            title = q.get('title', '')
            question = q.get('question', '') or q.get('introduction', '')
            
            question_text = f"Title: {title}\nQuestion: {question}"
            if 'chartData' in q:
                question_text += "\n\nChart Data (JSON):\n" + json.dumps(q['chartData'], indent=2)
            
            payload = {
                "id": q.get('id', 'unknown'),
                "question": question_text,
                "task_type_num": 1,
                "band": 8
            }
            try:
                r = requests.post(SERVER_URL, json=payload, timeout=5)
                if r.status_code == 200:
                    count += 1
                    print(f"[T1-PRAC] Enqueued: {payload['id']}")
            except: pass
            
    return count

if __name__ == "__main__":
    print("Populating Phạm Tiến Dũng Gia Sư Queue...")
    try:
        t2 = process_task2()
        t1 = process_task1()
        print(f"\nSuccess! Task 2: {t2}, Task 1: {t1}")
    except Exception as e:
        print(f"Fatal error: {e}")

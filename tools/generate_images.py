import os
import re
import json
import requests
import time
import random
import mysql.connector
import asyncio
import glob
from datetime import datetime
from urllib.parse import quote

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR) in ['scripts', 'tools']:
    BASE_DIR = os.path.dirname(SCRIPT_DIR)
else:
    BASE_DIR = SCRIPT_DIR

# Configuration
IMAGE_BASE_DIR = os.path.join(BASE_DIR, "public", "image")
BASE_URL = "https://image.pollinations.ai/prompt"
RETRIES = 3
DELAY_BETWEEN = 5 
TIMEOUT = 60 

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "ielts_speaking"
}

import hashlib

def get_safe_id(text):
    if not text: return "unknown"
    # Remove non-alphanumeric (except underscores and spaces)
    s = re.sub(r'[^a-zA-Z0-9\s_]', '', str(text))
    # Replace ALL whitespace with underscores
    s = re.sub(r'\s+', '_', s)
    s = s.strip('_').lower()
    # Replace multiple underscores with a single one
    s = re.sub(r'_+', '_', s)
    return s[:100]

def download_image(task_id, prompt):
    """Logic to download image from Pollinations Phạm Tiến Dũng Gia Sư."""
    if not os.path.exists(IMAGE_BASE_DIR):
        os.makedirs(IMAGE_BASE_DIR)

    safe_id = get_safe_id(task_id)
    filename = f"{safe_id}.jpg"
    target_path = os.path.join(IMAGE_BASE_DIR, filename)

    # Check if already exists
    if os.path.exists(target_path):
        return True

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    # Clean prompt for URL safety
    clean_prompt = prompt[:1000] # Limit prompt length for URL stability
    encoded_prompt = quote(clean_prompt)
    random_seed = random.randint(0, 999999999)
    url = f"{BASE_URL}/{encoded_prompt}?width=800&height=800&nologo=true&seed={random_seed}&model=flux"

    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.get(url, timeout=TIMEOUT, headers=headers)
            if response.status_code == 200:
                with open(target_path, 'wb') as f:
                    f.write(response.content)
                return True
            elif response.status_code == 429:
                time.sleep(30)
        except Exception as e:
            pass
        
        if attempt < RETRIES:
            time.sleep(10)
    
    return False

def get_legacy_tasks():
    """Scans all JSON prompt files in data/prompts/."""
    prompts_dir = os.path.join(BASE_DIR, "data", "prompts")
    prompt_files = glob.glob(os.path.join(prompts_dir, "prompts*.json"))
    
    all_legacy = []
    for pf in prompt_files:
        try:
            with open(pf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_legacy.extend(data)
        except: pass
    return all_legacy

async def image_worker():
    print("=" * 60)
    print(" IELTS IMAGE GENERATION WORKER (Hybrid Mode) ")
    print("=" * 60)
    
    # 1. PROCESS LEGACY JSON FILES FIRST
    legacy_tasks = get_legacy_tasks()
    if legacy_tasks:
        total = len(legacy_tasks)
        missing = []
        for t in legacy_tasks:
            tid = t.get('id', 'unknown')
            if not os.path.exists(os.path.join(IMAGE_BASE_DIR, f"{get_safe_id(tid)}.jpg")):
                missing.append(t)
        
        done_count = total - len(missing)
        print(f"\n--- CHECKING LEGACY DATA (JSON) ---")
        print(f"Total images required: {total}")
        print(f"Already done: {done_count}")
        print(f"Remaining to generate: {len(missing)}")
        print("-" * 40)
        
        if missing:
            i = 0
            while i < len(missing):
                t = missing[i]
                tid = t.get('id', 'unknown')
                tprompt = t.get('prompt', '')
                
                print(f"[{done_count + i + 1}/{total}] Generating legacy: {tid}...", end="\r")
                success = download_image(tid, tprompt)
                
                if success:
                    print(f"[{done_count + i + 1}/{total}] SUCCESS: {tid}                      ")
                    i += 1
                else:
                    print(f"[{done_count + i + 1}/{total}] FPhạm Tiến Dũng Gia SưLED: {tid}. Retrying in 5s...          ")
                    await asyncio.sleep(5)
                
                await asyncio.sleep(DELAY_BETWEEN)
        else:
            print("All legacy images are already present.")
            
    print("\n[OK] Legacy processing finished.")
    print("--- Switching to MySQL Queue for new data ---\n")

    # 2. CONTINUE WITH MYSQL QUEUE
    while True:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            # Fetch one pending image task
            cursor.execute("SELECT * FROM ai_tasks WHERE task_type = 'image' AND status = 'pending' ORDER BY created_at ASC LIMIT 1")
            task = cursor.fetchone()
            
            if task:
                task_id = task['id']
                data = json.loads(task['task_data'])
                img_id = data.get('id')
                word = data.get('word', 'Unknown')
                prompt = data.get('prompt', '')
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] MySQL Task: {word}...")
                
                # Update status to 'processing'
                cursor.execute("UPDATE ai_tasks SET status = 'processing' WHERE id = %s", (task_id,))
                conn.commit()
                
                success = download_image(img_id, prompt)
                
                final_status = 'success' if success else 'failed'
                cursor.execute("UPDATE ai_tasks SET status = %s, completed_at = %s WHERE id = %s", 
                             (final_status, datetime.now(), task_id))
                conn.commit()
                
                print(f"  Result: {final_status}")
                await asyncio.sleep(DELAY_BETWEEN)
            else:
                await asyncio.sleep(15)
                
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[CRITICAL ERROR] {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(image_worker())
    except KeyboardInterrupt:
        print("\nWorker stopped by user.")

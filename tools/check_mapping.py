import os
import json
import re

BASE_DIR = r"d:\Ton_nhi\ielts_splits"
DATA_FILE = os.path.join(BASE_DIR, "ielts_all_data.js")
IMAGE_DIR = os.path.join(BASE_DIR, "public", "image")

def check_mapping():
    # 1. Get data
    import subprocess
    result = subprocess.run(['node', 'tools/extract_data.js'], capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print("Node error")
        return
    data = json.loads(result.stdout)
    
    # 2. Check Part 1, Question 1, Band 7, Sentence 0
    q1 = data['p1'][0]
    print(f"Q1 ID: {q1['id']}")
    text = q1['samples']['band7']['text']
    print(f"Text: {text[:50]}...")
    
    # 3. Predict old filename
    # ielts_speaking_part_1.html -> ielts_speaking_part_10html
    # question 0, band7? 
    # In the old system, it probably iterated through band7, then 8, then 9.
    # So index might be cumulative or separate.
    
    # Let's list files that start with html_sent_ielts_speaking_part_10html_0_
    import glob
    matches = glob.glob(os.path.join(IMAGE_DIR, "html_sent_ielts_speaking_part_10html_0_*.jpg"))
    print(f"Matches for Q1: {matches}")

if __name__ == "__main__":
    check_mapping()

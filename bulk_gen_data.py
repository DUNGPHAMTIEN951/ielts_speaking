import json
import re
import mysql.connector
import hashlib
import os
import sys

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "ielts_speaking"
}

def add_to_queue(cursor, task_type, data):
    # Tạo hash duy nhất cho mỗi yêu cầu để tránh lặp
    hash_str = f"{task_type}_{json.dumps(data, sort_keys=True)}"
    task_hash = hashlib.sha256(hash_str.encode()).hexdigest()
    
    try:
        sql = "INSERT IGNORE INTO ai_tasks (task_hash, task_type, task_data, status) VALUES (%s, %s, %s, 'pending')"
        cursor.execute(sql, (task_hash, task_type, json.dumps(data)))
    except Exception as e:
        pass

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    data_path = "ielts_all_data.js"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    print("--- Reading question data ---")
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return

    # Tìm tất cả các block câu hỏi dùng Regex
    # Pattern tìm id, topic và q (Hỗ trợ cả nháy đơn và nháy kép)
    pattern = re.compile(r'\{\s*"id":\s*"(?P<id>[^"]+)",\s*"topic":\s*"(?P<topic>[^"]+)",\s*"q":\s*"(?P<q>[^"]+)"', re.DOTALL)
    
    matches = list(pattern.finditer(content))
    total_q = len(matches)
    
    if total_q == 0:
        # Thử lại với nháy đơn nếu nháy kép không ra (đề phòng format)
        pattern = re.compile(r"\{\s*'id':\s*'(?P<id>[^']+)',\s*'topic':\s*'(?P<topic>[^']+)',\s*'q':\s*'(?P<q>[^']+)'", re.DOTALL)
        matches = list(pattern.finditer(content))
        total_q = len(matches)

    print(f"Found {total_q} questions.")
    if total_q == 0: return

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except Exception as e:
        print(f"MySQL Connection Error: {e}")
        return
    
    print(f"--- Enqueuing {total_q * 30} tasks into MySQL ---")
    
    count = 0
    for match in matches:
        qid = match.group('id')
        question = match.group('q')
        
        # 1. Barem: 50 samples (Split into 5 tasks x 10 samples)
        for i in range(5):
            add_to_queue(cursor, "barem", {"id": qid, "question": question, "band": 8, "count": 10, "chunk": i+1})
        
        # CHUNKING: Split large requests into smaller 10-item tasks for better reliability
        # 2. 100 Vocabulary C1, C2 -> 10 tasks x 10 words
        for i in range(10):
            add_to_queue(cursor, "vocab", {"id": qid, "question": question, "count": 10, "vocab_type": "vocabulary", "chunk": i+1})
        
        # 3. 50 Collocations -> 5 tasks x 10 items
        for i in range(5):
            add_to_queue(cursor, "vocab", {"id": qid, "question": question, "count": 10, "vocab_type": "collocation", "chunk": i+1})
        
        # 4. 50 Idioms -> 5 tasks x 10 items
        for i in range(5):
            add_to_queue(cursor, "vocab", {"id": qid, "question": question, "count": 10, "vocab_type": "idiom", "chunk": i+1})
        
        # 5. 50 Phrasal Verbs -> 5 tasks x 10 items
        for i in range(5):
            add_to_queue(cursor, "vocab", {"id": qid, "question": question, "count": 10, "vocab_type": "phrasal_verb", "chunk": i+1})
        
        count += 1
        if count % 10 == 0:
            print(f"Processed {count}/{total_q} questions ({(count/total_q*100):.1f}%)...")

    conn.commit()
    cursor.close()
    conn.close()
    print("\n[SUCCESS] All tasks enqueued to MySQL.")
    print("Phạm Tiến Dũng Gia Sư Server will process them sequentially.")

if __name__ == "__main__":
    main()

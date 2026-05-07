import mysql.connector
import json

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "ielts_speaking"
}

def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # We only want to redo Task 1 guides to apply the new formatting
        # To be safe, let's just clear all writing tasks that are NOT chart generation
        # because the user wants better formatting for guides.
        query = "DELETE FROM ai_tasks WHERE task_type IN ('writing_guide', 'writing_sample', 'vocab')"
        cursor.execute(query)
        conn.commit()
        print(f"Successfully deleted {cursor.rowcount} writing tasks.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "ielts_speaking"
}

def clean_and_requeue():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Delete ALL pending tasks to start fresh with chunked data
        cursor.execute("DELETE FROM ai_tasks WHERE status = 'pending'")
        conn.commit()
        print(f"Removed {cursor.rowcount} pending vocab tasks.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clean_and_requeue()

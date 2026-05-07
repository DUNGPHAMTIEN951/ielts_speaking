import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": ""
}

def init():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ielts_speaking CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE ielts_speaking")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_hash VARCHAR(64) UNIQUE,
                task_type VARCHAR(20),
                task_data JSON,
                status VARCHAR(20) DEFAULT 'pending',
                chat_name VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME
            )
        """)
        conn.commit()
        print("Database and Table initialized successfully.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    init()

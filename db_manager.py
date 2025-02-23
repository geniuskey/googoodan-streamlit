import sqlite3

DB_PATH = "ranking.db"

def init_db():
    """
    ranking 테이블이 없다면 생성한다.
    컬럼:
    - id (자동 증가)
    - name (사용자 이름)
    - score (REAL)
    - play_time (REAL)
    - correct_count (INTEGER)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            score REAL,
            play_time REAL,
            correct_count INTEGER
        )
    """)
    conn.commit()
    conn.close()

def insert_ranking(name, score, play_time, correct_count):
    """새로운 스코어를 ranking 테이블에 삽입"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ranking (name, score, play_time, correct_count)
        VALUES (?, ?, ?, ?)
    """, (name, score, play_time, correct_count))
    conn.commit()
    conn.close()

def get_top_rankings(limit=100):
    """score가 높은 순서대로 상위 limit개 레코드 반환"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, score, play_time, correct_count
        FROM ranking
        ORDER BY score DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

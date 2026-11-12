from app.database import get_db_connection


def add_message(session_id: str, role: str, content: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,))
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.commit()
    conn.close()


def get_history(session_id: str) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
        (session_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


def get_all_sessions() -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id FROM sessions")
    rows = cursor.fetchall()
    conn.close()
    return [row["session_id"] for row in rows]


def clear_history(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

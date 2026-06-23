import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

def get_db_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path) -> None:
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Create base entries table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        
        # Create FTS5 virtual table using entries as external content
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
            content,
            content='entries',
            content_rowid='id'
        );
        """)
        
        # Create Triggers to sync entries with FTS5 virtual table
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
            INSERT INTO entries_fts(rowid, content) VALUES (new.id, new.content);
        END;
        """)
        
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
            INSERT INTO entries_fts(entries_fts, rowid, content) VALUES('delete', old.id, old.content);
        END;
        """)
        
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
            INSERT INTO entries_fts(entries_fts, rowid, content) VALUES('delete', old.id, old.content);
            INSERT INTO entries_fts(rowid, content) VALUES (new.id, new.content);
        END;
        """)
        
        conn.commit()

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", 
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "did", "do", 
    "does", "doing", "don", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", 
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", 
    "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", 
    "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", 
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", 
    "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with", "you", "your", 
    "yours", "yourself", "yourselves", "please", "retry", "tool", "error", "next", "step", "steps", "task", 
    "progress", "recommended", "todo", "list", "parameter", "environment", "details", "visual", "studio", 
    "code", "visible", "files", "open", "tabs", "current", "time", "working", "directory", "workspace", 
    "configuration", "detected", "cli", "tools", "will", "would", "should", "could", "shouldn", "don"
}

def sanitize_fts_query(query: str) -> str:
    # Strip non-alphanumeric/non-cjk/non-space characters
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', query)
    words = cleaned.split()
    
    filtered_words = []
    for w in words:
        w_lower = w.lower()
        if w_lower in STOP_WORDS:
            continue
        # CJK characters are preserved even if 1 char. English terms must be >= 2 chars.
        if len(w) >= 2 or re.match(r'[\u4e00-\u9fff]', w):
            filtered_words.append(w)
            
    # Return OR list of terms for soft search matching
    return " OR ".join(filtered_words) if filtered_words else ""

def add_entry(db_path: Path, content: str, author: str, created_at: str = None) -> int:
    if not created_at:
        from datetime import timezone
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entries (content, author, created_at) VALUES (?, ?, ?)",
            (content, author, created_at)
        )
        conn.commit()
        return cursor.lastrowid

def search_entries(db_path: Path, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    sanitized = sanitize_fts_query(query)
    if not sanitized:
        return []
        
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            # BM25 ranking: lower rank value is better match (most negative/lowest)
            cursor.execute("""
                SELECT e.id, e.content, e.author, e.created_at, bm25(entries_fts) as rank
                FROM entries_fts f
                JOIN entries e ON e.id = f.rowid
                WHERE entries_fts MATCH ?
                ORDER BY rank ASC
                LIMIT ?
            """, (sanitized, limit))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Fallback to simple LIKE query if FTS5 syntax fails
            like_pat = f"%{query}%"
            cursor.execute("""
                SELECT id, content, author, created_at, 0.0 as rank
                FROM entries
                WHERE content LIKE ?
                LIMIT ?
            """, (like_pat, limit))
            return [dict(row) for row in cursor.fetchall()]

def list_entries(db_path: Path) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, author, created_at FROM entries ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_entry(db_path: Path, entry_id: int) -> bool:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0

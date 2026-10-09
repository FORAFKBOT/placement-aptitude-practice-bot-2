"""
database.py - SQLite Database Management & Repository for Placement Aptitude Practice Bot
Stores questions, user attempts, test sessions, and analytics.
"""

import sqlite3
import json
import os
import random
from typing import Optional, List, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "questions.db")
JSON_PATH = os.path.join(DATA_DIR, "questions.json")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and populates it with extracted questions."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    # Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        company TEXT,
        topic TEXT,
        difficulty TEXT DEFAULT 'Medium',
        question_text TEXT NOT NULL,
        code_snippet TEXT DEFAULT '',
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        explanation TEXT,
        source_file TEXT,
        is_generated INTEGER DEFAULT 0
    )
    """)

    # Attempts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_attempts (
        attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        question_id INTEGER,
        category TEXT,
        topic TEXT,
        user_choice TEXT,
        is_correct INTEGER,
        time_taken_sec REAL DEFAULT 0,
        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    """)

    # Test Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_sessions (
        session_id TEXT PRIMARY KEY,
        test_type TEXT,
        target_company TEXT,
        score REAL,
        total_questions INTEGER,
        correct_count INTEGER,
        accuracy_percent REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    # Seed with questions from questions.json if empty
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    if count == 0 and os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            q_list = json.load(f)
        for q in q_list:
            opts = q.get('options', {})
            cursor.execute("""
            INSERT INTO questions (category, company, topic, difficulty, question_text,
                                  code_snippet, option_a, option_b, option_c, option_d,
                                  correct_answer, explanation, source_file, is_generated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q.get('category', 'quantitative'),
                q.get('company', 'General'),
                q.get('topic', 'General Aptitude'),
                q.get('difficulty', 'Medium'),
                q.get('question', ''),
                q.get('code_snippet', ''),
                opts.get('A', 'Option A'),
                opts.get('B', 'Option B'),
                opts.get('C', 'Option C'),
                opts.get('D', 'Option D'),
                q.get('answer', 'A'),
                q.get('explanation', ''),
                q.get('source', 'Drive Material'),
                0
            ))
        conn.commit()
        print(f"Populated database with {len(q_list)} placement questions from {JSON_PATH}")

    conn.close()

def insert_question(q: Dict[str, Any], is_generated: bool = False) -> int:
    """Inserts a new question into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    opts = q.get('options', {})
    cursor.execute("""
    INSERT INTO questions (category, company, topic, difficulty, question_text,
                          code_snippet, option_a, option_b, option_c, option_d,
                          correct_answer, explanation, source_file, is_generated)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        q.get('category'),
        q.get('company', 'General'),
        q.get('topic', 'General'),
        q.get('difficulty', 'Medium'),
        q.get('question', ''),
        q.get('code_snippet', ''),
        opts.get('A', ''),
        opts.get('B', ''),
        opts.get('C', ''),
        opts.get('D', ''),
        q.get('answer', 'A'),
        q.get('explanation', ''),
        q.get('source', 'User Added'),
        1 if is_generated else 0
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Helper to convert database row to question dictionary."""
    return {
        'id': row['id'],
        'category': row['category'],
        'company': row['company'],
        'topic': row['topic'],
        'difficulty': row['difficulty'],
        'question': row['question_text'],
        'code_snippet': row['code_snippet'],
        'options': {
            'A': row['option_a'],
            'B': row['option_b'],
            'C': row['option_c'],
            'D': row['option_d']
        },
        'answer': row['correct_answer'],
        'explanation': row['explanation'],
        'source': row['source_file'],
        'is_generated': bool(row['is_generated'])
    }

def get_question_by_id(qid: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None

def get_random_question(category: Optional[str] = None,
                        company: Optional[str] = None,
                        topic: Optional[str] = None,
                        difficulty: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM questions WHERE 1=1"
    params = []
    
    if category:
        query += " AND LOWER(category) = ?"
        params.append(category.lower())
    if company:
        query += " AND LOWER(company) LIKE ?"
        params.append(f"%{company.lower()}%")
    if topic:
        query += " AND LOWER(topic) LIKE ?"
        params.append(f"%{topic.lower()}%")
    if difficulty:
        query += " AND LOWER(difficulty) = ?"
        params.append(difficulty.lower())
        
    query += " ORDER BY RANDOM() LIMIT 1"
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row_to_dict(row) if row else None

def get_mock_test_questions(company: str = "TCS",
                            questions_per_section: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """Retrieves a balanced set of questions for a company placement mock test."""
    conn = get_connection()
    categories = ['quantitative', 'logical', 'verbal', 'coding']
    sections = {}

    for cat in categories:
        # First try to get company-specific questions
        rows = conn.execute("""
            SELECT * FROM questions 
            WHERE LOWER(category) = ? AND LOWER(company) LIKE ?
            ORDER BY RANDOM() LIMIT ?
        """, (cat, f"%{company.lower()}%", questions_per_section)).fetchall()
        
        selected = [row_to_dict(r) for r in rows]
        
        # If needed, fill with general category questions
        if len(selected) < questions_per_section:
            needed = questions_per_section - len(selected)
            existing_ids = [s['id'] for s in selected]
            placeholders = ",".join("?" for _ in existing_ids) if existing_ids else "0"
            fill_rows = conn.execute(f"""
                SELECT * FROM questions 
                WHERE LOWER(category) = ? AND id NOT IN ({placeholders})
                ORDER BY RANDOM() LIMIT ?
            """, [cat] + existing_ids + [needed]).fetchall()
            selected.extend([row_to_dict(r) for r in fill_rows])

        sections[cat] = selected

    conn.close()
    return sections

def record_attempt(session_id: str, question_id: int, category: str, topic: str,
                   user_choice: str, is_correct: bool, time_taken_sec: float = 0.0):
    conn = get_connection()
    conn.execute("""
        INSERT INTO user_attempts (session_id, question_id, category, topic,
                                  user_choice, is_correct, time_taken_sec)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, question_id, category, topic, user_choice, 1 if is_correct else 0, time_taken_sec))
    conn.commit()
    conn.close()

def record_session(session_id: str, test_type: str, target_company: str,
                   score: float, total: int, correct: int):
    acc = (correct / total * 100) if total > 0 else 0.0
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO test_sessions (session_id, test_type, target_company,
                                             score, total_questions, correct_count, accuracy_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, test_type, target_company, score, total, correct, acc))
    conn.commit()
    conn.close()

def get_performance_stats() -> Dict[str, Any]:
    """Computes overall and sectional analytics from user practice history."""
    conn = get_connection()
    total_attempts = conn.execute("SELECT COUNT(*) FROM user_attempts").fetchone()[0]
    correct_attempts = conn.execute("SELECT COUNT(*) FROM user_attempts WHERE is_correct = 1").fetchone()[0]
    avg_time = conn.execute("SELECT AVG(time_taken_sec) FROM user_attempts WHERE time_taken_sec > 0").fetchone()[0] or 0.0

    # Category breakdown
    cat_rows = conn.execute("""
        SELECT category, 
               COUNT(*) as total,
               SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
               AVG(time_taken_sec) as avg_time
        FROM user_attempts
        GROUP BY category
    """).fetchall()

    categories_stats = {}
    for r in cat_rows:
        tot = r['total']
        cor = r['correct']
        acc = (cor / tot * 100) if tot > 0 else 0.0
        categories_stats[r['category']] = {
            'total': tot,
            'correct': cor,
            'accuracy': round(acc, 1),
            'avg_time': round(r['avg_time'] or 0.0, 1)
        }

    # Weak topics (< 60% accuracy with >= 2 attempts)
    topic_rows = conn.execute("""
        SELECT topic, category,
               COUNT(*) as total,
               SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
        FROM user_attempts
        GROUP BY topic, category
        HAVING total >= 2
        ORDER BY (CAST(correct AS FLOAT) / total) ASC
        LIMIT 5
    """).fetchall()

    weak_topics = []
    for r in topic_rows:
        tot = r['total']
        cor = r['correct']
        acc = (cor / tot * 100) if tot > 0 else 0.0
        weak_topics.append({
            'topic': r['topic'],
            'category': r['category'],
            'total': tot,
            'accuracy': round(acc, 1)
        })

    conn.close()
    return {
        'total_attempts': total_attempts,
        'correct_attempts': correct_attempts,
        'overall_accuracy': round((correct_attempts / total_attempts * 100) if total_attempts > 0 else 0.0, 1),
        'avg_time_sec': round(avg_time, 1),
        'category_stats': categories_stats,
        'weak_topics': weak_topics
    }

def get_db_summary() -> Dict[str, Any]:
    """Returns question count breakdown currently present in the database."""
    conn = get_connection()
    total_q = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    
    cat_rows = conn.execute("SELECT category, COUNT(*) as cnt FROM questions GROUP BY category").fetchall()
    cats = {r['category']: r['cnt'] for r in cat_rows}
    
    comp_rows = conn.execute("SELECT company, COUNT(*) as cnt FROM questions GROUP BY company").fetchall()
    comps = {r['company']: r['cnt'] for r in comp_rows}
    
    conn.close()
    return {
        'total_questions': total_q,
        'categories': cats,
        'companies': comps
    }

if __name__ == '__main__':
    init_db()
    summary = get_db_summary()
    print("Database Initialized Successfully!")
    print(json.dumps(summary, indent=2))

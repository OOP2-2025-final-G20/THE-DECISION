import sqlite3
 
DB_PATH = "vote_app.db"
 
conn = sqlite3.connect(DB_PATH)

cur = conn.cursor()
 
cur.executescript("""

CREATE TABLE IF NOT EXISTS questions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    question TEXT NOT NULL,

    option_a TEXT NOT NULL,

    option_b TEXT NOT NULL,

    created_at TEXT NOT NULL

);
 
CREATE TABLE IF NOT EXISTS votes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    question_id INTEGER NOT NULL,

    choice TEXT CHECK(choice IN ('A', 'B')) NOT NULL,

    user_name TEXT,

    voted_at TEXT NOT NULL,

    FOREIGN KEY (question_id) REFERENCES questions(id)

);

""")
 
conn.commit()

conn.close()
 
print("vote_app.db initialized")

 
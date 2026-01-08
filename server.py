"""
FastAPIサーバー - 究極の二択！意思決定・多数決支援ツール
SQLite版（JSON不使用）
"""
 
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pathlib import Path
import sqlite3
 
app = FastAPI(
    title="究極の二択！意思決定・多数決支援ツール",
    version="1.0.0"
)
 
# ---------- Static ----------
app.mount("/static", StaticFiles(directory="static"), name="static")
 
# ---------- DB ----------
DB_PATH = "vote_app.db"
 
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
# ---------- Models ----------
class QuestionCreate(BaseModel):
    q: str
    a: str
    b: str
 
class QuestionUpdate(BaseModel):
    q: str
    a: str
    b: str
 
class VoteRequest(BaseModel):
    question_id: int
    choice: str
    user_name: Optional[str] = None
 
# ---------- Pages ----------
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = Path("templates/index.html")
    if not html_path.exists():
        return HTMLResponse("<h1>index.html not found</h1>")
    return FileResponse(html_path)
 
# ---------- API ----------
 
@app.get("/api/question")
async def get_current_question():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, question, option_a, option_b
        FROM questions
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
 
    if not row:
        raise HTTPException(status_code=404, detail="お題が登録されていません")
 
    return {
        "id": row["id"],
        "q": row["question"],
        "a": row["option_a"],
        "b": row["option_b"]
    }
 
@app.get("/api/question/{question_id}")
async def get_question(question_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, question, option_a, option_b
        FROM questions WHERE id = ?
    """, (question_id,))
    row = cur.fetchone()
    conn.close()
 
    if not row:
        raise HTTPException(status_code=404, detail="お題が見つかりません")
 
    return {
        "id": row["id"],
        "q": row["question"],
        "a": row["option_a"],
        "b": row["option_b"]
    }
 
@app.get("/api/questions")
async def get_all_questions():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, question, option_a, option_b
        FROM questions
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
 
    return [
        {"id": r["id"], "q": r["question"], "a": r["option_a"], "b": r["option_b"]}
        for r in rows
    ]
 
@app.post("/api/question")
async def create_question(data: QuestionCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO questions (question, option_a, option_b, created_at)
        VALUES (?, ?, ?, ?)
    """, (data.q, data.a, data.b, datetime.now().isoformat()))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
 
    return {"id": new_id, "q": data.q, "a": data.a, "b": data.b}
 
@app.put("/api/question/{question_id}")
async def update_question(question_id: int, data: QuestionUpdate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE questions
        SET question = ?, option_a = ?, option_b = ?
        WHERE id = ?
    """, (data.q, data.a, data.b, question_id))
 
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="お題が見つかりません")
 
    conn.commit()
    conn.close()
    return {"success": True}
 
@app.delete("/api/question/{question_id}")
async def delete_question(question_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM votes WHERE question_id = ?", (question_id,))
    cur.execute("DELETE FROM questions WHERE id = ?", (question_id,))
 
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="お題が見つかりません")
 
    conn.commit()
    conn.close()
    return {"success": True}
 
@app.post("/api/vote")
async def post_vote(vote: VoteRequest):
    conn = get_db()
    cur = conn.cursor()
 
    cur.execute("SELECT id FROM questions WHERE id = ?", (vote.question_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="お題が見つかりません")
 
    if vote.choice not in ("A", "B"):
        conn.close()
        raise HTTPException(status_code=400, detail="choiceはAまたはB")
 
    cur.execute("""
        INSERT INTO votes (question_id, choice, user_name, voted_at)
        VALUES (?, ?, ?, ?)
    """, (
        vote.question_id,
        vote.choice,
        vote.user_name,
        datetime.now().isoformat()
    ))
 
    conn.commit()
    conn.close()
    return {"success": True}
 
@app.get("/api/results")
async def get_results(question_id: Optional[int] = None):
    conn = get_db()
    cur = conn.cursor()
 
    if question_id is None:
        cur.execute("SELECT id FROM questions ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="お題がありません")
        question_id = row["id"]
 
    cur.execute("""
        SELECT question, option_a, option_b
        FROM questions WHERE id = ?
    """, (question_id,))
    q = cur.fetchone()
    if not q:
        conn.close()
        raise HTTPException(status_code=404, detail="お題が見つかりません")
 
    cur.execute("""
        SELECT choice, COUNT(*) cnt
        FROM votes
        WHERE question_id = ?
        GROUP BY choice
    """, (question_id,))
    rows = cur.fetchall()
    conn.close()
 
    votes_A = sum(r["cnt"] for r in rows if r["choice"] == "A")
    votes_B = sum(r["cnt"] for r in rows if r["choice"] == "B")
    total = votes_A + votes_B
 
    return {
        "question_id": question_id,
        "question": q["question"],
        "optionA": q["option_a"],
        "optionB": q["option_b"],
        "votes_A": votes_A,
        "votes_B": votes_B,
        "total": total,
        "percentage_A": round(votes_A / total * 100, 1) if total else 0,
        "percentage_B": round(votes_B / total * 100, 1) if total else 0,
    }
 
@app.get("/api/history")
async def get_history():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT question FROM questions ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [r["question"] for r in rows]
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
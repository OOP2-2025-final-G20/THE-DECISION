"""
FastAPIサーバー - 究極の二択！意思決定・多数決支援ツール（SQLite版）
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3
from pathlib import Path

# --------------------
# アプリ設定
# --------------------
app = FastAPI(
    title="究極の二択！意思決定・多数決支援ツール",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = "vote_app.db"

# --------------------
# DBユーティリティ
# --------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --------------------
# データモデル
# --------------------
class QuestionCreate(BaseModel):
    q: str
    a: str
    b: str

class QuestionUpdate(BaseModel):
    q: Optional[str] = None
    a: Optional[str] = None
    b: Optional[str] = None

class VoteRequest(BaseModel):
    question_id: int
    choice: str
    user_name: Optional[str] = None

# --------------------
# 画面
# --------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --------------------
# 問題 API
# --------------------
@app.get("/api/questions")
async def get_all_questions():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, question AS q, option_a AS a, option_b AS b
        FROM questions
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/question/{question_id}")
async def get_question(question_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, question AS q, option_a AS a, option_b AS b
        FROM questions WHERE id = ?
    """, (question_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="お題が見つかりません")
    return dict(row)

@app.post("/api/question")
async def create_question(data: QuestionCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO questions (question, option_a, option_b, created_at)
        VALUES (?, ?, ?, ?)
    """, (data.q, data.a, data.b, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"success": True}

@app.put("/api/question/{question_id}")
async def update_question(question_id: int, data: QuestionUpdate):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="お題が見つかりません")

    if data.q:
        cur.execute("UPDATE questions SET question=? WHERE id=?", (data.q, question_id))
    if data.a:
        cur.execute("UPDATE questions SET option_a=? WHERE id=?", (data.a, question_id))
    if data.b:
        cur.execute("UPDATE questions SET option_b=? WHERE id=?", (data.b, question_id))

    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/question/{question_id}")
async def delete_question(question_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM votes WHERE question_id=?", (question_id,))
    cur.execute("DELETE FROM questions WHERE id=?", (question_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# --------------------
# 投票 API
# --------------------
@app.post("/api/vote")
async def post_vote(vote: VoteRequest):
    if vote.choice not in ("A", "B"):
        raise HTTPException(status_code=400, detail="choiceはAまたはB")

    conn = get_db()
    cur = conn.cursor()

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

# --------------------
# 結果 API
# --------------------
@app.get("/api/results")
async def get_results(question_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT question, option_a, option_b
        FROM questions WHERE id = ?
    """, (question_id,))
    q = cur.fetchone()
    if q is None:
        conn.close()
        raise HTTPException(status_code=404, detail="お題が見つかりません")

    cur.execute("""
        SELECT choice, COUNT(*) as count
        FROM votes WHERE question_id=?
        GROUP BY choice
    """, (question_id,))
    rows = cur.fetchall()
    conn.close()

    votes = {row["choice"]: row["count"] for row in rows}
    a = votes.get("A", 0)
    b = votes.get("B", 0)
    total = a + b

    return {
        "question_id": question_id,
        "question": q["question"],
        "optionA": q["option_a"],
        "optionB": q["option_b"],
        "votes_A": a,
        "votes_B": b,
        "total": total,
        "percentage_A": round(a / total * 100, 1) if total else 0,
        "percentage_B": round(b / total * 100, 1) if total else 0
    }

@app.get("/api/history")
async def get_history():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT question FROM questions ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [row["question"] for row in rows]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
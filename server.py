"""
FastAPIサーバー - 究極の二択！意思決定・多数決支援ツール
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import os
from pathlib import Path

app = FastAPI(
    title="究極の二択！意思決定・多数決支援ツール",
    description="会議で意見が割れた時に使う、エンタメ性の高い投票アプリ",
    version="1.0.0"
)

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# データファイルのパス
DATA_DIR = Path("data")
QUESTIONS_FILE = DATA_DIR / "questions.json"
VOTES_FILE = DATA_DIR / "votes.json"

# データディレクトリの作成
DATA_DIR.mkdir(exist_ok=True)

# 初期データの設定
INITIAL_QUESTIONS = [
    {"id": 1, "q": "一生食べるならどっち？", "a": "高級寿司", "b": "至高の焼肉"},
    {"id": 2, "q": "旅行に行くなら？", "a": "過去へ", "b": "未来へ"},
    {"id": 3, "q": "住むならどっち？", "a": "極寒の地", "b": "灼熱の地"},
]

# --- データモデル定義 ---

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
    choice: str  # "A" or "B"
    user_name: Optional[str] = None

# --- データ永続化関数 ---

def load_questions() -> List[dict]:
    """お題データを読み込む"""
    if QUESTIONS_FILE.exists():
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # 初期データを保存
    save_questions(INITIAL_QUESTIONS)
    return INITIAL_QUESTIONS

def save_questions(questions: List[dict]):
    """お題データを保存する"""
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def load_votes() -> List[dict]:
    """投票データを読み込む"""
    if VOTES_FILE.exists():
        try:
            with open(VOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def save_votes(votes: List[dict]):
    """投票データを保存する"""
    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)

def get_next_question_id() -> int:
    """次のお題IDを取得する"""
    questions = load_questions()
    if not questions:
        return 1
    return max(q["id"] for q in questions) + 1

def get_active_question_id() -> Optional[int]:
    """現在アクティブなお題IDを取得する（最新のお題）"""
    questions = load_questions()
    if not questions:
        return None
    return max(q["id"] for q in questions)

# --- APIエンドポイント ---

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """メインHTMLを返す"""
    html_path = Path("templates/index.html")
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse("<h1>HTMLファイルが見つかりません</h1>")

@app.get("/api/question")
async def get_current_question():
    """現在アクティブなお題を取得する"""
    question_id = get_active_question_id()
    if question_id is None:
        raise HTTPException(status_code=404, detail="お題が登録されていません")
    
    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)
    if question is None:
        raise HTTPException(status_code=404, detail="お題が見つかりません")
    
    return question

@app.get("/api/question/{question_id}")
async def get_question(question_id: int):
    """特定のお題を取得する"""
    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)
    if question is None:
        raise HTTPException(status_code=404, detail="お題が見つかりません")
    return question

@app.get("/api/questions")
async def get_all_questions():
    """過去のお題一覧を取得する"""
    questions = load_questions()
    # 新しい順にソート
    questions.sort(key=lambda x: x["id"], reverse=True)
    return questions

@app.post("/api/question")
async def create_question(question_data: QuestionCreate):
    """新しいお題を作成する"""
    questions = load_questions()
    new_id = get_next_question_id()
    
    new_question = {
        "id": new_id,
        "q": question_data.q,
        "a": question_data.a,
        "b": question_data.b
    }
    
    questions.append(new_question)
    save_questions(questions)
    
    return new_question

@app.put("/api/question/{question_id}")
async def update_question(question_id: int, question_update: QuestionUpdate):
    """お題を編集する"""
    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)
    
    if question is None:
        raise HTTPException(status_code=404, detail="お題が見つかりません")
    
    # 更新
    if question_update.q is not None:
        question["q"] = question_update.q
    if question_update.a is not None:
        question["a"] = question_update.a
    if question_update.b is not None:
        question["b"] = question_update.b
    
    save_questions(questions)
    return question

@app.delete("/api/question/{question_id}")
async def delete_question(question_id: int):
    """お題を削除する"""
    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)
    
    if question is None:
        raise HTTPException(status_code=404, detail="お題が見つかりません")
    
    questions = [q for q in questions if q["id"] != question_id]
    save_questions(questions)
    
    # 関連する投票も削除
    votes = load_votes()
    votes = [v for v in votes if v["question_id"] != question_id]
    save_votes(votes)
    
    return {"success": True, "message": "お題を削除しました"}

@app.post("/api/vote")
async def post_vote(vote: VoteRequest):
    """投票を受け付ける"""
    # お題の存在確認
    questions = load_questions()
    question = next((q for q in questions if q["id"] == vote.question_id), None)
    if question is None:
        raise HTTPException(status_code=404, detail="お題が見つかりません")
    
    # 選択肢の検証
    if vote.choice not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="choiceは'A'または'B'である必要があります")
    
    # 投票を保存
    votes = load_votes()
    new_vote = {
        "question_id": vote.question_id,
        "choice": vote.choice,
        "user_name": vote.user_name,
        "voted_at": datetime.now().isoformat()
    }
    votes.append(new_vote)
    save_votes(votes)
    
    return {"success": True, "message": "投票を受け付けました"}

@app.get("/api/results")
async def get_results(question_id: Optional[int] = None):
    """現在の集計結果を取得する"""
    # question_idが指定されていない場合は、アクティブなお題を使用
    if question_id is None:
        question_id = get_active_question_id()
        if question_id is None:
            raise HTTPException(status_code=404, detail="お題が登録されていません")
    
    # お題の取得
    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)
    if question is None:
        raise HTTPException(status_code=404, detail="お題が見つかりません")
    
    # 投票の集計
    votes = load_votes()
    question_votes = [v for v in votes if v["question_id"] == question_id]
    
    votes_A = sum(1 for v in question_votes if v["choice"] == "A")
    votes_B = sum(1 for v in question_votes if v["choice"] == "B")
    total = votes_A + votes_B
    
    percentage_A = (votes_A / total * 100) if total > 0 else 0.0
    percentage_B = (votes_B / total * 100) if total > 0 else 0.0
    
    return {
        "question_id": question_id,
        "question": question["q"],
        "optionA": question["a"],
        "optionB": question["b"],
        "votes_A": votes_A,
        "votes_B": votes_B,
        "total": total,
        "percentage_A": round(percentage_A, 1),
        "percentage_B": round(percentage_B, 1)
    }

@app.get("/api/question/{question_id}/results")
async def get_question_results(question_id: int):
    """特定のお題の集計結果を取得する"""
    return await get_results(question_id=question_id)

@app.get("/api/history")
async def get_history():
    """過去のお題の質問文一覧を取得する"""
    questions = load_questions()
    return [item["q"] for item in questions]

if __name__ == "__main__":
    import uvicorn
    # 全てのネットワークインターフェースで待ち受け
    uvicorn.run(app, host="0.0.0.0", port=8000)

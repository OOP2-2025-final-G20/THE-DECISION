import flet as ft
import flet.fastapi as flet_fastapi
from fastapi import FastAPI
from pydantic import BaseModel

# --- 1. バックエンド設定 (FastAPI) ---
app = FastAPI()

# 共有データ
votes = {"A": 0, "B": 0}
question_data = {
    "question": "一生食べるならどっち？",
    "optionA": "高級寿司",
    "optionB": "至高の焼肉"
}

class Vote(BaseModel):
    choice: str

@app.post("/api/vote")
async def post_vote(vote: Vote):
    if vote.choice in votes:
        votes[vote.choice] += 1
    return votes

@app.get("/api/results")
async def get_results():
    return votes

# --- 2. フロントエンド設定 (Flet Web UI) ---
async def main(page: ft.Page):
    page.title = "究極の2択 Web"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # 結果表示用ラベル
    result_label = ft.Text("現在の結果 A: 0 票 / B: 0 票", size=20, weight="bold")

    async def vote_clicked(e):
        choice = "A" if e.control.text == question_data["optionA"] else "B"
        # 内部で直接バックエンドの処理を呼ぶ
        votes[choice] += 1
        result_label.value = f"現在の結果 A: {votes['A']} 票 / B: {votes['B']} 票"
        
        # 画面を「投票完了」の状態にする
        btn_a.disabled = True
        btn_b.disabled = True
        status_text.value = "投票ありがとうございました！"
        page.update()

    # UI要素の作成
    question_text = ft.Text(question_data["question"], size=40, weight="bold")
    status_text = ft.Text("どちらかを選んでください", size=16, color="grey")
    btn_a = ft.ElevatedButton(question_data["optionA"], on_click=vote_clicked, width=250, height=60)
    btn_b = ft.ElevatedButton(question_data["optionB"], on_click=vote_clicked, width=250, height=60)

    page.add(
        ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        question_text,
                        status_text,
                        ft.Divider(),
                        ft.Row([btn_a, btn_b], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                        ft.Divider(),
                        result_label,
                    ],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
            )
        )
    )

# --- 3. 統合 (FletをFastAPIにマウントする) ---
app.mount("/", flet_fastapi.app(main))

if __name__ == "__main__":
    import uvicorn
    # 全てのネットワークインターフェースで待ち受け
    uvicorn.run(app, host="0.0.0.0", port=8000)
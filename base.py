import flet as ft
import time
import random

# ==========================================
# データ・通信（モック）
# ==========================================
class DummyNetworkService:
    # データを保存する擬似データベース
    mock_db = [
        {"id": 1, "q": "一生食べるならどっち？", "a": "高級寿司", "b": "至高の焼肉"},
        {"id": 2, "q": "旅行に行くなら？", "a": "過去へ", "b": "未来へ"},
        {"id": 3, "q": "住むならどっち？", "a": "極寒の地", "b": "灼熱の地"},
    ]

    @staticmethod
    def get_question():
        if not DummyNetworkService.mock_db:
            return {"q": "問題がありません", "a": "-", "b": "-"}
        return random.choice(DummyNetworkService.mock_db)

    @staticmethod
    def post_vote(choice):
        return {
            "success": True,
            "current_votes": {
                "A": random.randint(5, 20),
                "B": random.randint(5, 20)
            }
        }
    
    @staticmethod
    def get_history():
        return [item["q"] for item in DummyNetworkService.mock_db]

    @staticmethod
    def get_my_questions():
        return DummyNetworkService.mock_db

    @staticmethod
    def delete_question(q_id):
        DummyNetworkService.mock_db = [q for q in DummyNetworkService.mock_db if q["id"] != q_id]

    @staticmethod
    def update_question(q_id, new_q, new_a, new_b):
        for item in DummyNetworkService.mock_db:
            if item["id"] == q_id:
                item["q"] = new_q
                item["a"] = new_a
                item["b"] = new_b
                break

# ==========================================
# メイン処理
# ==========================================
def main(page: ft.Page):
    page.title = "究極の2択 Web"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {"Roboto": "Roboto-Bold.ttf"}
    
    # 状態管理用の変数
    current_editing_id = None
    last_choice = "A"

    # --- 共通パーツ ---
    def create_app_bar(title, color):
        return ft.AppBar(
            title=ft.Text(title, color=ft.colors.WHITE),
            center_title=False,
            bgcolor=color,
            automatically_imply_leading=True,
        )

    # --- 1. トップページ ---
    def view_top():
        return ft.View(
            "/",
            [
                create_app_bar("トップメニュー", ft.colors.BLUE_500),
                ft.Container(height=30),
                ft.Text("究極の選択へようこそ", size=30, weight=ft.FontWeight.BOLD),
                ft.Container(height=30),
                ft.Column([
                    # 回答ボタン
                    ft.Container(
                        content=ft.Text("回答を始める", color=ft.colors.BLUE_700),
                        width=300, height=55, bgcolor=ft.colors.BLUE_50,
                        border_radius=30, alignment=ft.alignment.center,
                        on_click=lambda _: page.go("/question"),
                        border=ft.border.all(1, ft.colors.BLUE_100)
                    ),
                    ft.Container(height=10),
                    # 作成ボタン
                    ft.Container(
                        content=ft.Text("問題を作る", color=ft.colors.BLUE_700),
                        width=300, height=55, bgcolor=ft.colors.BLUE_50,
                        border_radius=30, alignment=ft.alignment.center,
                        on_click=lambda _: page.go("/create"),
                        border=ft.border.all(1, ft.colors.BLUE_100)
                    ),
                    ft.Container(height=10),
                    # 履歴ボタン
                    ft.Container(
                        content=ft.Text("過去の履歴", color=ft.colors.BLUE_700),
                        width=300, height=55, bgcolor=ft.colors.BLUE_50,
                        border_radius=30, alignment=ft.alignment.center,
                        on_click=lambda _: page.go("/history"),
                        border=ft.border.all(1, ft.colors.BLUE_100)
                    ),
                    ft.Container(height=10),
                    # 編集ボタン
                    ft.Container(
                        content=ft.Text("問題を編集", color=ft.colors.BROWN_700),
                        width=300, height=55, bgcolor=ft.colors.ORANGE_50,
                        border_radius=30, alignment=ft.alignment.center,
                        on_click=lambda _: page.go("/edit_list"),
                        border=ft.border.all(1, ft.colors.ORANGE_100)
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=ft.colors.WHITE
        )

    # --- 2. 回答画面 ---
    def view_question():
        q = DummyNetworkService.get_question()
        
        def on_vote(choice):
            nonlocal last_choice
            last_choice = choice
            page.go("/result")

        def create_circle_btn(text, color, choice):
            return ft.Container(
                content=ft.Text(text, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                width=150, height=150, bgcolor=color, border_radius=75,
                alignment=ft.alignment.center,
                on_click=lambda e: on_vote(choice),
                shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.with_opacity(0.3, color))
            )

        q_text = q.get("q", q.get("question", "No Question"))
        op_a = q.get("a", q.get("optionA", "A"))
        op_b = q.get("b", q.get("optionB", "B"))

        return ft.View(
            "/question",
            [
                create_app_bar("回答画面", ft.colors.ORANGE_400),
                ft.Container(height=40),
                ft.Text(f"Q. {q_text}", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=60),
                ft.Row(
                    [
                        create_circle_btn(op_a, ft.colors.RED_400, "A"),
                        ft.Container(width=30),
                        create_circle_btn(op_b, ft.colors.BLUE_400, "B"),
                    ], alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            bgcolor=ft.colors.WHITE
        )

    # --- 3. 結果画面 ---
    def view_result():
        result_data = DummyNetworkService.post_vote(last_choice)
        votes_a = result_data["current_votes"]["A"]
        votes_b = result_data["current_votes"]["B"]
        total = votes_a + votes_b
        w_a = (votes_a / total) * 300 if total > 0 else 0
        w_b = (votes_b / total) * 300 if total > 0 else 0

        bar_a = ft.Container(
            content=ft.Text(f"A: {votes_a}票", color=ft.colors.WHITE),
            width=0, height=50, bgcolor=ft.colors.RED_400, border_radius=5,
            alignment=ft.alignment.center,
            animate=ft.animation.Animation(800, ft.AnimationCurve.ELASTIC_OUT)
        )
        bar_b = ft.Container(
            content=ft.Text(f"B: {votes_b}票", color=ft.colors.WHITE),
            width=0, height=50, bgcolor=ft.colors.BLUE_400, border_radius=5,
            alignment=ft.alignment.center,
            animate=ft.animation.Animation(800, ft.AnimationCurve.ELASTIC_OUT)
        )

        def open_result(e):
            e.control.visible = False
            result_col.visible = True
            page.update()
            time.sleep(0.1)
            bar_a.width = w_a
            bar_b.width = w_b
            bar_a.update()
            bar_b.update()

        result_col = ft.Column([
            ft.Row([bar_a, ft.Container(width=10), ft.Text("VS"), ft.Container(width=10), bar_b], alignment=ft.MainAxisAlignment.CENTER),
        ], visible=False)

        return ft.View(
            "/result",
            [
                create_app_bar("集計結果", ft.colors.RED_400),
                ft.Container(height=30),
                ft.Text("投票完了！", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=30),
                ft.Container(
                    content=ft.Text("結果をオープン！", color=ft.colors.WHITE),
                    width=200, height=50, bgcolor=ft.colors.ORANGE_400, border_radius=25,
                    alignment=ft.alignment.center, on_click=open_result
                ),
                result_col,
                ft.Container(height=50),
                ft.Container(content=ft.Text("トップに戻る", color=ft.colors.BLUE), padding=10, on_click=lambda _: page.go("/"))
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, bgcolor=ft.colors.WHITE
        )

    # --- 4. 問題登録画面 ---
    def view_create():
        return ft.View(
            "/create",
            [
                create_app_bar("問題を登録", ft.colors.GREEN_500),
                ft.Container(height=30),
                ft.Text("新しい2択を作ろう", size=20),
                ft.Container(height=20),
                ft.TextField(label="質問文", width=300),
                ft.TextField(label="選択肢A", width=300),
                ft.TextField(label="選択肢B", width=300),
                ft.Container(height=20),
                ft.ElevatedButton("登録する", bgcolor=ft.colors.GREEN_500, color=ft.colors.WHITE, width=150, on_click=lambda _: page.go("/")),
                ft.TextButton("キャンセル", on_click=lambda _: page.go("/"))
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, bgcolor=ft.colors.WHITE
        )

    # --- 5. 履歴画面 ---
    def view_history():
        history_items = DummyNetworkService.get_history()
        return ft.View(
            "/history",
            [
                create_app_bar("過去の履歴", ft.colors.PURPLE_600),
                ft.ListView([ft.ListTile(leading=ft.Icon(ft.icons.HISTORY), title=ft.Text(item)) for item in history_items], expand=True)
            ], bgcolor=ft.colors.WHITE
        )

    # --- 6. 編集リスト画面 ---
    def view_edit_list():
        my_questions = DummyNetworkService.get_my_questions()
        
        def delete_item(e, q_id):
            DummyNetworkService.delete_question(q_id)
            route_change(ft.RouteChange(page.route))

        def go_to_edit(q_id):
            nonlocal current_editing_id
            current_editing_id = q_id
            controls.append(
                ft.ListTile(
                    title=ft.Text(q["q"], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    subtitle=ft.Text(f"A: {q['a']} / B: {q['b']}"),
                    trailing=ft.Row(
                        [
                            ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE, on_click=lambda e, x=current_id: go_to_edit(x)),
                            ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED, on_click=lambda e, x=current_id: delete_item(e, x)),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        width=100
                    )
                )
            )

        return ft.View(
            "/edit_list",
            [
                create_app_bar("問題の編集・削除", ft.colors.BROWN_400),
                ft.ListView(controls, expand=True),
                ft.Container(
                    content=ft.Text("トップに戻る", color=ft.colors.BROWN),
                    padding=20,
                    alignment=ft.alignment.center,
                    on_click=lambda _: page.go("/")
                )
            ], bgcolor=ft.colors.WHITE
        )

    # --- 7. 編集詳細画面 ---
    def view_edit_detail(q_id):
        target_q = next((item for item in DummyNetworkService.mock_db if item["id"] == q_id), None)
        
        if not target_q:
            return ft.View("/edit_detail", [create_app_bar("エラー", ft.colors.GREY), ft.Text("データが見つかりません")])

        tf_q = ft.TextField(label="質問文", value=target_q["q"], width=300)
        tf_a = ft.TextField(label="選択肢A", value=target_q["a"], width=300)
        tf_b = ft.TextField(label="選択肢B", value=target_q["b"], width=300)

        def save_changes(e):
            DummyNetworkService.update_question(q_id, tf_q.value, tf_a.value, tf_b.value)
            page.go("/edit_list")

        return ft.View(
            "/edit_detail",
            [
                create_app_bar("内容を編集", ft.colors.BROWN_400),
                ft.Container(height=30),
                tf_q, tf_a, tf_b,
                ft.Container(height=20),
                ft.ElevatedButton("変更を保存", bgcolor=ft.colors.BROWN_400, color=ft.colors.WHITE, width=150, on_click=save_changes),
                ft.TextButton("キャンセル", on_click=lambda _: page.go("/edit_list"))
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, bgcolor=ft.colors.WHITE
        )

    # --- ルーティング管理 ---
    def route_change(route):
        page.views.clear()
        page.views.append(view_top())

        if page.route == "/question":
            page.views.append(view_question())
        elif page.route == "/create":
            page.views.append(view_create())
        elif page.route == "/history":
            page.views.append(view_history())
        elif page.route == "/edit_list":
            page.views.append(view_edit_list())
        elif page.route == "/edit_detail":
            page.views.append(view_edit_list()) 
            page.views.append(view_edit_detail(current_editing_id))
        elif page.route.startswith("/result"):
            page.views.append(view_question())
            page.views.append(view_result())
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

# Webブラウザでポート8080で開く設定
ft.app(target=main, view=ft.WEB_BROWSER, port=8000)

        
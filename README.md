# THE-DECISION

>**リアルタイム・意思決定投票プラットフォーム**
>迷える集団に「決断」を下す。全員参加型の2択投票システム。
>

## アプリの概要
特定の選択肢に対して、『A vs B』のように投票を行う。投票を行ったら、待機画面に行き全員が終わったら自分で開示ボタンを押すと全員の解答が見えるようになる。投票は匿名で行われるため、行き詰まった会議での意思決定を促したり、某ゲームのように全員の意見が一致するかを確認する遊びを行うこともできるエンターテイメント性を兼ね備えたWebアプリである。また、過去の履歴の表示や選択肢の追加なども行うことができる。

## 仕様
本システムの実装仕様および機能要件

### 1. フロントエンド機能
* **問題選択画面**: 回答したい問題を一覧から選択できる画面を提供。問題リストはAPIから動的に取得し、クリックで選択可能。
* **投票画面**: 選択された問題の質問文と、2つの円形ボタン（2択の選択肢）を表示。ボタンクリックで投票を実行し、結果画面へ更新。
* **結果表示画面**: 投票完了後、「結果をオープン！」ボタンで集計結果を表示。A/Bそれぞれの票数とパーセンテージをバーアニメーションで可視化。
* **履歴表示**: 過去のお題の質問文一覧をリスト形式で閲覧可能。APIから取得したデータを動的に表示。


### 2. バックエンド機能 (Server & Logic)

* **データ永続化**: SQLiteデータベース（`vote_app.db`）を使用してデータを永続化。サーバー再起動後も履歴が残る。
* **お題管理API**: お題の作成（POST）、取得（GET）、更新（PUT）、削除（DELETE）を実装。関連する投票データも適切に管理。

### 3. 管理者機能 (Administration)
* **お題作成**: 任意のタイミングで新しい「質問文」と「選択肢A/B」を登録する機能。
* **お題編集**: 登録済みのお題の内容を編集する機能。質問文と選択肢を変更可能。
* **お題削除**: 不要なお題を削除する機能。削除時は関連する投票データも自動的に削除される。


---

## 役割分担と問い合わせ先

機能の追加要望、バグ報告、仕様に関する質問は、各担当者のGithubアカウントへメンション付きで連絡をお願いします。

| 担当領域  | 担当者のアカウント  | 責任範囲  |
| :--- | :--- | :--- |
| **Project Leader / PM** | [@宮澤悠大さんのID](https://github.com/fightingle2525) | 全体設計、API仕様策定、結合テスト、進捗管理 |
| **UI / Frontend** | [@仙田和暉さんのID](https://github.com/FlexLife777) | 画面レイアウト、ボタンデザイン、見た目の調整 |
| **Visual Effects** | [@石田柊人さんのID](https://github.com/Shuto0126) | グラフアニメーション、結果発表時の演出エフェクト |
| **Server Logic** | [@加藤雅士さんのID](https://github.com/masa2513) | FastAPI実装、集計ロジック、ルーティング処理 |
| **Data & Network** | [@西脇晃蒼さんのID](https://github.com/Akiraao4532) | データベース設計(SQLite)、過去ログ機能、通信環境設定 |

---

## 動作条件: require

> 動作に必要な条件

```bash
# Requires Python 3.13 or higher
# GUIおよびWebフレームワーク
flet>=0.21.0
flet-web>=0.80.0

# APIサーバー
fastapi>=0.115.12
uvicorn>=0.35.0
jinja2>=3.0.0

# データ通信（クライアント側でテストする場合に必要）
requests>=2.31.0

# サーバー側でのデータ定義
pydantic>=2.9.0
```

## Usage：使い方
> このリポジトリのアプリを動作させるために行う手順
```bash
### 仮想環境（env）を作成
python3 -m venv env #←コピーして実行

### 仮想環境を有効化 (Mac / Linux)
source env/bin/activate　#←コピーして実行
pip install -r requirements.txt　#←コピーして実行
python init_db.py #←コピーして実行
python server.py　#←コピーして実行
```

サーバーが起動したら、ブラウザで `http://localhost:8000` にアクセスしてください。

<br>

>ローカルサーバーを外部公開し他の端末からアクセスするために行う手順

1. 以下のリンクからアカウントを作成
https://dashboard.ngrok.com/get-started/setup/macos

2. 画面左のタブから『Setup & Installation』を選択、Homebrewでの操作手順に従いターミナルから「brew install ngrok」コピー＆ペーストして実行

3. その後「ngrok config add-authtoken ○○○」（○○○には個人のauthtokenがあらかじめ入力されている）を同じくコピー＆ペーストし実行

4. 最後に「ngrok http △△△」（△△△は任意のポート番号）を実行すれば外部公開は完了


別端末からアクセスする側はホストのターミナル画面に表示された『Forwarding』という欄の左側のURLを開き、『Visit Site』というボタンを押すことでアクセスすることが可能

<br>

## ファイル構成

```
THE-DECISION/
├── server.py              # FastAPIサーバー（バックエンド）
├── templates/
│   └── index.html         # HTMLテンプレート（フロントエンド）
├── static/
│   ├── css/
│   │   └── style.css      # CSSスタイル
│   └── js/
│       └── app.js          # JavaScript（フロントエンドロジック）
├── data/                  # データ保存ディレクトリ（自動生成）
│   ├── questions.json     # お題データ
│   └── votes.json         # 投票データ
└── requirements.txt       # 依存パッケージ
```
- `GET /api/question` - 現在アクティブなお題を取得
- `POST /api/vote` - 投票を受け付ける
- `GET /api/results` - 集計結果を取得
- `GET /api/questions` - お題一覧を取得
- `POST /api/question` - お題を作成
- `PUT /api/question/{question_id}` - お題を編集
- `DELETE /api/question/{question_id}` - お題を削除
- `GET /api/history` - 過去のお題の質問文一覧を取得

詳細なAPI仕様は、サーバー起動後に `http://localhost:8000/docs` で確認できます。

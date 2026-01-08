# THE-DECISION

>**リアルタイム・意思決定投票プラットフォーム**
>迷える集団に「決断」を下す。全員参加型の2択投票システム。
>

## アプリの概要
特定の選択肢に対して、AorBのように投票を行う。投票を行ったら、待機画面に行き全員が終わったら自分で開示ボタンを押すと全員の解答が見えるようになる。また、過去の履歴の表示や選択肢の追加などをできるようにする。

## 仕様
本システムの実装仕様および機能要件

### 1. フロントエンド機能
* **投票画面**: 現在の質問と、巨大なA/Bボタンを表示。
* **同期制御**: サーバー側のステータス（投票中/集計完了）をポーリングまたはSocket通信で監視し、画面を自動遷移させる。
* **履歴表示**: 過去の投票データをリスト形式で閲覧可能にする。

### 2. バックエンド機能 (Server & Logic)
* **集計API**: 投票のリクエストを受け付け、メモリまたはDB上の数値を更新する。
* **ステータス管理**: 「投票受付中」から「結果開示」へのフラグ管理を行う。
* **データ永続化**: サーバー再起動後も履歴が残るよう、SQLite等のデータベースにログを保存する。

### 3. 管理者機能 (Administration)
* **強制開示**: 全員の投票を待たずに結果画面へ強制遷移させる権限。
* **お題追加**: 任意のタイミングで新しい「質問文」と「選択肢」を登録する機能。

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
python server.py　#←コピーして実行
```

サーバーが起動したら、ブラウザで `http://localhost:8000` にアクセスしてください。

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

## APIエンドポイント

- `GET /` - メインHTMLページ
- `GET /api/question` - 現在アクティブなお題を取得
- `POST /api/vote` - 投票を受け付ける
- `GET /api/results` - 集計結果を取得
- `GET /api/questions` - お題一覧を取得
- `POST /api/question` - お題を作成
- `PUT /api/question/{question_id}` - お題を編集
- `DELETE /api/question/{question_id}` - お題を削除
- `GET /api/history` - 過去のお題の質問文一覧を取得

詳細なAPI仕様は、サーバー起動後に `http://localhost:8000/docs` で確認できます。

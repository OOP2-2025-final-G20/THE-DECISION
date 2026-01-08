# THE-DECISION

## アプリの概要
特定の選択肢に対して、AorBのように投票を行う。投票を行ったら、待機画面に行き全員が終わったら自分で開示ボタンを押すと全員の解答が見えるようになる。また、過去の履歴の表示や選択肢の追加などをできるようにする。

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
python base.py　#←コピーして実行
```

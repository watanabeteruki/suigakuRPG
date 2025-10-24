# 🎒 スイガクRPG (SuigakuRPG)

## 概要

スイガクRPGは、幼稚園から小学校低学年の幼児を対象とした、学習とRPGを組み合わせたWebアプリケーションです。マップ画面での移動やモンスターとの接触を通じて問題が出題され、正解すると戦闘に勝利できる仕組みです。

## 🎯 技術スタック

| 要素 | 技術 |
| :--- | :--- |
| **バックエンド (ゲームロジック)** | Python (Flaskを想定) |
| **フロントエンド (UI/UX)** | HTML, CSS, JavaScript (Vanilla JS) |

---

## 🚀 プロジェクトのセットアップ

### 1. 依存ライブラリのインストール

プロジェクトのバックエンドはPythonで動作します。まず、必要なライブラリをインストールします。

1.  **仮想環境の作成と有効化** (推奨)
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

2.  **依存ライブラリのインストール**
    `requirements.txt` にリストされたライブラリをインストールします。
    ```bash
    pip install -r requirements.txt
    ```

### 2. アプリケーションの実行

以下のコマンドでPythonバックエンドサーバーを起動します。

```bash
# プロジェクトルート（SuigakuRPG/）から実行
python app/main.py
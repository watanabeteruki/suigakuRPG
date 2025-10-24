# app/main.py
from flask import Flask
from app.api.routes import setup_routes

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# ルーティングを設定
setup_routes(app)

# フロントエンドの静的ファイルを配信する設定 (staticフォルダを参照)
# デフォルトで'static'フォルダは配信されますが、ここでは簡略化のため特別な設定はしていません。

if __name__ == '__main__':
    # 開発サーバーの起動
    app.run(debug=True, host='0.0.0.0', port=5000)
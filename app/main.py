# app/main.py
import os

from flask import Flask

from app.api.routes import setup_routes

#'app/main.py' の場所を基準に、一つ上の階層 (プロジェクトルート) を見つける
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# staticフォルダのパスを正しく設定
static_folder_path = os.path.join(project_root, "static")

# Flaskアプリケーションのインスタンスを作成 (static_folderのパスを指定)
app = Flask(__name__, static_folder=static_folder_path, static_url_path="")

# ルーティングを設定
setup_routes(app)

# フロントエンドの静的ファイルを配信する設定 (staticフォルダを参照)
# デフォルトで'static'フォルダは配信されますが、ここでは簡略化のため特別な設定はしていません。

if __name__ == "__main__":
    # 開発サーバーの起動
    app.run(debug=True, host="0.0.0.0", port=5000)

# app/__init__.py (Flaskアプリのインスタンス化の例)

from flask import Flask

def create_app():
    """アプリケーションファクトリ関数"""
    app = Flask(__name__)
    
    # ここで設定のロードや拡張機能の初期化を行う（例：データベース接続）

    # ルーティングを設定
    from .api.routes import setup_routes
    setup_routes(app)
    
    return app

# main.pyでは、この create_app() 関数を呼び出してアプリを起動することが多い
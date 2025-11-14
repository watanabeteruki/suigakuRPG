# app/api/routes.py
from flask import Flask, jsonify, request

from app.game.controller import GameController

# アプリケーション全体でシングルトンとしてGameControllerを保持
game_controller = GameController()


def setup_routes(app: Flask):
    """Flaskアプリケーションにルーティングを設定する関数。"""

    @app.route("/")
    def index():
        """トップページ (index.html) を返す。"""

        return app.send_static_file("index.html")

    @app.route("/api/status", methods=["GET"])
    def get_status():
        """現在のゲーム状態を取得するエンドポイント。"""
        # フロントエンドの初期ロード時などに使用
        return jsonify(game_controller._get_game_state())

    @app.route("/api/move", methods=["POST"])
    def move_player():
        """プレイヤーの移動リクエストを受け付けるエンドポイント。"""
        data = request.get_json()
        direction = data.get("direction")

        if not direction:
            return (
                jsonify({"status": "error", "message": "方向が指定されていません。"}),
                400,
            )

        result = game_controller.handle_move(direction)
        return jsonify(result)

    @app.route("/api/battle/action", methods=["POST"])
    def battle_action():
        """戦闘中の行動（回答）リクエストを受け付けるエンドポイント。"""
        data = request.get_json()
        action = data.get("action")  # 例: 'たたかう', 'にげる'
        answer = data.get("answer")  # 'たたかう'の場合に回答データ

        if not action:
            return (
                jsonify(
                    {"status": "error", "message": "アクションが指定されていません。"}
                ),
                400,
            )

        result = game_controller.submit_answer(action, answer)
        return jsonify(result)

    @app.route("/api/reset", methods=["POST"])
    def reset_game():
        """ゲーム状態をリセットするエンドポイント。"""
        # 1. コントローラーのリセット処理を呼び出す
        new_game_state = game_controller.handle_reset()
        # 2. リセット後の新しい状態を返す
        return jsonify(new_game_state)

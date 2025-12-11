from typing import Dict, Optional

from .map import Map, Monster, Question
from .player import Player


class GameController:
    """
    ゲームの状態を一元管理し、ロジックを実行するクラス。
    """

    def __init__(self):
        self.maps = Map.initialize_maps()
        self.player = Player(start_x=4, start_y=8, map_id="town")
        self.current_map: Map = self.maps[self.player.current_map]
        self.current_battle: Optional[Monster] = None

    def _get_game_state(self) -> Dict:
        """
        現在のゲーム状態をまとめて返す（フロントエンドへのデータ）。
        """
        active_monsters = [
            {
                "x": m.location_x,
                "y": m.location_y,
                "name": m.name,
                "image_file": m.image_file,
            }
            for m in self.current_map.monsters.values()
            if not m.is_defeated
        ]
        return {
            "player": self.player.get_status(),
            "current_map_id": self.current_map.map_id,
            "monsters": active_monsters,
            "background_image": self.current_map.image_file,
        }

    def handle_move(self, direction: str) -> Dict:
        """
        移動操作を受け付け、衝突判定を行い、必要に応じて戦闘やマップ遷移をトリガーする。
        """
        original_x, original_y = self.player.location_x, self.player.location_y
        self.player.move(direction)
        new_x, new_y = self.player.location_x, self.player.location_y

        # 壁との衝突判定
        map_width = self.current_map.width
        map_height = self.current_map.height
        if not (0 <= new_x < map_width and 0 <= new_y < map_height):
            self.player.location_x, self.player.location_y = original_x, original_y
            return {"status": "moved", "game_state": self._get_game_state()}

        # モンスターや施設との衝突判定
        collision = self.current_map.check_collision(new_x, new_y)

        if collision:
            entity_type = collision["type"]
            entity = collision["entity"]

            if entity_type == "monster":
                self.current_battle = entity
                self.player.location_x, self.player.location_y = (
                    original_x,
                    original_y,
                )
                return self._start_battle(self.current_battle)

            elif entity_type == "facility":
                # (マップ移動ロジックは無効化)
                if entity.get("type") == "service":
                    self.player.heal(5)

                elif entity.get("type") == "transition":
                    # 1. 移動先のマップIDと座標を取得
                    target_map_id = entity["target_map"]
                    target_x = entity["target_x"]
                    target_y = entity["target_y"]

                    # 2. プレイヤー情報を更新
                    self.player.current_map = target_map_id
                    self.player.location_x = target_x
                    self.player.location_y = target_y

                    # 3. コントローラーの現在のマップ情報を更新
                    self.current_map = self.maps[target_map_id]

                    # 4. 新しいマップの状態を返す
                    return {"status": "moved", "game_state": self._get_game_state()}

        return {"status": "moved", "game_state": self._get_game_state()}

    def _start_battle(self, monster: Monster) -> Dict:
        """
        戦闘画面に必要なデータを返す。
        """
        question_obj = monster.get_question()
        question_data = question_obj.to_dict()

        return {
            "status": "battle",
            "monster_name": monster.name,
            "monster_hp": question_obj.damage_on_failure * 2,
            "player_hp": self.player.hp,
            "question": question_data,
            "monster_image_file": monster.image_file,
            "actions": ["たたかう", "にげる"],
            "game_state": self._get_game_state(),
        }

    def submit_answer(self, action: str, answer: Optional[str] = None) -> Dict:
        """
        戦闘中のアクション（回答）を受け付け、結果を処理する。
        """
        if not self.current_battle:
            return {"status": "error", "message": "現在戦闘中ではありません。"}

        monster = self.current_battle

        if action == "にげる":
            self.current_battle = None
            return {
                "status": "battle_end",
                "message": "戦闘から離脱しました。",
                "game_state": self._get_game_state(),
            }

        if action == "たたかう" and answer is not None:
            question = monster.get_question()
            is_correct = question.check_answer(answer)

            if is_correct:
                monster.is_defeated = True
                self.current_battle = None
                return {
                    "status": "battle_win",
                    "message": f"{question.problem_text}の答えは正解！{monster.name}を倒しました。",
                    "game_state": self._get_game_state(),
                }
            else:
                damage = question.damage_on_failure
                self.player.decrease_hp(damage)

                if self.player.is_defeated():
                    self.current_battle = None
                    return {
                        "status": "game_over",
                        "message": f"不正解！HPが0になりました。ゲームオーバー...",
                        "game_state": self._get_game_state(),
                    }
                else:
                    return {
                        "status": "battle_continue",
                        "message": f"不正解！{damage}のダメージを受けました。残りHP: {self.player.hp}",
                        "question": question.to_dict(),
                        "game_state": self._get_game_state(),
                    }

        self.current_battle = None
        return {
            "status": "battle_end",
            "message": "不明なアクションのため戦闘から離脱しました。",
            "game_state": self._get_game_state(),
        }

    def handle_reset(self) -> Dict:
        """
        ゲームの状態を初期化する (ゲームオーバー時)。
        """
        self.player = Player(start_x=4, start_y=8, map_id="town")

        for map_instance in self.maps.values():
            for monster in map_instance.monsters.values():
                monster.is_defeated = False

        self.current_map = self.maps[self.player.current_map]
        self.current_battle = None
        return self._get_game_state()

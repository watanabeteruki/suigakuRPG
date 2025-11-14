import random
from typing import Dict, List, Optional


class Question:
    """算数問題の内容と正誤判定を管理するクラス。"""

    def __init__(self, name: str, problem: str, correct_answer: str, damage: int):
        self.name = name
        self.problem_text = problem
        self.correct_answer = correct_answer
        self.damage_on_failure = damage

    def check_answer(self, answer: str) -> bool:
        """回答の正誤を判定する。"""
        return str(answer).strip() == self.correct_answer

    def to_dict(self) -> dict:
        return {"monster_name": self.name, "problem_text": self.problem_text}


class Monster:
    """マップ上のモンスターシンボルと、それに紐づく問題を管理するクラス。"""

    def __init__(self, name: str, x: int, y: int, image_file: str, question: Question):
        self.name = name
        self.location_x = x
        self.location_y = y
        self.image_file = image_file
        self.question = question  # 👈 このモンスター専用の質問
        self.is_defeated = False
        self.battle_start_point = (x, y)

    def get_question(self) -> Question:
        return self.question


class Map:
    """マップ構造と地点の管理クラス。"""

    def __init__(
        self,
        map_id: str,
        width: int,
        height: int,
        monsters: List[Monster],
        facilities: List[Dict],
        image_file: str,
    ):
        self.map_id = map_id
        self.width = width
        self.height = height
        self.monsters = {(m.location_x, m.location_y): m for m in monsters}
        self.facilities = facilities
        self.image_file = image_file  # 👈 マップの背景画像

    @staticmethod
    def initialize_maps():
        """初期マップデータを生成するファクトリメソッド。"""

        # ▼ 質問とモンスターをここで定義し、紐づける ▼
        q1 = Question("さんすう", "1 + 1 = ?", "2", 3)
        m1 = Monster("ゴーレム", 5, 5, image_file="monster_golem.png", question=q1)

        q2 = Question("なぞなぞ", "パンはパンでも食べられないパンは？", "フライパン", 1)
        m2 = Monster("トロール", 10, 8, image_file="monster_troll.png", question=q2)

        map_town = Map(
            map_id="town",
            width=20,
            height=15,
            image_file="kenrokuen_map.png",  # 👈 兼六園マップを「町」として使う
            monsters=[m1, m2],
            facilities=[
                # ▼ マップ移動に関する記述を削除 ▼
                {"name": "アイテム屋", "x": 12, "y": 5, "type": "service"},
            ],
        )

        # 複数マップは削除
        return {
            "town": map_town,
        }

    def check_collision(self, x: int, y: int) -> Optional[Dict]:
        if (x, y) in self.monsters:
            monster = self.monsters[(x, y)]
            if not monster.is_defeated:
                return {"type": "monster", "entity": monster}
        for facility in self.facilities:
            if facility["x"] == x and facility["y"] == y:
                return {"type": "facility", "entity": facility}
        return None

    def remove_monster(self, monster: Monster):
        if (monster.location_x, monster.location_y) in self.monsters:
            self.monsters[(monster.location_x, monster.location_y)].is_defeated = True

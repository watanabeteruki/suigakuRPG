# app/game/map.py
from typing import List, Optional, Dict

class Question:
    """算数問題の内容と正誤判定を管理するクラス。"""
    def __init__(self, name: str, problem: str, correct_answer: str, damage: int):
        self.name = name          # モンスターの名前
        self.problem_text = problem
        self.correct_answer = correct_answer
        self.damage_on_failure = damage
        # 選択肢はフロントエンドで生成されるものと仮定し、ここでは含めない

    def check_answer(self, answer: str) -> bool:
        """回答の正誤を判定する。"""
        # 回答は文字列として受け取り、比較
        return str(answer).strip() == self.correct_answer

    def to_dict(self) -> dict:
        """戦闘開始時のUI表示に必要なデータを返す。"""
        return {
            'monster_name': self.name,
            'problem_text': self.problem_text
        }

class Monster:
    """マップ上のモンスターシンボルと、それに紐づく問題を管理するクラス。"""
    def __init__(self, name: str, x: int, y: int, question: Question):
        self.name = name
        self.location_x = x
        self.location_y = y
        self.question = question
        self.is_defeated = False
        self.battle_start_point = (x, y) # 敗北時に戻る地点

    def get_question(self) -> Question:
        """出題するQuestionオブジェクトを返す。"""
        return self.question

class Map:
    """マップ構造と地点の管理クラス。"""
    def __init__(self, map_id: str, width: int, height: int, monsters: List[Monster], facilities: List[Dict]):
        self.map_id = map_id
        self.width = width
        self.height = height
        self.monsters = { (m.location_x, m.location_y): m for m in monsters }
        self.facilities = facilities # 施設（例: 入口、アイテム屋）の座標と情報

    @staticmethod
    def initialize_maps():
        """初期マップデータを生成するファクトリメソッド。"""
        
        # モンスターと問題の定義
        q1 = Question("算数ゴブリン", "1 + 1 = ?", "2", 3)
        m1 = Monster("算数ゴブリン", 5, 5, q1)
        
        q2 = Question("九九オニ", "モンスターの数は？", "1", 5) # 図に一つだけなので
        m2 = Monster("九九オニ", 10, 8, q2)

        # マップ '町' の定義（図1に合わせた簡易的な座標）
        map_town = Map(
            map_id='town',
            width=20, 
            height=15,
            monsters=[m1, m2],
            facilities=[
                {'name': '兼六園', 'x': 2, 'y': 3, 'type': 'facility', 'target_map': 'kenrokuen'},
                {'name': '金沢城', 'x': 8, 'y': 3, 'type': 'facility', 'target_map': 'kanazawajo'},
                {'name': 'アイテム屋', 'x': 12, 'y': 5, 'type': 'service'}
            ]
        )
        return {'town': map_town}

    def check_collision(self, x: int, y: int) -> Optional[Dict]:
        """
        指定された座標に何があるか判定する。
        """
        # 1. モンスターとの接触判定
        if (x, y) in self.monsters:
            monster = self.monsters[(x, y)]
            if not monster.is_defeated:
                return {'type': 'monster', 'entity': monster}

        # 2. 施設との接触判定
        for facility in self.facilities:
            if facility['x'] == x and facility['y'] == y:
                return {'type': 'facility', 'entity': facility}
        
        # 何もなし
        return None

    def remove_monster(self, monster: Monster):
        """
        倒したモンスターをマップから消す（シンボルを消す）。
        """
        if (monster.location_x, monster.location_y) in self.monsters:
            self.monsters[(monster.location_x, monster.location_y)].is_defeated = True
            # マップ画面ではシンボルが消えるが、ここではフラグで管理
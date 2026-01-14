# app/game/map.py
import json
import os
import random
from typing import Dict, List, Optional, Set, Tuple


class Question:
    """算数問題の内容と正誤判定を管理するクラス。"""

    def __init__(self, name: str, problem: str, correct_answer: str, damage: int):
        self.name = name
        self.problem_text = problem
        if isinstance(correct_answer, list):
            self.correct_answers = [str(a) for a in correct_answer]
        else:
            self.correct_answers = [str(correct_answer)]

        self.damage_on_failure = damage

    def check_answer(self, answer: str) -> bool:
        """回答の正誤を判定する。"""
        return str(answer).strip() in self.correct_answers

    def to_dict(self) -> dict:
        is_numeric = all(ans.isdigit() for ans in self.correct_answers)
        return {
            "monster_name": self.name,
            "problem_text": self.problem_text,
            "input_type": "number" if is_numeric else "text",
        }


class Monster:
    """マップ上のモンスターシンボルと、それに紐づく問題を管理するクラス。"""

    def __init__(
        self, name: str, x: int, y: int, image_file: str, questions: List[Question]
    ):
        self.name = name
        self.location_x = x
        self.location_y = y
        self.image_file = image_file
        self.questions = questions
        self.is_defeated = False
        self.battle_start_point = (x, y)

    def get_question(self) -> Question:
        return random.choice(self.questions)


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
        map_data: List[List[int]],
    ):
        self.map_id = map_id
        self.width = width
        self.height = height
        self.monsters = {(m.location_x, m.location_y): m for m in monsters}
        self.facilities = facilities
        self.image_file = image_file
        self.map_data = map_data

        self.blocked_cells = set()
        for y, row in enumerate(map_data):
            for x, cell_type in enumerate(row):
                if cell_type == 1:
                    self.blocked_cells.add((x, y))

    def is_blocked(self, x: int, y: int) -> bool:
        return (x, y) in self.blocked_cells

    def get_safe_zones(self) -> List[Tuple[int, int]]:
        safe_spots = []
        for y, row in enumerate(self.map_data):
            for x, cell_type in enumerate(row):
                if cell_type == 0 and x > 6:
                    safe_spots.append((x, y))
        return safe_spots

    # -------------------------------------------------------------
    # ▼ 追加: JSONからマップを読み込むクラスメソッド
    # -------------------------------------------------------------
    @classmethod
    def load_from_json(cls, filename: str) -> "Map":
        """指定されたJSONファイルを読み込み、Mapインスタンスを生成して返す (モンスターは空の状態)"""

        # このファイルの場所(app/game/)から、JSONのある場所(app/data/maps/)へのパスを作る
        base_dir = os.path.dirname(__file__)  # app/game
        json_path = os.path.join(
            base_dir, "..", "data", "maps", filename
        )  # app/data/maps/filename

        # パスの正規化（..などを解決）
        json_path = os.path.normpath(json_path)

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Map file not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            map_id=data["map_id"],
            width=data["width"],
            height=data["height"],
            monsters=[],  # モンスターは後でコード側で追加する
            facilities=data["facilities"],
            image_file=data["image_file"],
            map_data=data["map_data"],
        )

    # ... (check_collision, remove_monster メソッドは変更なし) ...
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

    @staticmethod
    def initialize_maps():
        """初期マップデータを生成するファクトリメソッド。"""

        # ---------------------------------------------------------
        # 1. 問題プールの作成 (ここは変更なし)
        # ---------------------------------------------------------
        math_questions_kids = [
            Question("さんすう", "1 + 1 は なあに？", "2", 1),
            Question("さんすう", "かたて の ゆび は なんぼん？", "5", 1),
            Question("さんすう", "さんかくけい の かど は いくつ？", "3", 1),
            Question("さんすう", "くるま の タイヤ は いくつ？", "4", 1),
            Question("さんすう", "5 - 1 は なあに？", "4", 1),
            Question("さんすう", "10 は 1 と 0、では 1 と 1 は？", "11", 1),
            Question("さんすう", "とけい の かたち は まる？ さんかく？", "まる", 1),
            Question("さんすう", "ぞう と あり、 おおきい のは？", "ぞう", 1),
            Question("さんすう", "1、2、3、[？]、5。 [？] はなに？", "4", 1),
            Question("さんすう", "なにもない とき の すうじ は？", "0", 1),
        ]

        word_questions_kids = [
            Question("ことば", "あさ 起きたら なんていう？", "おはよう", 1),
            Question("ことば", "ねる まえ の あいさつ は？", "おやすみ", 1),
            Question("ことば", "「わんわん」 なく どうぶつ は？", "いぬ", 1),
            Question("ことば", "「にゃー」 と なく どうぶつ は？", "ねこ", 1),
            Question("ことば", "あかい くだもの、 なあに？（り◯ご）", "りんご", 1),
            Question("ことば", "きいろくて ながい くだもの は？", "ばなな", 1),
            Question("ことば", "あつい の はんたい は？（さ◯い）", "さむい", 1),
            Question(
                "ことば",
                "ありがとう と いわれたら？（どういたし◯◯）",
                "どういたしまして",
                1,
            ),
            Question(
                "ことば",
                "みみ が ながい どうぶつ は？",
                ["うさぎ", "ウサギ", "ロバ", "ろば"],
                1,
            ),
            Question("ことば", "はな が ながい どうぶつ は？", "ぞう", 1),
        ]

        heart_questions_kids = [
            Question("こころ", "ごはん を たべる まえ は？", "いただきます", 1),
            Question("こころ", "ごはん を たべた あと は？", "ごちそうさま", 1),
            Question(
                "こころ", "おともだち に ぶつかっちゃった。なんていう？", "ごめんね", 1
            ),
            Question("こころ", "おもちゃ を かして ほしい とき は？", "かして", 1),
            Question(
                "こころ", "プレゼント を もらったよ。なんていう？", "ありがとう", 1
            ),
            Question("こころ", "おうち に かえって きたら？", "ただいま", 1),
            Question("こころ", "おうち を でる とき は？", "いってきます", 1),
            Question("こころ", "ゴミ は どこ に すてる？（ご◯ばこ）", "ごみばこ", 1),
            Question("こころ", "ぬいだ くつ は どうする？（そ◯える）", "そろえる", 1),
            Question("こころ", "おともだち が ないていたら？（よし◯◯）", "よしよし", 1),
        ]

        mixed_pool = math_questions_kids + word_questions_kids + heart_questions_kids

        # ---------------------------------------------------------
        # ▼ 2. マップロード (JSONから読み込み！)
        # ---------------------------------------------------------
        map_town = Map.load_from_json("town.json")
        map_market = Map.load_from_json("market.json")
        map_castle = Map.load_from_json("castle.json")

        # ---------------------------------------------------------
        # ▼ 3. モンスター配置 (townマップのみ)
        # ---------------------------------------------------------
        # 安全地帯を取得 (Mapクラスのメソッドを活用)
        safe_zones = map_town.get_safe_zones()

        # ランダムに2箇所選ぶ
        if len(safe_zones) >= 2:
            spawn_points = random.sample(safe_zones, 2)
        else:
            spawn_points = [(10, 10), (11, 10)]  # フォールバック

        m1 = Monster(
            "ゴーレム",
            spawn_points[0][0],
            spawn_points[0][1],
            "monster_golem.png",
            questions=mixed_pool,
        )
        m2 = Monster(
            "トロール",
            spawn_points[1][0],
            spawn_points[1][1],
            "monster_troll.png",
            questions=mixed_pool,
        )

        # モンスター辞書を更新 (初期化時には空だったため)
        map_town.monsters = {(m.location_x, m.location_y): m for m in [m1, m2]}

        boss = Monster(
            name="王様",
            x=9,
            y=10,
            image_file="osama_boss.png",
            questions=mixed_pool,  # 問題は既存のプールを使用（専用の問題リストを作ってもOK）
        )

        map_castle.monsters = {(boss.location_x, boss.location_y): boss}

        return {
            "town": map_town,
            "market": map_market,  # 👈 追加
            "castle": map_castle,
        }

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
        return {"monster_name": self.name, "problem_text": self.problem_text}


class Monster:
    """マップ上のモンスターシンボルと、それに紐づく問題を管理するクラス。"""

    # ▼ 変更: question(単体) ではなく questions(リスト) を受け取る
    def __init__(
        self, name: str, x: int, y: int, image_file: str, questions: List[Question]
    ):
        self.name = name
        self.location_x = x
        self.location_y = y
        self.image_file = image_file
        self.questions = questions  # 👈 リストとして保存
        self.is_defeated = False
        self.battle_start_point = (x, y)

    def get_question(self) -> Question:
        # ▼ 変更: 戦闘開始のたびにリストからランダムに1問選んで返す
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
                if cell_type == 1:  # 1番は「壁（池や木）」と決める
                    self.blocked_cells.add((x, y))

    def is_blocked(self, x: int, y: int) -> bool:
        """指定された座標が通行禁止エリアかどうかを返す。"""
        return (x, y) in self.blocked_cells

    def get_safe_zones(self) -> List[Tuple[int, int]]:
        safe_spots = []
        for y, row in enumerate(self.map_data):
            for x, cell_type in enumerate(row):
                # 0番(道) かつ 施設などがない場所
                if cell_type == 0 and x > 6:
                    safe_spots.append((x, y))
        return safe_spots

    @staticmethod
    def initialize_maps():
        """初期マップデータを生成するファクトリメソッド。"""

        town_data = [
            # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 0
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 1
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],  # 2
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # 3
            [1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1],  # 4
            [1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1],  # 5
            [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0],  # 6
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0],  # 7
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0],  # 8
            [1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # 9
            [1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1],  # 10
            [1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],  # 11
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],  # 12
            [0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0],  # 13
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 14
        ]

        # ---------------------------------------------------------
        # ▼ 1. 問題プールの作成 (ここが今回の主役！)
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
        # ▼ 5. マップ生成
        # ---------------------------------------------------------
        map_town = Map(
            map_id="town",
            width=20,
            height=15,
            image_file="kenrokuen_map.png",
            monsters=[],
            facilities=[
                {"name": "アイテム屋", "x": 12, "y": 5, "type": "service"},
                {
                    "name": "金沢城へ",
                    "x": 18,
                    "y": 1,
                    "type": "transition",
                    "target_map": "castle",
                    "target_x": 2,
                    "target_y": 13,
                },
                {
                    "name": "金沢城へ",
                    "x": 17,
                    "y": 1,
                    "type": "transition",
                    "target_map": "castle",
                    "target_x": 2,
                    "target_y": 13,
                },
            ],
            map_data=town_data,
        )

        safe_zones = map_town.get_safe_zones()

        spawn_points = random.sample(safe_zones, 2)

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

        # 配置が決まったので登録し直す
        map_town.monsters = {(m.location_x, m.location_y): m for m in [m1, m2]}

        market_data = [[0] * 20 for _ in range(15)]
        # 周りだけ壁にするなら...
        for x in range(20):
            market_data[0][x] = 1
            market_data[14][x] = 1
        for y in range(15):
            market_data[y][0] = 1
            market_data[y][19] = 1

        map_market = Map(
            map_id="castle",
            width=20,
            height=15,
            image_file="Omicho_market.png",
            monsters=[],
            facilities=[
                {
                    "name": "兼六園へ",
                    "x": 2,
                    "y": 14,
                    "type": "transition",
                    "target_map": "town",
                    "target_x": 18,
                    "target_y": 2,
                },
            ],
            map_data=market_data,
        )

        return {
            "town": map_town,
            "castle": map_market,
        }

    # ... (以下のメソッドは変更なし) ...
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

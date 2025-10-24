# app/game/player.py

class Player:
    """
    主人公のステータスを管理するクラス。
    """
    INITIAL_HP = 10

    def __init__(self, start_x: int, start_y: int, map_id: str):
        self.hp = self.INITIAL_HP
        self.location_x = start_x
        self.location_y = start_y
        self.current_map = map_id

    def move(self, direction: str) -> bool:
        """
        指定された方向に移動し、座標を更新する。
        実際の移動可能判定はMapクラスで行うため、ここでは座標更新のみ。
        """
        # 簡易的な移動処理
        if direction == 'up':
            self.location_y -= 1
        elif direction == 'down':
            self.location_y += 1
        elif direction == 'left':
            self.location_x -= 1
        elif direction == 'right':
            self.location_x += 1
        
        # 座標が有効かどうかのチェック（Mapクラスで行うべきだが、ここでは単純にTrueを返す）
        return True

    def decrease_hp(self, damage: int):
        """
        HPを減少させる。
        """
        self.hp = max(0, self.hp - damage)

    def heal(self, amount: int):
        """
        HPを回復させる。
        """
        # MAX HPの概念を導入するなら、ここで制限をかける
        self.hp += amount
    
    def is_defeated(self) -> bool:
        """
        敗北判定 (HPが0以下か)。
        """
        return self.hp <= 0

    def get_status(self) -> dict:
        """
        現在のプレイヤー状態を辞書で返す (APIレスポンス用)。
        """
        return {
            'hp': self.hp,
            'x': self.location_x,
            'y': self.location_y,
            'map_id': self.current_map
        }
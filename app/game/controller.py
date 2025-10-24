# app/game/controller.py
from .player import Player
from .map import Map, Monster, Question
from typing import Dict, Optional

class GameController:
    """
    ゲームの状態を一元管理し、ロジックを実行するクラス。
    """
    def __init__(self):
        # 初期化
        self.maps = Map.initialize_maps()
        self.player = Player(start_x=4, start_y=8, map_id='town') # 初期位置
        self.current_map: Map = self.maps[self.player.current_map]
        self.current_battle: Optional[Monster] = None # 現在戦闘中のモンスター

    def _get_game_state(self) -> Dict:
        """
        現在のゲーム状態をまとめて返す（フロントエンドへのデータ）。
        """
        # マップ上のモンスターの位置と状態をフィルタリング
        active_monsters = [
            {'x': m.location_x, 'y': m.location_y, 'name': m.name}
            for m in self.current_map.monsters.values() if not m.is_defeated
        ]

        return {
            'player': self.player.get_status(),
            'current_map_id': self.current_map.map_id,
            'monsters': active_monsters,
            # 施設情報なども必要に応じて含める
        }

    # --- API連携メソッド ---

    def handle_move(self, direction: str) -> Dict:
        """
        移動操作を受け付け、衝突判定を行い、必要に応じて戦闘やマップ遷移をトリガーする。
        """
        # 1. 座標を仮更新
        original_x, original_y = self.player.location_x, self.player.location_y
        self.player.move(direction) # Playerの座標を更新

        new_x, new_y = self.player.location_x, self.player.location_y

        # 2. 衝突判定
        collision = self.current_map.check_collision(new_x, new_y)

        if collision:
            entity_type = collision['type']
            entity = collision['entity']

            if entity_type == 'monster':
                # モンスターと接触 -> 戦闘開始
                self.current_battle = entity
                self.player.location_x, self.player.location_y = original_x, original_y # 戦闘はシンボルが重なった場所で発生、移動はしない
                return self._start_battle(self.current_battle)

            elif entity_type == 'facility':
                # 施設（入口など）と接触 -> マップ切り替えまたはサービス提供
                if 'target_map' in entity:
                    # マップ切り替えの処理...（ここでは未実装。別マップの初期化が必要）
                    pass
                # アイテム屋などのサービス提供処理
                if entity.get('type') == 'service':
                    self.player.heal(5) # 例：アイテム屋でHP回復
                
                # 移動はそのまま許可される

        # 衝突なし、または施設への移動は完了
        return {'status': 'moved', 'game_state': self._get_game_state()}

    def _start_battle(self, monster: Monster) -> Dict:
        """
        戦闘画面に必要なデータを返す。
        """
        question_data = monster.get_question().to_dict()
        return {
            'status': 'battle',
            'monster_hp': monster.question.damage_on_failure * 2, # 簡易的なHP表示
            'player_hp': self.player.hp,
            'question': question_data,
            # ここで選択肢（たたかう、アイテムなど）の情報を渡す
            'actions': ['たたかう', 'にげる'],
            'game_state': self._get_game_state()
        }

    def submit_answer(self, action: str, answer: Optional[str] = None) -> Dict:
        """
        戦闘中のアクション（回答）を受け付け、結果を処理する。
        """
        if not self.current_battle:
            return {'status': 'error', 'message': '現在戦闘中ではありません。'}

        monster = self.current_battle
        question = monster.get_question()
        
        if action == 'たたかう' and answer is not None:
            is_correct = question.check_answer(answer)
            
            if is_correct:
                # 勝利
                monster.is_defeated = True
                self.current_battle = None
                return {
                    'status': 'battle_win', 
                    'message': f'{question.problem_text}の答えは正解！{monster.name}を倒しました。',
                    'game_state': self._get_game_state()
                }
            else:
                # 敗北（不正解）
                damage = question.damage_on_failure
                self.player.decrease_hp(damage)

                if self.player.is_defeated():
                    # HPが0になった場合
                    self.current_battle = None
                    # マップ上のモンスターはそのまま残る（消滅しない）
                    # プレイヤーを戦闘開始地点に戻す処理はここでは割愛（簡易化のため）
                    return {
                        'status': 'game_over', 
                        'message': f'不正解！HPが0になりました。ゲームオーバー...',
                        'game_state': self._get_game_state()
                    }
                else:
                    # HPが残っている場合
                    return {
                        'status': 'battle_continue', 
                        'message': f'不正解！{damage}のダメージを受けました。残りHP: {self.player.hp}',
                        'question': question.to_dict(), # 問題を再表示
                        'game_state': self._get_game_state()
                    }
        
        # その他（にげる、アイテムなど）
        self.current_battle = None
        return {'status': 'battle_end', 'message': '戦闘から離脱しました。', 'game_state': self._get_game_state()}
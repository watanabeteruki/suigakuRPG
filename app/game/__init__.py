# app/game/__init__.py (インポートの簡略化の例)

# 例: 'app.game' から直接 Player, Map をインポートできるようにする
from .player import Player
from .map import Map, Monster, Question
from .controller import GameController
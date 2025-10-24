// static/js/ui_renderer.js

/**
 * 画面描画とUI更新を担当するオブジェクト (FrontendUIの実装)。
 */
const UIRenderer = {
    // 画面要素のキャッシュ
    mapScreen: document.getElementById('map-screen'),
    battleScreen: document.getElementById('battle-screen'),
    mapGrid: document.getElementById('map-grid'),

    // --- 画面切り替え ---

    /**
     * 指定された画面に切り替える。
     * @param {string} screenId 'map' または 'battle'
     */
    switchScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        if (screenId === 'map') {
            this.mapScreen.classList.add('active');
        } else if (screenId === 'battle') {
            this.battleScreen.classList.add('active');
        }
    },

    // --- ステータス表示 ---

    /**
     * プレイヤーのHPステータスを更新する。
     * @param {object} playerStatus - { hp, x, y, map_id }
     */
    updatePlayerStatus(playerStatus) {
        const statusHTML = `HP: ${playerStatus.hp}`;
        document.getElementById('player-status-map').innerHTML = statusHTML;
        document.getElementById('player-status-battle').innerHTML = statusHTML;
    },

    // --- マップ画面描画 ---

    /**
     * マップ画面全体を描画・更新する。
     * @param {object} gameState - GameControllerから返される状態データ
     */
    renderMap(gameState) {
        const { player, monsters } = gameState;
        
        // 1. プレイヤーHPの更新
        this.updatePlayerStatus(player);

        // 2. マップ要素の描画
        // マップグリッドを一旦クリア
        this.mapGrid.innerHTML = '';
        
        // プレイヤーシンボルの描画
        const playerEl = document.createElement('div');
        playerEl.className = 'player-symbol';
        playerEl.textContent = '主';
        // CSS Gridの座標に配置 (1から始まるため +1)
        playerEl.style.gridColumnStart = player.x + 1;
        playerEl.style.gridRowStart = player.y + 1;
        this.mapGrid.appendChild(playerEl);

        // モンスターシンボルの描画
        monsters.forEach(m => {
            const monsterEl = document.createElement('div');
            monsterEl.className = 'monster-symbol';
            monsterEl.textContent = 'M';
            monsterEl.style.gridColumnStart = m.x + 1;
            monsterEl.style.gridRowStart = m.y + 1;
            this.mapGrid.appendChild(monsterEl);
        });

        // TODO: 施設シンボルの描画もここに追加する
        
        this.switchScreen('map');
    },

    // --- 戦闘画面描画 ---

    /**
     * 戦闘画面を描画・更新する。
     * @param {object} battleData - GameControllerから返される戦闘データ
     */
    renderBattle(battleData) {
        this.updatePlayerStatus(battleData.game_state.player);
        
        document.getElementById('monster-name').textContent = battleData.question.monster_name;
        document.getElementById('problem-text').textContent = battleData.question.problem_text;
        document.getElementById('battle-message').textContent = 'たたかう を選んで回答を入力してください。';

        this.switchScreen('battle');
    },

    /**
     * 戦闘メッセージを更新する。
     * @param {string} message - 表示するメッセージ
     */
    updateBattleMessage(message) {
        document.getElementById('battle-message').textContent = message;
    }
};
// static/js/ui_renderer.js

const UIRenderer = {
    mapScreen: document.getElementById('map-screen'),
    battleScreen: document.getElementById('battle-screen'),
    mapGrid: document.getElementById('map-grid'),

    switchScreen(screenId) {
        // すべての画面から active クラスを外す
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // 指定された画面を表示する
        if (screenId === 'map') {
            this.mapScreen.classList.add('active');
        } else if (screenId === 'battle') {
            this.battleScreen.classList.add('active');
            document.getElementById('battle-actions').style.display = 'block';
        } 
        // ▼▼▼ 追加: クリア画面とスタート画面の処理 ▼▼▼
        else if (screenId === 'clear') {
            document.getElementById('clear-screen').classList.add('active');
        }
        else if (screenId === 'start') {
            document.getElementById('start-screen').classList.add('active');
        }
        // ▲▲▲ 追加終わり ▲▲▲
        
        // 戦闘が終わったらコマンドを隠す
        if (screenId !== 'battle') {
            const battleActions = document.getElementById('battle-actions');
            if (battleActions) {
                battleActions.style.display = 'none';
            }
        }
    },

    updatePlayerStatus(playerStatus) {
        const statusHTML = `HP: ${playerStatus.hp}`;
        document.getElementById('player-status').innerHTML = statusHTML;
    },

    renderMap(gameState) {
        const { player, monsters, background_image } = gameState;
        
        this.updatePlayerStatus(player);

        this.mapGrid.innerHTML = '';

        if (background_image) {
            this.mapGrid.style.backgroundImage = `url('assets/${background_image}')`;
        }
        
        const playerIcon = document.createElement('div');
        playerIcon.classList.add('player');
        playerIcon.id = 'player-icon';
        playerIcon.style.gridColumnStart = player.x + 1;
        playerIcon.style.gridRowStart = player.y + 1;
        
        const playerImage = document.createElement('img');
        playerImage.src = 'assets/player_pixel.png'; 
        playerIcon.appendChild(playerImage);
        
        this.mapGrid.appendChild(playerIcon);

        monsters.forEach(m => {
            const monsterEl = document.createElement('div');
            monsterEl.className = 'monster-symbol';

            // ▼▼▼ 追加: 名前が「王様」なら boss クラスを追加 ▼▼▼
            if (m.name === '王様') {
                monsterEl.classList.add('boss');
            }
            
            const monsterImage = document.createElement('img');
            monsterImage.src = 'assets/' + m.image_file; 
            monsterEl.appendChild(monsterImage);
            
            monsterEl.style.gridColumnStart = m.x + 1;
            monsterEl.style.gridRowStart = m.y + 1;
            this.mapGrid.appendChild(monsterEl);
        });
    },

    renderBattle(battleData) {
        this.updatePlayerStatus(battleData.game_state.player);
        
        document.getElementById('monster-name').textContent = battleData.monster_name;
        document.getElementById('problem-text').textContent = battleData.question.problem_text;
        document.getElementById('battle-message').textContent = 'たたかう を選んで回答を入力してください。';
        document.getElementById('monster-image').src = 'assets/' + battleData.monster_image_file;

        this.switchScreen('battle');
    },

    updateBattleMessage(message) {
        document.getElementById('battle-message').textContent = message;
    }
};
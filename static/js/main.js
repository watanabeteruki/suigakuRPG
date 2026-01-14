// static/js/main.js

let isMoving = false; // 移動中フラグ (ラグ防止)

/**
 * 戦闘コマンドの有効/無効を切り替える
 */
function setBattleControlsEnabled(enabled) {
    document.getElementById('action-attack').disabled = !enabled;
    document.getElementById('action-flee').disabled = !enabled;
    document.getElementById('answer-input').disabled = !enabled;
    document.getElementById('submit-answer').disabled = !enabled;
}

/**
 * バックエンドAPIへのリクエストを行うヘルパー関数
 */
async function callApi(endpoint, data = {}) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    
    if (!response.ok) {
        const error = await response.json();
        console.error('API Error:', error);
        alert(`エラーが発生しました: ${error.message}`);
        return null;
    }
    
    return response.json();
}

/**
 * キーボードまたはボタン操作に基づいて移動を処理する関数。
 */
async function handleMove(direction) {
    
    if (isMoving) return;
    isMoving = true;

    const result = await callApi('/api/move', { direction: direction });
    
    if (result) {
        if (result.status === 'battle') {
            UIRenderer.renderBattle(result);
            setBattleControlsEnabled(true);
        } else if (result.status === 'moved') {
            UIRenderer.renderMap(result.game_state);
        
        // ▼▼▼ 追加: ゲームクリア時の処理 ▼▼▼
        } else if (result.status === 'game_clear') {
            // まず最後の位置（ゴール地点）を描画してから切り替え
            UIRenderer.renderMap(result.game_state);
            setTimeout(() => {
                UIRenderer.switchScreen('clear');
            }, 100);
        }
        // ▲▲▲ 追加終わり ▲▲▲
    }
    
    isMoving = false;
}

/**
 * ゲームのメイン処理とイベントリスナーの設定
 */
async function initializeGame() {
    // 1. 初期状態の取得と描画
    const initialState = await fetch('/api/status').then(res => res.json());
    if (initialState) {
        UIRenderer.renderMap(initialState);
    }

    // 2. マップ操作ボタンのイベントリスナー設定
    document.getElementById('map-controls').addEventListener('click', (event) => {
        if (event.target.tagName !== 'BUTTON') return;
        
        const direction = event.target.dataset.direction;
        if (direction) {
            handleMove(direction);
        }
    });

    // 3. キーボードイベントリスナーの設定
    document.addEventListener('keydown', (event) => {
        if (!UIRenderer.mapScreen.classList.contains('active')) {
            return;
        }
        
        let direction = null;
        switch (event.key) {
            case 'ArrowUp': case 'w': case 'W':
                direction = 'up'; break;
            case 'ArrowDown': case 's': case 'S':
                direction = 'down'; break;
            case 'ArrowLeft': case 'a': case 'A':
                direction = 'left'; break;
            case 'ArrowRight': case 'd': case 'D':
                direction = 'right'; break;
        }

        if (direction) {
            event.preventDefault();
            handleMove(direction);
        }
    });

    // 4. 戦闘アクションのイベントリスナー設定
    document.getElementById('submit-answer').addEventListener('click', async () => {
        const answerInput = document.getElementById('answer-input');
        const answer = answerInput.value.trim();
        answerInput.value = '';
        
        if (answer === '') {
            UIRenderer.updateBattleMessage('回答を入力してください！');
            return;
        }

        const result = await callApi('/api/battle/action', {
            action: 'たたかう',
            answer: answer
        });

        if (result) {
            UIRenderer.updatePlayerStatus(result.game_state.player);
            UIRenderer.updateBattleMessage(result.message);

            if (result.status === 'game_over') {
                setBattleControlsEnabled(false);
                setTimeout(async () => {
                    alert("ゲームオーバー...。初期状態に戻ります。");
                    const resetState = await callApi('/api/reset', {});
                    UIRenderer.renderMap(resetState);
                    UIRenderer.switchScreen('map');
                }, 2000);
            
            } else if (result.status === 'battle_win' || result.status === 'battle_end') {
                setBattleControlsEnabled(false);
                setTimeout(() => {
                    UIRenderer.renderMap(result.game_state);
                    UIRenderer.switchScreen('map');
                }, 2000);
            }
        }
    });

    document.getElementById('action-flee').addEventListener('click', async () => {
        const result = await callApi('/api/battle/action', { action: 'にげる' });
        if (result) {
            setBattleControlsEnabled(false);
            UIRenderer.updateBattleMessage(result.message);
            setTimeout(() => {
                UIRenderer.renderMap(result.game_state);
                UIRenderer.switchScreen('map');
            }, 2000);
        }
    });

    // 5. スタートボタンのイベントリスナー設定
    document.getElementById('start-game-button').addEventListener('click', () => {
        UIRenderer.switchScreen('map');
    });
    
    // ▼▼▼ 追加: タイトルに戻るボタンの設定 ▼▼▼
    const backButton = document.getElementById('back-to-title-button');
    if (backButton) {
        backButton.addEventListener('click', async () => {
            // サーバーの状態をリセット
            await callApi('/api/reset', {});
            // タイトル画面へ
            UIRenderer.switchScreen('start');
        });
    }
    // ▲▲▲ 追加終わり ▲▲▲

    const mapGrid = document.getElementById('map-grid');
    mapGrid.addEventListener('click', (event) => {
        const rect = mapGrid.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const clickY = event.clientY - rect.top;
        const cellWidth = rect.width / 20;
        const cellHeight = rect.height / 15;
        const x = Math.floor(clickX / cellWidth);
        const y = Math.floor(clickY / cellHeight);
        console.log(`この場所の座標: (${x}, ${y})`);
        alert(`座標: x=${x}, y=${y}`);
    });
}

// ページロード時にゲームを開始
document.addEventListener('DOMContentLoaded', initializeGame);
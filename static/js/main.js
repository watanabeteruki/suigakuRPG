// static/js/main.js

/**
 * バックエンドAPIへのリクエストを行うヘルパー関数
 * @param {string} endpoint - APIエンドポイントのパス (例: /api/move)
 * @param {object} data - 送信するデータ
 * @returns {Promise<object>} APIレスポンスデータ
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
 * @param {string} direction - 'up', 'down', 'left', 'right'
 */
async function handleMove(direction) {
    const result = await callApi('/api/move', { direction: direction });
    
    if (result) {
        if (result.status === 'battle') {
            // モンスターと接触 -> 戦闘画面へ
            UIRenderer.renderBattle(result);
        } else if (result.status === 'moved') {
            // 移動のみ -> マップ更新
            UIRenderer.renderMap(result.game_state);
        }
    }
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
        // 現在マップ画面が表示されているか確認
        if (!UIRenderer.mapScreen.classList.contains('active')) {
            return; // 戦闘画面など、他の画面ではキー操作を無視
        }
        
        let direction = null;

        // キー名で判定 (ArrowキーとWASDキー)
        switch (event.key) {
            case 'ArrowUp':
            case 'w':
            case 'W':
                direction = 'up';
                break;
            case 'ArrowDown':
            case 's':
            case 'S':
                direction = 'down';
                break;
            case 'ArrowLeft':
            case 'a':
            case 'A':
                direction = 'left';
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                direction = 'right';
                break;
        }

        if (direction) {
            // デフォルトのブラウザ動作（スクロールなど）を抑制
            event.preventDefault(); 
            // 移動処理を実行
            handleMove(direction);
        }
    });

    // 4. 戦闘アクションのイベントリスナー設定
    document.getElementById('submit-answer').addEventListener('click', async () => {
        const answerInput = document.getElementById('answer-input');
        const answer = answerInput.value.trim();
        answerInput.value = ''; // 入力欄をクリア
        
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

            if (result.status === 'battle_win' || result.status === 'game_over' || result.status === 'battle_end') {
                // 勝利・敗北・逃走の場合、少し待ってマップ画面に戻る
                setTimeout(() => {
                    UIRenderer.renderMap(result.game_state);
                }, 2000);
            }
        }
    });

    // 逃げるボタンの処理
    document.getElementById('action-flee').addEventListener('click', async () => {
        const result = await callApi('/api/battle/action', { action: 'にげる' });
        if (result) {
            UIRenderer.updateBattleMessage(result.message);
            setTimeout(() => {
                UIRenderer.renderMap(result.game_state);
            }, 2000);
        }
    });
}

// ページロード時にゲームを開始
document.addEventListener('DOMContentLoaded', initializeGame);
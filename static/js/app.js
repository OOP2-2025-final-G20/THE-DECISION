// APIベースURL
const API_BASE = '/api';

// グローバル変数
let currentQuestionId = null;
let currentEditingId = null;

// ページ表示管理
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    
    // 各ページの初期化
    if (pageId === 'question-page') {
        loadQuestion();
    } else if (pageId === 'history-page') {
        loadHistory();
    } else if (pageId === 'edit-list-page') {
        loadEditList();
    }
}

// API呼び出し関数
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API呼び出しエラー:', error);
        alert('エラーが発生しました: ' + error.message);
        throw error;
    }
}

// お題を読み込む
async function loadQuestion() {
    try {
        const question = await apiCall('/question');
        currentQuestionId = question.id;
        document.getElementById('question-text').textContent = `Q. ${question.q}`;
        document.getElementById('option-a-text').textContent = question.a;
        document.getElementById('option-b-text').textContent = question.b;
    } catch (error) {
        document.getElementById('question-text').textContent = 'Q. お題の読み込みに失敗しました';
    }
}

// 投票
async function vote(choice) {
    if (!currentQuestionId) {
        alert('お題が読み込まれていません');
        return;
    }
    
    try {
        await apiCall('/vote', 'POST', {
            question_id: currentQuestionId,
            choice: choice
        });
        
        // 結果ページに移動
        showPage('result-page');
        loadResults();
    } catch (error) {
        alert('投票に失敗しました');
    }
}

// 結果を読み込む
async function loadResults() {
    try {
        const results = await apiCall(`/results?question_id=${currentQuestionId}`);
        
        // 結果を非表示にして、ボタンを表示
        document.getElementById('result-content').classList.add('hidden');
        document.getElementById('open-result-btn').style.display = 'block';
        
        // 結果データを保存
        window.resultData = results;
    } catch (error) {
        alert('結果の読み込みに失敗しました');
    }
}

// 結果をオープン
function openResult() {
    const results = window.resultData;
    if (!results) return;
    
    // ボタンを非表示
    document.getElementById('open-result-btn').style.display = 'none';
    
    // 結果を表示
    const resultContent = document.getElementById('result-content');
    resultContent.classList.remove('hidden');
    
    const barA = document.getElementById('bar-a');
    const barB = document.getElementById('bar-b');
    const barAText = document.getElementById('bar-a-text');
    const barBText = document.getElementById('bar-b-text');
    
    // テキストを設定
    barAText.textContent = `${results.optionA}: ${results.votes_A}票 (${results.percentage_A}%)`;
    barBText.textContent = `${results.optionB}: ${results.votes_B}票 (${results.percentage_B}%)`;
    
    // アニメーションでバーを表示
    setTimeout(() => {
        const maxWidth = 300;
        const widthA = (results.votes_A / results.total) * maxWidth;
        const widthB = (results.votes_B / results.total) * maxWidth;
        
        barA.style.width = `${widthA}px`;
        barB.style.width = `${widthB}px`;
    }, 100);
}

// 問題を作成
async function createQuestion() {
    const q = document.getElementById('create-question').value.trim();
    const a = document.getElementById('create-option-a').value.trim();
    const b = document.getElementById('create-option-b').value.trim();
    
    if (!q || !a || !b) {
        alert('すべての項目を入力してください');
        return;
    }
    
    try {
        await apiCall('/question', 'POST', { q, a, b });
        alert('問題を登録しました');
        
        // フォームをクリア
        document.getElementById('create-question').value = '';
        document.getElementById('create-option-a').value = '';
        document.getElementById('create-option-b').value = '';
        
        // トップページに戻る
        showPage('top-page');
    } catch (error) {
        alert('問題の登録に失敗しました');
    }
}

// 履歴を読み込む
async function loadHistory() {
    try {
        const history = await apiCall('/history');
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        if (history.length === 0) {
            historyList.innerHTML = '<li>履歴がありません</li>';
            return;
        }
        
        history.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            historyList.appendChild(li);
        });
    } catch (error) {
        alert('履歴の読み込みに失敗しました');
    }
}

// 編集リストを読み込む
async function loadEditList() {
    try {
        const questions = await apiCall('/questions');
        const editList = document.getElementById('edit-list');
        editList.innerHTML = '';
        
        if (questions.length === 0) {
            editList.innerHTML = '<li>問題がありません</li>';
            return;
        }
        
        questions.forEach(q => {
            const li = document.createElement('li');
            li.className = 'edit-item-container';
            
            const itemDiv = document.createElement('div');
            itemDiv.className = 'edit-item';
            
            const title = document.createElement('div');
            title.className = 'edit-item-title';
            title.textContent = q.q;
            
            const subtitle = document.createElement('div');
            subtitle.className = 'edit-item-subtitle';
            subtitle.textContent = `A: ${q.a} / B: ${q.b}`;
            
            itemDiv.appendChild(title);
            itemDiv.appendChild(subtitle);
            
            const actions = document.createElement('div');
            actions.className = 'edit-actions';
            
            const editBtn = document.createElement('button');
            editBtn.className = 'edit-btn';
            editBtn.innerHTML = '✏️';
            editBtn.onclick = () => editQuestion(q.id);
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.innerHTML = '🗑️';
            deleteBtn.onclick = () => deleteQuestion(q.id);
            
            actions.appendChild(editBtn);
            actions.appendChild(deleteBtn);
            
            li.appendChild(itemDiv);
            li.appendChild(actions);
            editList.appendChild(li);
        });
    } catch (error) {
        alert('編集リストの読み込みに失敗しました');
    }
}

// 問題を編集
function editQuestion(questionId) {
    currentEditingId = questionId;
    
    // 問題データを取得
    apiCall(`/question/${questionId}`)
        .then(question => {
            document.getElementById('edit-question').value = question.q;
            document.getElementById('edit-option-a').value = question.a;
            document.getElementById('edit-option-b').value = question.b;
            showPage('edit-detail-page');
        })
        .catch(error => {
            alert('問題の読み込みに失敗しました');
        });
}

// 編集を保存
async function saveEdit() {
    if (!currentEditingId) {
        alert('編集する問題が選択されていません');
        return;
    }
    
    const q = document.getElementById('edit-question').value.trim();
    const a = document.getElementById('edit-option-a').value.trim();
    const b = document.getElementById('edit-option-b').value.trim();
    
    if (!q || !a || !b) {
        alert('すべての項目を入力してください');
        return;
    }
    
    try {
        await apiCall(`/question/${currentEditingId}`, 'PUT', { q, a, b });
        alert('変更を保存しました');
        showPage('edit-list-page');
        loadEditList();
    } catch (error) {
        alert('変更の保存に失敗しました');
    }
}

// 問題を削除
async function deleteQuestion(questionId) {
    if (!confirm('この問題を削除しますか？')) {
        return;
    }
    
    try {
        await apiCall(`/question/${questionId}`, 'DELETE');
        alert('問題を削除しました');
        loadEditList();
    } catch (error) {
        alert('問題の削除に失敗しました');
    }
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    // トップページを表示
    showPage('top-page');
});

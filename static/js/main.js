// DOM要素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const btnSelect = document.getElementById('btnSelect');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const btnRemove = document.getElementById('btnRemove');
const btnConvert = document.getElementById('btnConvert');
const resultSection = document.getElementById('resultSection');
const resultText = document.getElementById('resultText');
const btnDownload = document.getElementById('btnDownload');
const errorSection = document.getElementById('errorSection');
const errorText = document.getElementById('errorText');
const btnRetry = document.getElementById('btnRetry');
const loading = document.getElementById('loading');

// グローバル変数
let selectedFile = null;
let downloadData = null;

// 初期化
function init() {
    // イベントリスナーを設定
    btnSelect.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    btnRemove.addEventListener('click', handleFileRemove);
    btnConvert.addEventListener('click', handleConvert);
    btnDownload.addEventListener('click', handleDownload);
    btnRetry.addEventListener('click', handleRetry);

    // ドラッグ&ドロップイベント
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
}

// ファイル選択処理
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        validateAndSetFile(file);
    }
}

// ドラッグオーバー
function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('drag-over');
}

// ドラッグリーブ
function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('drag-over');
}

// ドロップ
function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    if (file) {
        validateAndSetFile(file);
    }
}

// ファイルのバリデーションと設定
function validateAndSetFile(file) {
    // 拡張子チェック
    if (!file.name.endsWith('.csv')) {
        showError('CSVファイルのみアップロード可能です');
        return;
    }

    // サイズチェック（5MB）
    if (file.size > 5 * 1024 * 1024) {
        showError('ファイルサイズが5MBを超えています');
        return;
    }

    // ファイルを設定
    selectedFile = file;
    
    // UIを更新
    uploadArea.style.display = 'none';
    fileInfo.style.display = 'flex';
    fileName.textContent = `📄 ${file.name} (${formatFileSize(file.size)})`;
    btnConvert.disabled = false;
    
    // エラー・結果をクリア
    hideError();
    hideResult();
}

// ファイル削除
function handleFileRemove() {
    selectedFile = null;
    fileInput.value = '';
    
    // UIをリセット
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
    btnConvert.disabled = true;
    
    hideError();
    hideResult();
}

// 変換処理
async function handleConvert() {
    if (!selectedFile) return;

    // ローディング表示
    showLoading();
    hideError();
    hideResult();

    try {
        // FormDataを作成
        const formData = new FormData();
        formData.append('file', selectedFile);

        // APIリクエスト
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 成功
            downloadData = {
                tempPath: data.temp_path,
                filename: data.filename
            };

            resultText.textContent = `${data.count}件の注文を変換しました`;
            showResult();
        } else {
            // エラー
            showError(data.error || '変換に失敗しました');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('通信エラーが発生しました。もう一度お試しください。');
    } finally {
        hideLoading();
    }
}

// ダウンロード処理
async function handleDownload() {
    if (!downloadData) return;

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                content: downloadData.content,
                filename: downloadData.filename
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = downloadData.filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            showError('ダウンロードに失敗しました');
        }
    } catch (error) {
        console.error('Download error:', error);
        showError('ダウンロード中にエラーが発生しました');
    }
}


// リトライ処理
function handleRetry() {
    hideError();
    hideResult();
    handleFileRemove();
}

// ローディング表示
function showLoading() {
    loading.style.display = 'flex';
}

function hideLoading() {
    loading.style.display = 'none';
}

// 結果表示
function showResult() {
    resultSection.style.display = 'block';
}

function hideResult() {
    resultSection.style.display = 'none';
}

// エラー表示
function showError(message) {
    errorText.textContent = message;
    errorSection.style.display = 'block';
}

function hideError() {
    errorSection.style.display = 'none';
}

// ファイルサイズをフォーマット
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ページ読み込み時に初期化
document.addEventListener('DOMContentLoaded', init);

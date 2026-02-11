# BASE → クリックポスト CSV変換ツール

BASEの注文CSVをクリックポストのまとめ申し込み用CSVに自動変換するWebアプリケーションです。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)

## 🚀 主な機能

- ✅ **簡単アップロード**: ドラッグ&ドロップまたはファイル選択でCSVをアップロード
- ✅ **自動変換**: BASEの注文データをクリックポスト形式に自動変換
- ✅ **即座にダウンロード**: 変換後すぐにダウンロード可能
- ✅ **安全性**: アップロードされたファイルは処理後すぐに削除
- ✅ **レスポンシブデザイン**: PC・スマホ・タブレット対応
- ✅ **エンコーディング自動検出**: UTF-8、Shift-JIS両方に対応

## 📋 機能詳細

### 入力（BASEの注文CSV）
- 注文ID
- 配送先情報（氏名、郵便番号、住所、電話番号）
- 商品情報

### 出力（クリックポスト用CSV）
- お届け先郵便番号（ハイフンなし7桁）
- お届け先氏名（全角20文字以内）
- お届け先敬称（「様」固定）
- お届け先住所1〜4行目（各20文字以内）
- 内容品（商品名、15文字以内）
- Shift-JISエンコーディング

### 制限事項
- 1回のアップロードで最大40件（クリックポストの制限）
- ファイルサイズ上限: 5MB
- 対応形式: CSV形式のみ

## 🛠️ 技術スタック

- **バックエンド**: Python 3.9+, Flask 3.0.0
- **フロントエンド**: HTML5, CSS3, Vanilla JavaScript
- **デプロイ**: 静的サイトホスティング対応

## 📦 プロジェクト構造

```
.
├── app.py                    # Flaskアプリケーション本体
├── requirements.txt          # Python依存パッケージ
├── Procfile                  # Herokuデプロイ設定
├── runtime.txt               # Pythonバージョン指定
├── vercel.json               # Vercelデプロイ設定
├── templates/
│   └── index.html           # メインHTML
├── static/
│   ├── css/
│   │   └── style.css        # スタイルシート
│   └── js/
│       └── main.js          # JavaScriptロジック
├── README.md                # このファイル
├── QUICKSTART.md            # クイックスタートガイド
└── .gitignore               # Git除外設定
```

## 🚀 ローカルでの起動方法

### 1. 必要な環境
- Python 3.9以上
- pip（Pythonパッケージマネージャー）

### 2. インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd base-to-clickpost-converter

# 仮想環境を作成（推奨）
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 3. アプリケーションを起動

```bash
python app.py
```

### 4. ブラウザでアクセス

```
http://localhost:5000
```

## 📖 使い方

### ステップ1: BASEから注文CSVをダウンロード
1. BASE管理画面にログイン
2. 「注文管理」をクリック
3. 「CSVダウンロード」でCSVファイルを取得

### ステップ2: ファイルをアップロード
1. Webアプリを開く
2. ドラッグ&ドロップまたは「ファイルを選択」ボタンをクリック
3. BASEからダウンロードしたCSVファイルを選択

### ステップ3: 変換
1. 「変換する」ボタンをクリック
2. 自動的にクリックポスト形式に変換されます

### ステップ4: ダウンロード
1. 変換完了後、「ダウンロード」ボタンをクリック
2. 変換済みCSVファイルをダウンロード

### ステップ5: クリックポストにアップロード
1. [クリックポスト公式サイト](https://clickpost.jp/)にアクセス
2. 「まとめ申込」をクリック
3. ダウンロードしたCSVファイルをアップロード

## 🌐 デプロイ方法

### Vercel（推奨）

1. [Vercel](https://vercel.com/)にサインアップ
2. GitHubリポジトリと連携
3. 自動的にデプロイされます

### Render

1. [Render](https://render.com/)にサインアップ
2. 「New Web Service」をクリック
3. GitHubリポジトリを選択
4. 以下の設定を入力：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

### Heroku

```bash
# Heroku CLIをインストール後
heroku login
heroku create your-app-name
git push heroku main
```

## 🔒 セキュリティ

- アップロードされたファイルは一時的にメモリに保存され、処理後すぐに削除されます
- ファイルサイズは5MBに制限されています
- CSVファイル以外はアップロードできません
- サーバーにユーザーデータは保存されません

## 🐛 トラブルシューティング

### Q: 変換エラーが発生する
**A**: 以下を確認してください：
- BASEから正しくCSVをダウンロードしているか
- ファイルが破損していないか
- ファイルサイズが5MB以下か

### Q: ダウンロードしたファイルが文字化けする
**A**: クリックポストはShift-JISを要求します。自動的にShift-JISで出力されますが、Excelで開く際は「データ」→「テキストファイル」→「Shift-JIS」を選択してください。

### Q: 40件以上の注文を変換したい
**A**: クリックポストの制限により、1回のアップロードは40件までです。複数回に分けて変換してください。

## 📄 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📧 お問い合わせ

質問や問題がある場合は、[Issues](https://github.com/yourusername/base-to-clickpost-converter/issues)を開いてください。

## 🙏 謝辞

ECサイト運営者の皆様の業務効率化に少しでも貢献できれば幸いです。

---

Made with ❤️ for EC sellers

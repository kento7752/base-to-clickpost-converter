from flask import Flask, request, jsonify, send_file, render_template
import csv
import io
import os
from collections import defaultdict
from datetime import datetime
import tempfile
import traceback

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB制限

# アップロード許可する拡張子
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """ファイル拡張子をチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def truncate_text(text, max_length):
    """テキストを指定文字数で切り詰める（全角・半角考慮）"""
    if not text:
        return ""
    
    length = 0
    result = ""
    for char in text:
        # 全角文字は2文字分、半角文字は1文字分としてカウント
        char_length = 2 if ord(char) > 127 else 1
        if length + char_length > max_length:
            break
        result += char
        length += char_length
    
    return result

def format_postal_code(postal_code):
    """郵便番号をハイフンなし7桁にフォーマット"""
    if not postal_code:
        return ""
    
    # 数字のみを抽出
    postal_code = ''.join(filter(str.isdigit, str(postal_code)))
    
    # 7桁に調整
    if len(postal_code) == 7:
        return postal_code
    elif len(postal_code) > 7:
        return postal_code[:7]
    else:
        return postal_code.zfill(7)

def split_address(prefecture, address1, address2, max_length=20):
    """住所を4行に分割（各行20文字以内）"""
    address_lines = ["", "", "", ""]
    
    # 1行目: 都道府県
    address_lines[0] = truncate_text(prefecture, max_length)
    
    # 2行目: 市区町村+町域
    address_lines[1] = truncate_text(address1, max_length)
    
    # 3行目: 番地・建物名
    if address2:
        address_lines[2] = truncate_text(address2, max_length)
    
    # 4行目は通常空欄
    
    return address_lines

def get_product_summary(products, max_length=15):
    """商品名リストから内容品を生成（15文字以内）"""
    if not products:
        return "商品"
    
    # 最初の商品名を使用
    first_product = products[0]
    # 改行・不要な文字を削除
    product_name = first_product.replace('\n', ' ').replace('\r', '').strip()
    
    return truncate_text(product_name, max_length)

def detect_encoding(file_content):
    """ファイルのエンコーディングを検出"""
    encodings = ['utf-8', 'shift-jis', 'cp932', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            file_content.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    
    # デフォルトはUTF-8でエラー無視
    return 'utf-8'

def convert_base_to_clickpost(base_csv_content):
    """BASEのCSVをクリックポスト形式に変換"""
    
    # エンコーディングを検出
    encoding = detect_encoding(base_csv_content)
    
    # CSVを読み込み
    csv_text = base_csv_content.decode(encoding, errors='replace')
    csv_file = io.StringIO(csv_text)
    reader = csv.reader(csv_file)
    
    # ヘッダーをスキップ
    next(reader)
    
    # 注文IDごとに商品をグループ化
    orders = defaultdict(lambda: {
        'postal_code': '',
        'name': '',
        'prefecture': '',
        'address1': '',
        'address2': '',
        'phone': '',
        'products': []
    })
    
    # データを読み込み
    for row in reader:
        if len(row) < 19:
            continue
        
        order_id = row[0]
        
        if not order_id or not order_id.strip():
            continue
        
        # 配送先情報を取得（最初の行のみ）
        if not orders[order_id]['postal_code']:
            orders[order_id]['postal_code'] = row[4] if len(row) > 4 else ''
            # 姓名を結合
            last_name = row[2] if len(row) > 2 else ''
            first_name = row[3] if len(row) > 3 else ''
            orders[order_id]['name'] = f"{last_name}{first_name}"
            orders[order_id]['prefecture'] = row[5] if len(row) > 5 else ''
            orders[order_id]['address1'] = row[6] if len(row) > 6 else ''
            orders[order_id]['address2'] = row[7] if len(row) > 7 else ''
            orders[order_id]['phone'] = row[8] if len(row) > 8 else ''
        
        # 商品情報を追加
        if len(row) > 18:
            product_name = row[18]
            if product_name and product_name.strip() and product_name != '商品名':
                # クーポン情報などネガティブ金額の商品は除外
                orders[order_id]['products'].append(product_name)
    
    # クリックポスト用CSVを生成
    output = io.StringIO()
    writer = csv.writer(output)
    
    # ヘッダー行
    writer.writerow([
        'お届け先郵便番号',
        'お届け先氏名',
        'お届け先敬称',
        'お届け先住所1行目',
        'お届け先住所2行目',
        'お届け先住所3行目',
        'お届け先住所4行目',
        '内容品'
    ])
    
    # データ行
    converted_count = 0
    for order_id, order_data in orders.items():
        # 必須項目のチェック
        if not order_data['postal_code'] or not order_data['name']:
            continue
        
        postal_code = format_postal_code(order_data['postal_code'])
        name = truncate_text(order_data['name'], 20)
        honorific = '様'
        
        address_lines = split_address(
            order_data['prefecture'],
            order_data['address1'],
            order_data['address2']
        )
        
        content = get_product_summary(order_data['products'])
        
        writer.writerow([
            postal_code,
            name,
            honorific,
            address_lines[0],
            address_lines[1],
            address_lines[2],
            address_lines[3],
            content
        ])
        
        converted_count += 1
        
        # 40件制限
        if converted_count >= 40:
            break
    
    # Shift-JISに変換
    output_content = output.getvalue()
    output_bytes = output_content.encode('shift-jis', errors='replace')
    
    return output_bytes, converted_count

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    """CSV変換エンドポイント"""
    try:
        # ファイルの存在チェック
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        file = request.files['file']
        
        # ファイル名チェック
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        # 拡張子チェック
        if not allowed_file(file.filename):
            return jsonify({'error': 'CSVファイルのみアップロード可能です'}), 400
        
        # ファイル内容を読み込み
        file_content = file.read()
        
        # サイズチェック
        if len(file_content) > 5 * 1024 * 1024:
            return jsonify({'error': 'ファイルサイズが5MBを超えています'}), 400
        
        # 変換処理
        converted_content, count = convert_base_to_clickpost(file_content)
        
        # 一時ファイルに保存
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        temp_file.write(converted_content)
        temp_file.close()
        
        # レスポンス用のファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'clickpost_{timestamp}.csv'
        
        return jsonify({
            'success': True,
            'count': count,
            'filename': output_filename,
            'temp_path': temp_file.name
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'変換中にエラーが発生しました: {str(e)}'}), 500

@app.route('/download/<path:temp_path>')
def download(temp_path):
    """変換済みファイルのダウンロード"""
    try:
        # セキュリティ: パスのバリデーション
        if not os.path.exists(temp_path) or not temp_path.startswith('/tmp/'):
            return jsonify({'error': 'ファイルが見つかりません'}), 404
        
        # ファイル名を取得
        filename = request.args.get('filename', 'clickpost.csv')
        
        # ファイルを送信
        response = send_file(
            temp_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
        # ダウンロード後にファイルを削除
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Failed to delete temp file: {e}")
        
        return response
    
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': 'ダウンロード中にエラーが発生しました'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """ファイルサイズ超過エラー"""
    return jsonify({'error': 'ファイルサイズが大きすぎます（最大5MB）'}), 413

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

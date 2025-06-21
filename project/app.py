from flask import Flask, request, render_template, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/upload')
DATA_FILE = os.path.join(BASE_DIR, 'data.txt')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 재료 정보 (단위 및 기본 데이터)
INGREDIENTS = {
    "garlic": {"name": "garlic", "unit": "piece", "per_click_amount": 1},
    "onion": {"name": "onion", "unit": "piece", "per_click_amount": 0.5},
    "mushroom": {"name": "mushroom", "unit": "piece", "per_click_amount": 1},
    "spinach": {"name": "spinach", "unit": "g", "per_click_amount": 10},
    "olive": {"name": "olive", "unit": "piece", "per_click_amount": 1},
    "pepper": {"name": "pepper", "unit": "piece", "per_click_amount": 1},
    "black_pepper": {"name": "black_pepper", "unit": "g", "per_click_amount": 2},
    "salt": {"name": "salt", "unit": "g", "per_click_amount": 2},
    "basil": {"name": "basil", "unit": "leaf", "per_click_amount": 1},
    "butter": {"name": "butter", "unit": "g", "per_click_amount": 10},
    "cheese": {"name": "cheese", "unit": "g", "per_click_amount": 10},
    "tomato": {"name": "tomato", "unit": "piece", "per_click_amount": 0.5},
    "anchovy": {"name": "anchovy", "unit": "piece", "per_click_amount": 1},
    "baccon": {"name": "baccon", "unit": "g", "per_click_amount": 10},
    "shrimp": {"name": "shrimp", "unit": "piece", "per_click_amount": 1},
    "chicken_stock": {"name": "chicken_stock", "unit": "g", "per_click_amount": 2},
    "spaghettini": {"name": "spaghettini", "unit": "serving", "per_click_amount": 1},
    "tagliatelle": {"name": "tagliatelle", "unit": "serving", "per_click_amount": 1},
    "regatoni": {"name": "regatoni", "unit": "serving", "per_click_amount": 1},
    "fusilli": {"name": "fusilli", "unit": "serving", "per_click_amount": 1},
    "milk": {"name": "milk", "unit": "ml", "per_click_amount": 20},
    "cream": {"name": "cream", "unit": "ml", "per_click_amount": 20},
    "tomato_paste": {"name": "tomato_paste", "unit": "g", "per_click_amount": 20},
    "olive_oil": {"name": "olive_oil", "unit": "ml", "per_click_amount": 5}
}

@app.route('/')
def home():
    image_folder = app.config['UPLOAD_FOLDER']
    all_images = sorted([f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    row1, row2, row3 = [], [], []
    for i, img in enumerate(all_images):
        if i % 3 == 0:
            row1.append(img)
        elif i % 3 == 1:
            row2.append(img)
        else:
            row3.append(img)
    return render_template('home.html', row1=row1, row2=row2, row3=row3)

@app.route('/ingredients', methods=['GET', 'POST'])
def ingredients():
    if request.method == 'POST':
        counts = request.form.get('counts')
        session['counts'] = counts
        return redirect(url_for('post'))
    ingredient_keys = list(INGREDIENTS.keys())
    initial_counts = { key: 0 for key in ingredient_keys }
    return render_template('ingredients.html', ingredient_keys=ingredient_keys, counts=initial_counts, ingredients=INGREDIENTS)

@app.route('/post')
def post():
    counts = session.get('counts', '{}')
    return render_template('post.html', counts=counts)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    title = request.form.get('title', '(No Title)')
    author = request.form.get('author', '(No Author)')  # 새로운 author 필드
    content = request.form.get('content', '')
    counts = session.get('counts', '{}')
    
    if file and content:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = {
            'filename': filename,
            'title': title,
            'author': author,
            'content': content,
            'timestamp': timestamp,
            'counts': json.loads(counts)
        }
        with open(DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return redirect(url_for('home'))

@app.route('/recipe/<filename>')
def recipe(filename):
    content, timestamp, saved_title, saved_author, counts = None, None, '(No Title)', '(No Author)', {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                if entry['filename'] == filename:
                    saved_title = entry.get('title', '(No Title)')
                    saved_author = entry.get('author', '(No Author)')
                    content = entry['content']
                    timestamp = entry['timestamp']
                    counts = entry['counts']
                    break

    if content is None:
        return "Recipe not found", 404

    date_only = timestamp.split(' ')[0]
    
    ingredient_display = {}
    for key, count in counts.items():
        count_int = int(count)
        if count_int != 0:
            name = INGREDIENTS.get(key, {}).get('name', key)
            unit = INGREDIENTS.get(key, {}).get('unit', '')
            ingredient_display[name] = f"{count_int} {unit}"

    content = content.replace('\n', '<br>')
    return render_template('recipe.html', image=filename, title=saved_title, author=saved_author, content=content, date=date_only, ingredients=ingredient_display)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

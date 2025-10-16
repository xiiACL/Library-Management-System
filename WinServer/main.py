import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # غيّرها عندك

# ربط SocketIO مع Flask باستخدام eventlet
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

import logging
from datetime import date, timedelta
import socket
from flask import jsonify, send_file,abort
import time
from downloader.downloaderscript import audio
from apscheduler.schedulers.background import BackgroundScheduler
import shutil

import os
import sqlite3
from flask import render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime


#######################IMPORT#######################


#######################SERVER SETTINGS#######################

UPLOAD_FOLDER = r"A:\Library\Python\FTP\FTP\uploads"
TEXT_STORAGE = []
TEXT_UPLOAD_FOLDER = r"A:\Library/Python/FTP/FTP/text"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
hostname = "192.168.1.177"
local_ip = socket.gethostbyname(hostname)
TEXT_FILE_PATH = r"A:\Library/Python/FTP/FTP/text/uploaded_texts.txt"
last_received_command = None
#app = Flask(__name__)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['image_folder'] = r"A:\Library\Python\FTP\FTP\uploads\bookimages"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['images_folder'] = r"A:\Library\Python\FTP\FTP\uploads\bookimages"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['backup_folder'] = 'backup'
os.makedirs(app.config['backup_folder'], exist_ok=True)
LOG_FILE = r"A:\Library/Python/FTP/FTP/log/book_logs"
DB_NAME = r"A:\Library/Python/FTP/FTP/ryadh.db"
LOG_FILE_RYADH = r"A:\Library/Python/FTP/FTP/log/ryadh.log"
if not os.path.exists(app.config['images_folder']):
    os.makedirs(app.config['images_folder'])

weeks_data = [
    [("الجمعة", 10, 2), ("السبت", 12, 2), ("الأحد", 15, 2), ("الاثنين", 10, 2), ("الثلاثاء", 15, 2), ("الأربعاء", 0, 0), ("الخميس", 20, 2)],
    [("الجمعة", 15, 3), ("السبت", 18, 3), ("الأحد", 20, 3), ("الاثنين", 15, 3), ("الثلاثاء", 20, 3), ("الأربعاء", 0, 0), ("الخميس", 25, 3)],
    [("الجمعة", 20, 4), ("السبت", 25, 4), ("الأحد", 15, 4), ("الاثنين", 20, 4), ("الثلاثاء", 25, 4), ("الأربعاء", 0, 0), ("الخميس", 30, 4)],
    [("الجمعة", 25, 5), ("السبت", 30, 5), ("الأحد", 20, 5), ("الاثنين", 25, 5), ("الثلاثاء", 30, 5), ("الأربعاء", 0, 0), ("الخميس", 35, 5)],
]


import secrets
secretcode = secrets.token_hex(16)  # يعطيك 32 حرف hex عشوائي


#######################SERVER SETTINGS#######################

#######################UNUSED COMNDS#######################

#is_muted = False

# @app.route('/toggle_mute')
# def toggle_mute():
#     global is_muted
#     render_template('toggle_mic.html',muted=False)
#
#
#     # Toggle the mute status
#     is_muted = not is_muted
#
#     # Return the updated mute state as JSON response
#     # UNUSED ONE
#     return jsonify(muted=is_muted)
#######

# @app.route('/vault')
# def load_passwords():
#     data = []
#     with open('NortonPasswordManager_06_13_25_09_16.csv', encoding='utf-8-sig') as f:
#         reader = csv.DictReader(f, delimiter=',')#        for row in reader:
# #            data.append(row)
#         for row in reader:
#             data.append(row)
#     return render_template('vault.html', data=data)
#######


#######################UNUSED COMNDS#######################

#######################UNUSED WINDOWS COMNDS#######################

# Function to handle quitting the app
def on_quit(icon, item):
    icon.stop()  # Stop the icon and the background task

# def run_server():
#     os.startfile(url)

def open_folder():
    os.startfile(r"A:\Library/Python/FTP/FTP")

#######################UNUSED WINDOWS COMNDS#######################

logging.basicConfig(
    filename='app.log',         # اسم ملف اللوج (هيتخلق في نفس مسار السكربت)
    level=logging.DEBUG,         # درجة التفاصيل (DEBUG عشان تسجل كل شي)
    format='%(asctime)s %(levelname)s: %(message)s',  # تنسيق السجل مع الوقت
    datefmt='%Y-%m-%d %H:%M:%S'
)
#######################DEF'S#######################

def start_server():
    init_db()
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=backup_db, trigger='interval', weeks=1)
    # scheduler.start()
    print("starting server...")
    socketio.run(app, host="192.168.1.177", port=5000,debug=True)
#######################DEF'S#######################

# Function that runs in a separate thread to print the received command
def print_command():
    global last_received_command
    while True:
        time.sleep(1)  # Sleep for a second before checking the command
        if last_received_command:
            print(f"Last received command: {last_received_command}")
            # Reset the command after printing, so it won't keep printing the same command
            last_received_command = None

#######################SERVER DEF'S#######################
#------> @app.route

@app.route('/')
def index():
    return render_template('index.html')
    # MAIN WINDOW

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/ser')
def ser():
    return render_template('server.html')
    # SHARE TEXT & FILES WINDOW

@app.route('/store')
def store():
    return render_template('store.html')
    # UNUSED STORE PAGE

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')
    # STUDY QUIZ EXAM
@app.route('/video')
def stream_video():
    video_dir = r"A:\Library/Python/MainTools/MainTool/streamd video"

    # List all mp4 files in the directory
    mp4_files = [f for f in os.listdir(video_dir) if f.lower().endswith('.mp4')]

    if not mp4_files:
        # No MP4 files found
        abort(404, description="No video file found.")

    # Pick the first mp4 file found
    video_path = os.path.join(video_dir, mp4_files[0])

    # Stream the video file
    return send_file(video_path, mimetype='video/mp4')
    # STREAM VIDEO PAGE ( CINEMA )

@app.route('/cmd', methods=['GET'])
def cmd():
    return render_template('cmd.html')
    # DISCORD COMMAND BOT


# Endpoint to receive the command and save it to the variable
@app.route('/cmd', methods=['GET'])
def save_command():
    global last_received_command
    command = request.args.get('cmd')  # Get the command from the query string
    if command:
        last_received_command = command  # Save it to the variable
        print(f"Command received: {command}")  # Print the received command to the console
        return jsonify({"status": "success", "command": last_received_command})
    return jsonify({"status": "error", "message": "No command received"}), 400
    # DISCORD COMMAND BOT #2
# Endpoint to check the last command saved
@app.route('/last_command', methods=['GET'])
def get_last_command():
    if last_received_command:
        return jsonify({"last_command": last_received_command})
    return jsonify({"status": "error", "message": "No command received yet"}), 404
    # DISCORD COMMAND BOT #3

@app.route('/get_data')
def get_data():
    load_texts_from_file()
    texts = TEXT_STORAGE

    files = os.listdir(UPLOAD_FOLDER)
    sorted_files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)), reverse=True)

    # Send current text file name (not full path)
    current_file = os.path.basename(TEXT_FILE_PATH)

    return jsonify({
        'texts': texts,
        'files': sorted_files,
        'current_file': current_file
    })
    # GET TEXT & FILES COMMAND

# Route to handle multiple file uploads
@app.route('/upload_files', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400  # Add error handling

    files = request.files.getlist('files')  # Get the list of files
    for file in files:
        if file.filename == '':
            continue  # Skip empty filenames
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    # Return success response with filenames
    return jsonify({'success': True, 'files': [file.filename for file in files]})
    # UPLOAD FILES COMMAND


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    # IDK

@app.route('/load_text_file', methods=['POST'])
def load_text_file():
    file_name = request.json.get('file_name')
    path = os.path.join('texts', file_name)  # assuming texts are stored in a 'texts/' folder

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            TEXT_STORAGE.clear()
            TEXT_STORAGE.extend(f.read().splitlines())
        return jsonify({'success': True, 'texts': TEXT_STORAGE})
    else:
        return jsonify({'success': False, 'error': 'File not found'}), 404
    # LOAD TEXT TO SERVER COMMAND

def load_texts_from_file():
    global TEXT_STORAGE
    if os.path.exists(TEXT_FILE_PATH):
        with open(TEXT_FILE_PATH, 'r', encoding='utf-8') as file:
            TEXT_STORAGE = [line.strip() for line in file.readlines() if line.strip()]
    # LOAD TEXT TO SERVER COMMAND

@app.route('/create_new_file', methods=['POST'])
def create_new_file():
    global TEXT_FILE_PATH, TEXT_STORAGE

    # Find next available file name
    i = 1
    base_name = "uploaded_texts"
    while True:
        new_path = os.path.join("texts", f"{base_name}{i}.txt")
        if not os.path.exists(new_path):
            break
        i += 1

    # Create the new file (empty)
    with open(new_path, 'w', encoding='utf-8') as f:
        pass

    # Switch the text file path
    TEXT_FILE_PATH = new_path

    # Clear in-memory and re-load (in this case will be empty)
    TEXT_STORAGE = []
    load_texts_from_file()  # In case file has any data (e.g., from other users)

    return jsonify({'success': True, 'new_file': new_path})
    # IDK COMMAND

@app.route('/load_file', methods=['POST'])
def load_file():
    filename = request.json.get('uploaded_texts')
    if not filename:
        return jsonify({'success': False, 'message': 'No filename provided'}), 400

    # Validate filename for security (optional: ensure no path traversal)
    if '/' in filename or '\\' in filename:
        return jsonify({'success': False, 'message': 'Invalid filename'}), 400

    full_path = os.path.join(TEXT_UPLOAD_FOLDER, filename)

    if not os.path.isfile(full_path):
        return jsonify({'success': False, 'message': 'File does not exist'}), 404

    global TEXT_FILE_PATH
    TEXT_FILE_PATH = full_path

    # Clear current in-memory text storage and reload from new file
    TEXT_STORAGE.clear()
    load_texts_from_file()

    return jsonify({'success': True, 'message': f'Loaded {filename}', 'current_file': filename})
    # IDK COMMAND

@app.route('/upload_text', methods=['POST'])
def upload_text():
    text = request.form.get('text')
    if text:
        TEXT_STORAGE.append(text)  # Add the text to memory
        print(text)
        with open(TEXT_FILE_PATH, 'a', encoding='utf-8') as file:
            file.write(text + '\n')  # Optionally save to a file for persistence
            print("Text Has been Uploaded")
    return jsonify({'success': True, 'texts': TEXT_STORAGE})
    # UPLOAD TEXT TO TEXT [] COMMAND

@app.route("/server")
def server():
    return render_template("/server.html")
    # LOAD SAHRE FILE AND TEXT PAGE COMMAND


from flask import Flask, render_template, request, flash, redirect, url_for
from flask_socketio import SocketIO
import threading
33
@app.route('/d', methods=['GET', 'POST'])
def downloader():
    url = ''

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            def emit_msg(event, data):
                socketio.emit(event, data)

            # شغل audio في Thread لتجنب حظر السيرفر
            def worker():
                try:
                    file_path, title = audio(url, emit=emit_msg)
                    # بعد ما يجهز الملف ابعث event للـ client
                    download_url = f"/download/{os.path.basename(file_path)}"
                    socketio.emit("download_ready", {"url": download_url, "title": title})
                except Exception as e:
                    emit_msg("progress", f"❌ Error: {str(e)}")

            threading.Thread(target=worker).start()

    return render_template("dow.html", url=url)




def backup_db():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    src = r"A:\Library\Python\FTP\FTP\books.db"
    dst = os.path.join(app.config['backup_folder'], f'books_backup_{timestamp}.db')
    shutil.copy2(src, dst)
    print(f"[✔] تم إنشاء نسخة احتياطية: {dst}")
    log_action(f"[✔] تم إنشاء نسخة احتياطية: {dst}")
    # BACKUP COMMAND

def log_action(action):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action}\n")
    # LOG COMMAND

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    # CHECK FILE COMMAND

def init_db():
    with sqlite3.connect(r"A:\Library\Python\FTP\FTP\books.db") as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                category TEXT,
                total_pages INTEGER,
                current_page INTEGER,
                purchase_date TEXT,
                last_read TEXT,
                book_format TEXT,
                cover_image TEXT,
                created_at TEXT,
                updated_at TEXT,
                series_name TEXT,
                series_part INTEGER
            )
        ''')
        conn.commit()
    # CREATE BOOKS TABLE IF NOT EXIST COMMAND

@app.route('/Books')
def books():
    search = request.args.get('q', '')
    sort = request.args.get('sort', '')
    query = "SELECT * FROM books"
    params = ()

    if search:
        query += " WHERE title LIKE ? OR author LIKE ? OR category LIKE ?"
        params = (f'%{search}%', f'%{search}%', f'%{search}%')

    if sort == 'created_at':
        query += " ORDER BY created_at DESC"
    else:
        query += " ORDER BY last_read DESC"

    with sqlite3.connect(r"A:\Library\Python\FTP\FTP\books.db") as conn:
        c = conn.cursor()
        c.execute(query, params)
        books = c.fetchall()

    return render_template('books3.html', books=books, search=search, sort=sort)
    # LOAD BOOKSHELF PAGE COMMAND

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        total_pages = int(request.form['total_pages'] or 0)
        current_page = int(request.form['current_page'] or 0)
        purchase_date = request.form['purchase_date']
        last_read = request.form['last_read']
        book_format = request.form['book_format']
        series_name = request.form.get('series_name')
        series_part = request.form.get('series_part') or None
        cover_image = None

        created_at = updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['images_folder'], filename))
                cover_image = filename

        with sqlite3.connect(r"A:\Library\Python\FTP\FTP\books.db") as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO books (title, author, category, total_pages, current_page, purchase_date, last_read,
                book_format, cover_image, created_at, updated_at, series_name, series_part)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, author, category, total_pages, current_page, purchase_date, last_read,
                  book_format, cover_image, created_at, updated_at, series_name, series_part))
            conn.commit()

        log_action(f"📘 تمت إضافة الكتاب: {title}")
        return redirect(url_for('books'))
    return render_template('add.html')
    # ADD BOOK TO BOOKSHELF COMMAND
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    with sqlite3.connect(r"A:\Library\Python\FTP\FTP\books.db") as conn:
        c = conn.cursor()
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            category = request.form['category']
            total_pages = int(request.form.get('total_pages', 0) or 0)
            current_page = int(request.form.get('current_page', 0) or 0)
            purchase_date = request.form['purchase_date']
            last_read = request.form['last_read']
            book_format = request.form['book_format']
            series_name = request.form.get('series_name')
            series_part = request.form.get('series_part') or None

            cover_image = None
            if 'cover_image' in request.files:
                file = request.files['cover_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['images_folder'], filename))
                    cover_image = filename

            updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if cover_image:
                c.execute('''
                    UPDATE books SET title=?, author=?, category=?, total_pages=?, current_page=?, purchase_date=?,
                    last_read=?, book_format=?, cover_image=?, updated_at=?, series_name=?, series_part=? WHERE id=?
                ''', (title, author, category, total_pages, current_page, purchase_date, last_read,
                      book_format, cover_image, updated_at, series_name, series_part, book_id))
            else:
                c.execute('''
                    UPDATE books SET title=?, author=?, category=?, total_pages=?, current_page=?, purchase_date=?,
                    last_read=?, book_format=?, updated_at=?, series_name=?, series_part=? WHERE id=?
                ''', (title, author, category, total_pages, current_page, purchase_date, last_read,
                      book_format, updated_at, series_name, series_part, book_id))

            conn.commit()
            log_action(f"📝 تم تعديل الكتاب: {title}")
            return redirect(url_for('books'))

        c.execute("SELECT * FROM books WHERE id=?", (book_id,))
        book = c.fetchone()
        return render_template('edit.html', book=book)
    # EDIT BOOK TO BOOKSHELF COMMAND

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    with sqlite3.connect(r"A:\Library\Python\FTP\FTP\books.db") as conn:
        c = conn.cursor()
        c.execute("SELECT title FROM books WHERE id=?", (book_id,))
        title = c.fetchone()[0]
        c.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
    log_action(f"🗑️ تم حذف الكتاب: {title}")
    # googlebackup("r"A:\Library\Python\FTP\FTP\books.db"")
    return redirect(url_for('books'))
    # REMOVE-DELETE BOOK TO BOOKSHELF COMMAND


@app.route('/update_page/<int:book_id>', methods=['POST'])
def update_page(book_id):
    new_page = int(request.form['current_page'])

    with sqlite3.connect(r"A:\Library\Python\FTP\FTP\books.db") as conn:
        c = conn.cursor()

        # احصل على الصفحة الحالية القديمة من قاعدة البيانات
        c.execute("SELECT title, current_page FROM books WHERE id=?", (book_id,))
        result = c.fetchone()

        if result:
            title, old_page = result

            # التحديث
            c.execute("""
                UPDATE books 
                SET current_page=?, last_read=?, updated_at=? 
                WHERE id=?
            """, (
                new_page,
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                book_id
            ))
            conn.commit()

            # سجل التغيير
            log_action(f"📖 تحديث صفحات كتاب: {title} من {old_page} إلى {new_page}")
#    googlebackup("r"A:\Library\Python\FTP\FTP\books.db"")
    return redirect(url_for('books'))
    # UPDATE BOOK PAGES COMMAND


@app.route('/uploads/bookimages/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['images_folder'], filename)
    # LOAD BOOK IMAGES ON BOOKSHELF PAGE COMMAND


def get_weeks_with_dates(start_date):
    weeks = []
    for week in weeks_data:
        week_list = []
        for day_name, duration, resistance in week:
            day_info = {
                "day_name": day_name,
                "duration": duration,
                "resistance": resistance,
                "date": start_date.strftime("%Y-%m-%d")
            }
            week_list.append(day_info)
            start_date += timedelta(days=1)
        weeks.append(week_list)
    return weeks
    # LOAD WEEKS & DATES TO PAGE COMMAND
def get_all_entries():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, distance, time, odo, calories FROM entries")
    rows = c.fetchall()
    conn.close()
    entries = {}
    for d, dist, t, odo, cal in rows:
        entries[d] = {
            "distance": dist,
            "time": t,
            "odo": odo,
            "calories": cal
        }
    return entries
    # LOAD DAY CAOUNT TO PAGE COMMAND

def get_entry(date_):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT distance, time, odo, calories FROM entries WHERE date=?", (date_,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"distance": row[0], "time": row[1], "odo": row[2], "calories": row[3]}
    else:
        return {"distance": "", "time": "", "odo": "", "calories": ""}
    # GET WEEKS & DATES TO PAGE COMMAND

def save_entry(date_, distance, time_, odo, calories):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO entries (date, distance, time, odo, calories)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
          distance=excluded.distance,
          time=excluded.time,
          odo=excluded.odo,
          calories=excluded.calories
    ''', (date_, distance, time_, odo, calories))
    conn.commit()
    conn.close()
    # SAVE WEEKS & DATES TO PAGE COMMAND

def log_action_update(date_, old_data, new_data):
    with open(LOG_FILE_RYADH, 'a', encoding='utf-8') as f:
        current_datetime = datetime.now()
        f.write(f"تحديث بيانات\n{date_}\n")
        f.write(f"\n{current_datetime}")
        f.write("من\n")
        f.write(f"المسافة: {old_data.get('distance', '')}\n")
        f.write(f"الوقت: {old_data.get('time', '')}\n")
        f.write(f"العداد: {old_data.get('odo', '')}\n")
        f.write(f"السعرات: {old_data.get('calories', '')}\n")
        f.write("إلى\n")
        f.write(f"المسافة: {new_data.get('distance', '')}\n")
        f.write(f"الوقت: {new_data.get('time', '')}\n")
        f.write(f"العداد: {new_data.get('odo', '')}\n")
        f.write(f"السعرات: {new_data.get('calories', '')}\n")
        f.write("-" * 20 + "\n")
def evaluate_performance(distance_km, time_min, calories):
    if time_min == 0:
        return "لا يوجد وقت مسجل"

    speed = (distance_km / time_min) * 60  # كم/ساعة

    if speed < 10:
        level = "خفيف"
    elif 10 <= speed < 18:
        level = "متوسط"
    else:
        level = "عالي"

    if calories < 100:
        cal_level = "سعرات منخفضة"
    elif 100 <= calories < 200:
        cal_level = "سعرات متوسطة"
    else:
        cal_level = "سعرات عالية"

    return f"أداء التمرين: {level}، {cal_level}."
    # GET SPEED, CAL RATE TO PAGE COMMAND
@app.route("/ryadh")
def ryadh():
    start = date(2025,7,21)
    weeks = get_weeks_with_dates(start)
    all_entries = get_all_entries()
    weekly_summaries = []
    weekly_calories = []
    weekly_distances = []

    for week in weeks:
        total_time = 0
        total_cal = 0
        total_dist = 0
        for day in week:
            entry = all_entries.get(day["date"])
            if entry:
                total_time += float(entry.get("time") or 0)
                total_cal += float(entry.get("calories") or 0)
                total_dist += float(entry.get("distance") or 0)

                # هنا تضيف التقييم لكل يوم
                day["evaluation"] = evaluate_performance(
                    float(entry.get("distance") or 0),
                    float(entry.get("time") or 0),
                    float(entry.get("calories") or 0)
                )
            else:
                day["evaluation"] = "لم يتم تسجيل بيانات"
        weekly_summaries.append(round(total_time, 2))
        weekly_calories.append(round(total_cal, 2))
        weekly_distances.append(round(total_dist, 2))

    return render_template(
        "ryadh.html",
        weeks=weeks,
        entries=all_entries,
        weekly_summaries=weekly_summaries,
        weekly_calories=weekly_calories,
        weekly_distances=weekly_distances,
        enumerate=enumerate,
    )
 # LOAD PAGE COMMAND

@app.route("/editryadh", methods=["GET", "POST"])
def editryadh():
    day_date = request.args.get("date")
    if not day_date:
        return "يجب تحديد التاريخ!", 400

    if request.method == "POST":
        def to_number(value):
            try:
                return float(value) if '.' in value else int(value)
            except:
                return 0

        old_data = get_entry(day_date)

        dist = to_number(request.form.get("distance", "0"))
        time_ = to_number(request.form.get("time", "0"))
        odo = to_number(request.form.get("odo", "0"))
        calories = to_number(request.form.get("calories", "0"))

        new_data = {
            "distance": dist,
            "time": time_,
            "odo": odo,
            "calories": calories
        }

        save_entry(day_date, dist, time_, odo, calories)
        log_action_update(day_date, old_data, new_data)

        return redirect(url_for("ryadh"))

    day_data = get_entry(day_date)
    return render_template("editryadh.html", date=day_date, data=day_data)
    # LOAD PAGE COMMAND
@app.route("/d3", methods=["GET", "POST"])
def d3():
    if request.method == "POST":
        url = request.form.get("url")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        print("URL:", url)
        print("Start Time:", start_time)
        print("End Time:", end_time)
        return render_template("d3.html", url=url, start_time=start_time, end_time=end_time, submitted=True)
    return render_template("d3.html", submitted=False)


start_server()
import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # غيّرها عندك

socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")
import logging
from datetime import date, timedelta
import socket
from flask import jsonify, send_file,abort
import shutil
import os
import sqlite3
from flask import render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

## Giting local IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
finally:
    s.close()

##############
UPLOAD_FOLDER = r"uploads"
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['images_folder'] = 'bookimages'
app.config['backup_folder'] = 'backup'
LOG_FILE = r"log/book.txt"
Books_NAME = r"books.db"

##### Create the folders/files:
def create_folders(folder_list):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for folder in folder_list:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)


def books_db(db_path: str = "books.db", overwrite: bool = False):
    """
    Create a new SQLite database with a table named 'books'
    matching the exact schema you showed in your screenshot.
    """

    db_file = "books.db"
    # Connect (this creates the file automatically if it doesn’t exist)
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # Drop the old table if overwrite is True
    if overwrite:
        cur.execute("DROP TABLE IF EXISTS books")

    # Create the 'books' table
    cur.execute("""
    CREATE TABLE books (
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
    );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database created successfully at: {db_file}")



#######################SERVER SETTINGS#######################



logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


#######################SERVER DEF'S#######################




@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    # IDK



def backup_db():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    src = Books_NAME
    dst = os.path.join(app.config['backup'], f'books_backup_{timestamp}.db')
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
    with sqlite3.connect(Books_NAME) as conn:
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
@app.route('/')
@app.route('/home')
@app.route('/main')
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

    with sqlite3.connect(Books_NAME) as conn:
        cnw = conn.cursor()
        cnw.execute(query, params)
        books = cnw.fetchall()

    return render_template('books.html', books=books, search=search, sort=sort)
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

        with sqlite3.connect(Books_NAME) as conn:
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
    with sqlite3.connect(Books_NAME) as conn:
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
    with sqlite3.connect(Books_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT title FROM books WHERE id=?", (book_id,))
        title = c.fetchone()[0]
        c.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
    log_action(f"🗑️ تم حذف الكتاب: {title}")
    # googlebackup("Books_NAME")
    return redirect(url_for('books'))
    # REMOVE-DELETE BOOK TO BOOKSHELF COMMAND


@app.route('/update_page/<int:book_id>', methods=['POST'])
def update_page(book_id):
    new_page = int(request.form['current_page'])

    with sqlite3.connect(Books_NAME) as conn:
        c = conn.cursor()

        # Giting last page read
        c.execute("SELECT title, current_page FROM books WHERE id=?", (book_id,))
        result = c.fetchone()

        if result:
            title, old_page = result

            # Update
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

            # Log
            log_action(f"📖 تحديث صفحات كتاب: {title} من {old_page} إلى {new_page}")
#    googlebackup("Books_NAME")
    return redirect(url_for('books'))
    # UPDATE BOOK PAGES COMMAND


@app.route('/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['images_folder'], filename)
    # LOAD BOOK IMAGES ON BOOKSHELF PAGE COMMAND


def start_server():
    init_db()
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=backup_db, trigger='interval', weeks=1)
    # scheduler.start()
    print("starting server...")
    create_folders(["uploads", "text", "backup", "log", "streamdvideo", "downloader","bookimages"])
    print(f"Your IP is: {local_ip}")
    socketio.run(app, host=local_ip, port=5000,debug=True)

if __name__ == "__main__":
    start_server()
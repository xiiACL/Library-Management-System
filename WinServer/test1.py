# --------------------- eventlet first! ---------------------
import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from flask_socketio import SocketIO
import yt_dlp
from threading import Timer

# --------------------- إعداد مجلد التحميل ---------------------
download_folder = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_folder, exist_ok=True)

# --------------------- Flask + SocketIO ---------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecretkey"
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

# --------------------- دوال مساعدة ---------------------
def delayed_remove(filename, delay=300):
    """يحذف الملف بعد delay ثانية"""
    filepath = os.path.join(download_folder, filename)
    Timer(delay, lambda: os.remove(filepath) if os.path.exists(filepath) else None).start()

def audio(url, emit=None):
    """تحميل الصوت من يوتيوب"""
    def progress_hook(d):
        if emit and d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '').strip()
            if percent:
                emit("progress", f"progress: {percent}")
            if speed:
                emit("progress", f"speed: {speed}")

        elif emit and d['status'] == 'finished':
            emit("progress", "✅ Download complete.")

    try:
        if emit:
            emit("progress", f"🔽 Downloading {url}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(result).replace(f".{result['ext']}", ".mp3")
            title = result.get('title', 'Unknown Title')

            if os.path.exists(file_path) and emit:
                download_url = f"/download/{os.path.basename(file_path)}"
                emit("download_ready", {"url": download_url, "title": title})
                delayed_remove(os.path.basename(file_path), delay=300)  # يحذف بعد 5 دقائق

            return file_path, title

    except Exception as e:
        if emit:
            emit("progress", f"❌ Error: {e}")
        raise RuntimeError(f"[Download Error] {e}")

# --------------------- Flask routes ---------------------
@app.route('/d', methods=['GET', 'POST'])
def downloader():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            # استخدم SocketIO background task بدل threading
            socketio.start_background_task(audio, url, emit=socketio.emit)
        return redirect(url_for("downloader"))
    return render_template("dow1.html", url='')

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(download_folder, filename, as_attachment=True)

# --------------------- Run server ---------------------
if __name__ == "__main__":
    # نظف المجلد عند بدء التشغيل
    for f in os.listdir(download_folder):
        try:
            os.remove(os.path.join(download_folder, f))
        except:
            pass

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
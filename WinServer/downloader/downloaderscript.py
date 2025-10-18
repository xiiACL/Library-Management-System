import yt_dlp
import os
#from FTP.telegram.telegramsendcode import send
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser

#download_folder = r"/media/imohammedyasser/First/Library/Videos/YT important"
download_folder = r"A:\Library/Python/FTP/FTP/downloads"
ffmpeg_folder = r"A:\Library\ffmpeg"
video_title = ""
# ====== Your credentials ======
api_id = 26078615          # Example: 12345678 (no quotes, just a number)
api_hash = '782f973801088567dfd9230bdb6a1abb'
phone = "+966545884135"
password = "M7O0D9IH"
# ===============================


# def progress(current, total):
#     print(f'Uploading: {current * 100 // total}%')
#
# # Sender
# async def send(video_title):
#     # Create the client
#     client = TelegramClient('session', api_id, api_hash)
#     # Connect to the Telegram session
#     await client.connect()
#     print("Connected")
#     filename = video_title
#     print(f"Sending file: {filename}")
#     await client.send_file('m3oha1mmed3', filename, progress_callback=progress)
#     print(f"✅ {filename} sent successfully!")
#     # Disconnect the client
#     await client.disconnect()
#
# # Downloader
# def audio(url):
#     try:
#         print(f"received: {url}")
#         ydl_opts = {
#             'format': 'bestaudio/best',
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '192',
#             }],
#             'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
#             'quiet': True,
#         }
#
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             result = ydl.extract_info(url, download=True)
#             file_path = ydl.prepare_filename(result).replace(result['ext'], 'mp3')
#             title = result.get('title', 'Unknown Title')
#             if os.path.exists(file_path):
#                 asyncio.run(send(file_path))
#                 return file_path, title
#
#             else:
#                 raise Exception("File not found after download")
#
#     except Exception as e:
#
#         raise RuntimeError(f"[Download Error] {e}")
channel_username = "m3oha1mmed3"          # Without @
def progress(current, total, emit=None):
    percent = int(current * 100 / total)
    print(f'Uploading: {percent}%')
    if emit:
        emit("progress",f"Telegram:{percent}%")

from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeAudio
from mutagen.mp3 import MP3

# client = TelegramClient('session', api_id, api_hash)
# asyncio.run(client.start())



# async def send(video_path, emit=None):
#     try:
#         print(f"Connected, sending file: {video_path}")
#         if emit:
#             emit("status", {"msg": "📤 Uploading to Telegram..."})
#
#         # Get duration from audio metadata
#         audio = MP3(video_path)
#         duration = int(audio.info.length)
#
#         await client.send_file(
#             entity=channel_username,
#             file=video_path,
#             attributes=[
#                 DocumentAttributeAudio(
#                     duration=duration,
#                     voice=False,
#                     title=video_title,     # Optional: customize title
#                     performer=""  # Optional: customize artist
#                 )
#             ],
#             voice=False,  # Make sure it's sent as music
#             progress_callback=lambda c, t: progress(c, t, emit)
#         )
#
#         print("✅ Upload done")
#         if emit:
#             emit("status", {"msg": "✅ Upload complete!"})
#     except Exception as e:
#         print(f"❌ Upload error: {e}")
#         if emit:
#             emit("status", {"msg": f"❌ Telegram Error: {e}"})
#     finally:
#         await client.disconnect()

# # Downloader
# def audio(url, emit=None):
#     global video_title
#     def progress_hook(d):
#         if emit and d['status'] == 'downloading':
#             print(f'Start Downloading: {video_title}')
#             percent = d.get('_percent_str', '').strip()
#             speed = d.get('_speed_str', '').strip()
#
#             if percent:
#                 emit("progress", f"progress: {percent}")
#             # if speed:
#             #     emit("progress", f"download speed: {speed}")
#
#         elif emit and d['status'] == 'finished':
#             emit("progress", "✅ Download complete.")
#
#     try:
#         if emit:
#             emit("progress", f"🔽 Downloading {video_title}")
#
#         ydl_opts = {
#             'format': 'bestaudio/best',
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '192',
#             }],
#             'progress_hooks': [progress_hook],
#             'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
#             'quiet': True,
#         }
#
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             result = ydl.extract_info(url, download=True)
#             file_path = ydl.prepare_filename(result).replace(f".{result['ext']}", ".mp3")
#             title = result.get('title', 'Unknown Title')
#             video_title = title
#             if os.path.exists(file_path):
#                 if emit:
#                     emit("progress", "📤 Uploading to Telegram...")
#                 emit("progress", "✅ Upload complete. Cleaning up...")
#
#                 try:
#                     os.remove(file_path)
#                     emit("progress", "🧹 File deleted from server.")
#                 except Exception as del_err:
#                     emit("progress", f"⚠️ Could not delete file: {del_err}")
#
#                 return file_path, title
#
#             else:
#                 raise FileNotFoundError("File not found after download")
#
#     except Exception as e:
#         if emit:
#             emit("progress", f"❌ Error: {e}")
#         raise RuntimeError(f"[Download Error] {e}")


# Create the Telegram client


# Run the asyncio event loop

def audio(url, emit=None):
    global video_title

    def progress_hook(d):
        if emit and d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '').strip()

            if percent:
                emit("progress", f"progress: {percent}")
            if speed:
                emit("progress", f"download speed: {speed}")

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
            video_title = title

            if os.path.exists(file_path):
                # جهّز رابط التحميل
                download_url = f"/download/{os.path.basename(file_path)}"

                if emit:
                    emit("progress", "📤 File ready for download.")
                    emit("download_ready", {"url": download_url, "title": title})

                return file_path, title
            else:
                raise FileNotFoundError("File not found after download")

    except Exception as e:
        if emit:
            emit("progress", f"❌ Error: {e}")
        raise RuntimeError(f"[Download Error] {e}")





def printerurl(url):
    print(f"received: {url}")
    audio(url)

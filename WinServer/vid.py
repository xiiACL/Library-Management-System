import os
from flask import Flask, Response, request, abort, render_template

app = Flask(__name__)

VIDEO_PATH = r"A:\Library\Python\MainTools\MainTool\streamd video\dehe31.mp4"


@app.route("/")
def index():
    return render_template("video.html")   # يفتح صفحة HTML


@app.route("/video")
def video():
    try:
        file_size = os.path.getsize(VIDEO_PATH)
        range_header = request.headers.get("Range", None)

        if range_header:
            byte1, byte2 = 0, None
            match = range_header.strip().split("=")[1]
            if "-" in match:
                parts = match.split("-")
                if parts[0]:
                    byte1 = int(parts[0])
                if parts[1]:
                    byte2 = int(parts[1])
            byte2 = byte2 if byte2 is not None else file_size - 1
            length = byte2 - byte1 + 1

            with open(VIDEO_PATH, "rb") as f:
                f.seek(byte1)
                data = f.read(length)

            resp = Response(data, status=206, mimetype="video/mp4")
            resp.headers.add("Content-Range", f"bytes {byte1}-{byte2}/{file_size}")
            resp.headers.add("Accept-Ranges", "bytes")
            resp.headers.add("Content-Length", str(length))
            return resp

        return Response(open(VIDEO_PATH, "rb").read(), mimetype="video/mp4")

    except Exception as e:
        abort(500, description=f"Error streaming video: {str(e)}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)

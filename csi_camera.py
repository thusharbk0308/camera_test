from flask import Flask, Response
from picamera2 import Picamera2
import cv2

app = Flask(__name__)

WIDTH = 1280
HEIGHT = 720

picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (WIDTH, HEIGHT)}
)

picam2.configure(config)
picam2.start()


def generate_frames():
    while True:

        frame = picam2.capture_array()

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        cv2.putText(
            frame,
            "CSI Camera",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame
            + b"\r\n"
        )


@app.route("/")
def home():
    return """
    <html>
    <body style="text-align:center;">
        <h2>CSI Camera</h2>
        <img src="/video_feed" width="900">
    </body>
    </html>
    """


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
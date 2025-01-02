from flask import Flask, Response, render_template_string, request
import cv2
import threading

app = Flask(__name__)

# Global variables
vid = None
camera_running = False
lock = threading.Lock()

# HTML Template for the page
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camera Control</title>
</head>
<body>
    <h1>Camera Control</h1>
    <div>
        <button onclick="startCamera()">Start Camera</button>
        <button onclick="stopCamera()">Stop Camera</button>
    </div>
    <div>
        <img id="camera-feed" src="/video_feed" width="640" height="480" onerror="this.src=''">
    </div>
    <script>
        function startCamera() {
            fetch('/start_camera', { method: 'POST' })
                .then(response => response.text())
                .then(data => {
                    document.getElementById('camera-feed').src = '/video_feed';
                })
                .catch(error => alert('Error: ' + error));
        }

        function stopCamera() {
            fetch('/stop_camera', { method: 'POST' })
                .then(response => response.text())
                .then(data => {
                    document.getElementById('camera-feed').src = '';
                })
                .catch(error => alert('Error: ' + error));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/video_feed')
def video_feed():
    global camera_running
    if not camera_running:
        return Response("Camera is not running", status=513)
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    global vid, lock
    while camera_running:
        with lock:
            if vid is not None and vid.isOpened():
                success, frame = vid.read()
                if success:
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                else:
                    break

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_running, vid
    with lock:
        if not camera_running:
            # Initialize the camera
            vid = cv2.VideoCapture(0)
            if not vid.isOpened():
                return "Error: Could not initialize the camera.", 500
            camera_running = True
    return "Camera started", 200

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera_running, vid
    with lock:
        if camera_running:
            # Release the camera
            vid.release()
            vid = None
            camera_running = False
    return "Camera stopped", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

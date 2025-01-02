import cv2
import mediapipe as mp
from flask import Flask, render_template, Response
import threading

vid = None
camera_running = False
lock = threading.Lock()

# Initialize Flask
app = Flask(__name__)

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
finger_tips = [8, 12, 16, 20]
thumb_tip = 4


# Check if the camera is opened correctly
# if not vid.isOpened():
#     print("Error: Could not access the camera.")
#     exit()

def generate_frames():
    global vid, lock, camera_running
    while camera_running:
        with lock:
            if vid is not None and vid.isOpened():
                success, frame = vid.read()
                if success:
                    # Flip the frame for a mirror effect
                    frame = cv2.flip(frame, 1)

                    # Convert the frame to RGB for Mediapipe processing
                    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = hands.process(img_rgb)

                    # Convert back to BGR for OpenCV rendering
                    frame = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

                    # Gesture recognition logic
                    if results.multi_hand_landmarks:
                        for hand_landmark in results.multi_hand_landmarks:
                            lm_list = []
                            for lm in hand_landmark.landmark:
                                lm_list.append(lm)

                            # Example gesture: F*** OFF
                            if (
                                lm_list[3].x < lm_list[4].x and
                                lm_list[8].y > lm_list[6].y and
                                lm_list[12].y < lm_list[10].y and
                                lm_list[16].y > lm_list[14].y and
                                lm_list[20].y > lm_list[18].y
                            ):
                                cv2.putText(frame, "F*** OFF !!!", (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                            # Draw hand landmarks
                            mp_draw.draw_landmarks(
                                frame, hand_landmark, mp_hands.HAND_CONNECTIONS,
                                mp_draw.DrawingSpec((0, 0, 255), 6, 3),
                                mp_draw.DrawingSpec((0, 255, 0), 4, 2)
                            )

                    # Encode the frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()

                    # Yield the frame
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                else:
                    break

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_running, vid
    print ("starting camera.....")
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
    print("stopping the camera")
    global camera_running, vid
    with lock:
        if camera_running:
            # Release the camera
            vid.release()
            vid = None
            camera_running = False
    return "Camera stopped", 200

@app.route('/')
def index():
    return render_template('index.html')  # This will render the index.html page

@app.route('/run-on-video')
def page1():
    return render_template('run-on-video.html')

@app.route('/control')
def control_page():
    return render_template('control.html')

@app.route('/about')
def page2():
    return render_template('about.html')

@app.route('/run-on-image')
def page3():
    return render_template('run-on-image.html')

@app.route('/settings')
def page4():
    return render_template('settings.html')

@app.route('/sign-to-text')
def page5():
    return render_template('sign-to-text.html')

@app.route('/text-to-sign')
def page6():
    return render_template('text-to-sign.html')

@app.route('/isl-sign-language')
def page7():
    return render_template('isl-sign-language.html')

@app.route('/usa-sign-language')
def page8():
    return render_template('usa-sign-language.html')

@app.route('/thai-sign-language')
def page9():
    return render_template('thai-sign-language.html')

@app.route('/text-isl-sign-language')
def page10():
    return render_template('text-isl-sign-language.html')

@app.route('/text-usa-sign-language')
def page11():
    return render_template('text-usa-sign-language.html')

@app.route('/text-thai-sign-language')
def page12():
    return render_template('text-thai-sign-language.html')
@app.route('/video_feed')
def video_feed():
    global camera_running
    if not camera_running:
        return Response("Camera is not running", status=503)
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

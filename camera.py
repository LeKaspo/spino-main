from flask import Flask, Response, render_template_string
import cv2
import threading
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions, Image, ImageFormat
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_utils, pose
import time

app = Flask(__name__)

# Hand-Landmarker
hand_options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path='hand_landmarker.task'),
    num_hands=4,
    running_mode=vision.RunningMode.VIDEO
)
hand_detector = vision.HandLandmarker.create_from_options(hand_options)

# Pose-Landmarker
pose_options = vision.PoseLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path='pose_landmarker_full.task'),
    running_mode=vision.RunningMode.VIDEO
)
pose_detector = vision.PoseLandmarker.create_from_options(pose_options)

# Face-Landmarker
face_options = vision.FaceLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path='face_landmarker.task'),
    running_mode=vision.RunningMode.VIDEO
)
face_detector = vision.FaceLandmarker.create_from_options(face_options)

# Object Detector (gleiches Muster wie Hand/Pose/Face: relativer Modellname)
'''
object_options = vision.ObjectDetectorOptions(
    base_options=python.BaseOptions(model_asset_path='object_detector.task'),
    running_mode=vision.RunningMode.VIDEO,
    max_results=5
)
object_detector = vision.ObjectDetector.create_from_options(object_options)'''

latest_frame = np.zeros((480, 640, 3), dtype=np.uint8)
lock = threading.Lock()

def draw_hand_landmarks(image, detection_result):
    try:
        for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
            handedness = detection_result.handedness[idx]
            
            # hand_landmarks könnte schon NormalizedLandmarkList sein
            if isinstance(hand_landmarks, landmark_pb2.NormalizedLandmarkList):
                hand_proto = hand_landmarks
            else:
                hand_proto = landmark_pb2.NormalizedLandmarkList()
                hand_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
                    for lm in hand_landmarks
                ])
            
            solutions.drawing_utils.draw_landmarks(
                image,
                hand_proto,
                solutions.hands.HAND_CONNECTIONS,
                solutions.drawing_styles.get_default_hand_landmarks_style(),
                solutions.drawing_styles.get_default_hand_connections_style()
            )
            
            # Handedness-Text
            height, width, _ = image.shape
            x_coords = [lm.x for lm in hand_proto.landmark]
            y_coords = [lm.y for lm in hand_proto.landmark]
            text_x = int(min(x_coords) * width)
            text_y = int(min(y_coords) * height) - 10
            cv2.putText(image, handedness[0].category_name, (text_x, text_y),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
    except Exception as e:
        print("Fehler beim Zeichnen der Hand-Landmarks:", e)


def draw_pose_landmarks(image, pose_result):
    if not pose_result or not pose_result.pose_landmarks:
        return

    # Breite/Höhe für Pixelkoordinaten
    height, width, _ = image.shape

    # Extrahiere die Landmarks (bei heavy task gibt es meist nur eine Gruppe)
    landmarks = pose_result.pose_landmarks[0] if isinstance(pose_result.pose_landmarks, list) else pose_result.pose_landmarks

    # Prüfen, wie viele Landmarks wir haben
    num_landmarks = len(landmarks)

    # Wenn 33 Landmarks → Standard-Zeichen mit Verbindungen
    if num_landmarks == 33:
        landmark_list_proto = landmark_pb2.NormalizedLandmarkList()
        for lm in landmarks:
            landmark_list_proto.landmark.append(
                landmark_pb2.NormalizedLandmark(
                    x=lm.x, y=lm.y, z=lm.z,
                    visibility=getattr(lm, 'visibility', 0.0),
                    presence=getattr(lm, 'presence', 0.0)
                )
            )
        drawing_utils.draw_landmarks(
            image,
            landmark_list_proto,
            pose.POSE_CONNECTIONS,
            landmark_drawing_spec=drawing_utils.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
            connection_drawing_spec=drawing_utils.DrawingSpec(color=(0,0,255), thickness=2)
        )
    else:
        # Bei Heavy-Pose → nur Punkte zeichnen
        for lm in landmarks:
            try:
                x_px = int(lm.x * width)
                y_px = int(lm.y * height)
                cv2.circle(image, (x_px, y_px), 2, (0,255,0), -1)
            except Exception as e:
                print("Warnung: lm hat kein Attribut 'x':", lm)


def draw_face_landmarks(image, detection_result):
    try:
        if not detection_result.face_landmarks:
            return

        for face in detection_result.face_landmarks:
            if isinstance(face, landmark_pb2.NormalizedLandmarkList):
                face_proto = face
            else:
                face_proto = landmark_pb2.NormalizedLandmarkList()
                face_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
                    for lm in face
                ])

            landmark_spec = drawing_utils.DrawingSpec(color=(0,255,0), thickness=1, circle_radius=1)
            connection_spec = drawing_utils.DrawingSpec(color=(0,0,255), thickness=1)

            drawing_utils.draw_landmarks(
                image,
                face_proto,
                solutions.face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=landmark_spec,
                connection_drawing_spec=connection_spec
            )
    except Exception as e:
        print("Fehler beim Zeichnen der Face-Landmarks:", e)


def draw_object_detections(image, detection_result):
    try:
        if not detection_result or not getattr(detection_result, 'detections', None):
            return

        height, width, _ = image.shape
        for det in detection_result.detections:
            # Bounding box
            if det.bounding_box:
                left = int(det.bounding_box.origin_x * width)
                top = int(det.bounding_box.origin_y * height)
                w = int(det.bounding_box.width * width)
                h = int(det.bounding_box.height * height)
                cv2.rectangle(image, (left, top), (left + w, top + h), (255, 0, 0), 2)

            # Label / Score
            labels = []
            if det.classification:
                for cls in det.classification:
                    labels.append(f"{cls.category_name}:{cls.score:.2f}")

            if labels:
                text = ", ".join(labels[:2])
                cv2.putText(image, text, (left, max(10, top - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    except Exception as e:
        print("Fehler beim Zeichnen der Object-Detections:", e)


def capture_loop():
    global latest_frame
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera konnte nicht geöffnet werden!")
        return

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                print("Kein Frame")
                continue

            # Flip horizontal (Spiegelbild)
            #frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = np.ascontiguousarray(rgb, dtype=np.uint8)

            mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
            timestamp_ms = int(time.time() * 1000)

            try:
                hand_result = hand_detector.detect_for_video(mp_image, timestamp_ms)
            except Exception as e:
                print("HandLandmarker Fehler:", e)
                hand_result = None

            try:
                pose_result = pose_detector.detect_for_video(mp_image, timestamp_ms)
            except Exception as e:
                print("PoseLandmarker Fehler:", e)
                pose_result = None

            try:
                face_result = face_detector.detect_for_video(mp_image, timestamp_ms)
            except Exception as e:
                print("FaceLandmarker Fehler:", e)
                face_result = None

            '''
            try:
                obj_result = object_detector.detect_for_video(mp_image, timestamp_ms)
            except Exception as e:
                print("ObjectDetector Fehler:", e)
                obj_result = None'''

            annotated = rgb.copy()
            if hand_result:
                draw_hand_landmarks(annotated, hand_result)
            if pose_result:
                draw_pose_landmarks(annotated, pose_result)
            if face_result:
                draw_face_landmarks(annotated, face_result)
            #if obj_result:
            #    draw_object_detections(annotated, obj_result)

            output = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)

            with lock:
                latest_frame = output
        except Exception as e:
            print("Fehler im Capture-Thread:", e)
            time.sleep(1)

def gen_frames():
    global latest_frame
    while True:
        with lock:
            frame = latest_frame.copy()
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template_string("""
    <html>
      <head><title>MediaPipe Multi-Detection</title></head>
      <body style="text-align:center;">
        <h1>Hand, Pose & Face Landmark Stream</h1>
        <img src="{{ url_for('video_feed') }}" width="1280" height="720">
      </body>
    </html>
    """)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=capture_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

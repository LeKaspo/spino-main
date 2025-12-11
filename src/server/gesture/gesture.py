import cv2
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions, Image, ImageFormat
from mediapipe.framework.formats import landmark_pb2
import time
import threading
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.processcommands as processcommands
import server.config.config as config

latest_frame = np.zeros((480, 640, 3), dtype=np.uint8)
lock = threading.Lock()
last_gesture = None
last_detection_time = time.time()
was_stopped = False

hand_options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path="src/server/gesture/hand_landmarker.task"),
    num_hands=1,
    running_mode=vision.RunningMode.VIDEO
)
hand_detector = vision.HandLandmarker.create_from_options(hand_options)

def gen_frames():
    global latest_frame
    while True:
        with lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() +
               b'\r\n')

def capture_loop():
    global last_detection_time
    global latest_frame
    global was_stopped
    cap = None

    while cap is None or not cap.isOpened():
        cap = cv2.VideoCapture("http://192.168.0.145:8090/?action=stream")
        if not cap.isOpened():
            time.sleep(2)
        else:
            print("Successfully connected to stream.")

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                continue

            #frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = np.ascontiguousarray(rgb, dtype=np.uint8)

            mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
            timestamp_ms = int(time.time() * 1000)

            annotated = rgb.copy()
            if config.system_status["gesture_mode_active"] and config.system_status["stop_flag"]:
                was_stopped = False
                try:
                    hand_result = hand_detector.detect_for_video(mp_image, timestamp_ms)
                except Exception as e:
                    print("HandLandmarker Error:", e)
                    hand_result = None

                if hand_result and len(hand_result.hand_landmarks) > 0:
                    last_detection_time = time.time()

                if hand_result:
                    draw_hand_landmarks(annotated, hand_result)
            
            dt = time.time() - last_detection_time
            if dt > 3 and not was_stopped:
                was_stopped = True
                processcommands.gesture_command("fist_normal")
                last_detection_time = time.time()

            output = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)

            with lock:
                latest_frame = output
        except Exception as e:
            print("Error in Capture-Thread:", e)
            time.sleep(1)

def draw_hand_landmarks(image, detection_result):
    global last_gesture
    try:
        for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
            handedness = detection_result.handedness[idx]
            
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

            # Label: Left / Right
            hand_label = handedness[0].category_name

            gesture = classify_gesture(hand_proto.landmark, hand_label)
            if gesture != last_gesture:
                last_gesture = gesture
                processcommands.gesture_command("fist_normal")
                processcommands.gesture_command(gesture)

            cv2.putText(image, f"{hand_label} - {gesture}", (text_x, text_y),
                        cv2.FONT_HERSHEY_DUPLEX, 1,
                        (0, 255, 0), 1, cv2.LINE_AA)
            
    except Exception as e:
        print("Error in draw_hand_landmarks:", e)


def detect_fist(lm):
    closed = 0
    finger_pairs = [(8,6),(12,10),(16,14),(20,18)]
    for tip, pip in finger_pairs:
        if lm[tip].y > lm[pip].y:
            closed += 1
    return closed >= 3


def detect_palm_or_back(lm, handedness_label):
    thumb_tip = lm[4].x
    thumb_base = lm[17].x

    if handedness_label == "Left":
        return "palm" if thumb_tip < thumb_base else "back"
    else:
        return "palm" if thumb_tip > thumb_base else "back"


def detect_rotation(lm):
    mid_x = (lm[9].x + lm[13].x) / 2.0
    dx = mid_x - lm[0].x
    hand_width = max(lm[i].x for i in [0,5,9,13,17]) - min(lm[i].x for i in [0,5,9,13,17])
    threshold = hand_width * 0.65

    if abs(dx) < threshold:
        return "normal"
    elif dx > 0:
        return "rotated_left"
    else:
        return "rotated_right"

def classify_gesture(lm, handedness_label):
    if detect_fist(lm):
        rot = detect_rotation(lm)
        return f"fist_{rot}"
    side = detect_palm_or_back(lm, handedness_label)
    rot = detect_rotation(lm)
    return f"{side}_{rot}"

def start():
    capture_thread = threading.Thread(target=capture_loop, daemon=True)
    capture_thread.start()
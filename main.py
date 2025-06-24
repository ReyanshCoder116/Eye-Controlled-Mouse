
import cv2
import mediapipe as mp
import pyautogui
import time

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

# Blink tracking
left_eye_closed = False
right_eye_closed = False
left_eye_timer = 0
right_eye_timer = 0
cooldown_left = cooldown_right = False
cooldown_duration = 1.0  # cooldown after a click
cursor_history = []

def is_eye_closed(top, bottom, threshold=0.017):
    return (top.y - bottom.y) < threshold

def smooth_cursor(x, y, max_len=5):
    cursor_history.append((x, y))
    if len(cursor_history) > max_len:
        cursor_history.pop(0)
    avg_x = sum(pos[0] for pos in cursor_history) / len(cursor_history)
    avg_y = sum(pos[1] for pos in cursor_history) / len(cursor_history)
    return avg_x, avg_y

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb)
    h, w, _ = frame.shape

    if output.multi_face_landmarks:
        lm = output.multi_face_landmarks[0].landmark
        eye = lm[474]
        x = int(eye.x * w)
        y = int(eye.y * h)

        screen_x = screen_w * (eye.x - 0.3) * 2.5
        screen_y = screen_h * (eye.y - 0.3) * 2.5

        sm_x, sm_y = smooth_cursor(screen_x, screen_y)
        if abs(sm_x - pyautogui.position()[0]) > 5 or abs(sm_y - pyautogui.position()[1]) > 5:
            pyautogui.moveTo(sm_x, sm_y, duration=0.05)

        now = time.time()

        # === LEFT EYE ===
        lt, lb = lm[145], lm[159]
        if is_eye_closed(lt, lb):
            if not left_eye_closed:
                left_eye_timer = now
                left_eye_closed = True
        else:
            if left_eye_closed and now - left_eye_timer > 0.5 and not cooldown_left:
                pyautogui.click()
                print("🟢 LEFT CLICK")
                cooldown_left = True
                left_eye_timer = now
            left_eye_closed = False

        # === RIGHT EYE ===
        rt, rb = lm[374], lm[386]
        if is_eye_closed(rt, rb):
            if not right_eye_closed:
                right_eye_timer = now
                right_eye_closed = True
        else:
            if right_eye_closed and now - right_eye_timer > 0.5 and not cooldown_right:
                pyautogui.rightClick()
                print("🟡 RIGHT CLICK")
                cooldown_right = True
                right_eye_timer = now
            right_eye_closed = False

    # Cooldown reset
    if cooldown_left and time.time() - left_eye_timer > cooldown_duration:
        cooldown_left = False
    if cooldown_right and time.time() - right_eye_timer > cooldown_duration:
        cooldown_right = False

    cv2.imshow("Eye Mouse Controller ULTIMATE", frame)
    cv2.waitKey(1)

# My Code
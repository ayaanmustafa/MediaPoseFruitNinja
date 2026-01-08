import cv2, random, math, time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from collections import deque
import numpy as np
import winsound

def draw_png(frame, png, x, y):
    h, w = png.shape[:2]
    if x < 0 or y < 0 or x + w > frame.shape[1] or y + h > frame.shape[0]:
        return
    alpha = png[:, :, 3] / 255.0
    for c in range(3):
        frame[y:y+h, x:x+w, c] = (
            alpha * png[:, :, c] +
            (1 - alpha) * frame[y:y+h, x:x+w, c]
        )

trail = deque(maxlen=8)  
overlay = None
alpha = 0.7
smoothed_x, smoothed_y = None, None
SMOOTHING = 0.7
HIT_RADIUS = 25
RESPAWN_DELAY = 0.85  # seconds delay before respawn to avoid teleport feel


# Fruit assets
fruit_imgs = [
    cv2.imread("asset/apple1.png", cv2.IMREAD_UNCHANGED),
    cv2.imread("asset/pineapple.png", cv2.IMREAD_UNCHANGED),
    cv2.imread("asset/banana1.png", cv2.IMREAD_UNCHANGED),
    cv2.imread("asset/cherry.png", cv2.IMREAD_UNCHANGED)
]

def rotate_img(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    return cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)  # preserve alpha
    )

# verify and fix alpha channels
for i, f in enumerate(fruit_imgs):
    if f is None:
        raise FileNotFoundError(f"Could not load fruit image at index {i}")
    if f.shape[2] == 3:
        alpha_ch = 255 * np.ones(f.shape[:2], dtype=f.dtype)
        f = np.dstack((f, alpha_ch))
    fruit_imgs[i] = cv2.resize(f, (60, 60))


# local spawn helper (shadows any imported one)
def spawn_fruit_local():
    x = float(random.randint(30, 610))
    return {
        "img": random.choice(fruit_imgs),
        "x": x,
        "y": float(480 - 5),
        "vx": 4.0 if x < 320 else -4.0,
        "vy": -22.0,
        "alive": True,
        "angle": random.uniform(0, 360),
        "omega": random.uniform(-4, 4),
        "respawn_timer": 0.0,
    }

# -----------------------------
# MediaPipe HandLandmarker (kept as-is)
# -----------------------------
BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

landmarker = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# initial single fruit
fruits = [spawn_fruit_local()]

score = 0

game_over = False
extra_fruit_spawned = False
extra_fruit_spawned2 = False
extra_fruit_spawned3 = False
prev_time = time.time()

while cap.isOpened():
    now = time.time()
    dt = now - prev_time
    prev_time = now

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    result = landmarker.detect_for_video(mp_image, int(now * 1000))

    if result.hand_landmarks:
        h, w, _ = frame.shape
        # use only first hand's fingertip for trail (keeps behavior consistent)
        hand_landmarks = result.hand_landmarks[0]
        lm = hand_landmarks[8]
        raw_x, raw_y = lm.x * w, lm.y * h

        if smoothed_x is None:
            smoothed_x, smoothed_y = raw_x, raw_y
        else:
            smoothed_x = SMOOTHING * smoothed_x + (1 - SMOOTHING) * raw_x
            smoothed_y = SMOOTHING * smoothed_y + (1 - SMOOTHING) * raw_y

        cx, cy = int(smoothed_x), int(smoothed_y)
        trail.append((cx, cy))

        # draw trail
        for i in range(1, len(trail)):
            # cv2.line(frame, trail[i - 1], trail[i], (200, 200, 200), thickness=5)
            cv2.line(frame, trail[i - 1], trail[i], (0, 0, 10*i), thickness=3)
            
        cv2.circle(frame, (cx, cy), 5, (0, 255, 255), -1)


    if not game_over and len(trail) > 0:
        hits = []
        for idx, f in enumerate(fruits):
            if not f.get("alive", True):
                continue
            # check trail points against this fruit
            hit = any((px - f["x"])**2 + (py - f["y"])**2 <= HIT_RADIUS**2 for px, py in trail)
            if hit:
                hits.append(idx)
                winsound.PlaySound("asset\\airswish.wav", winsound.SND_ASYNC)

        # apply hits (one by one) — each fruit handled independently
        for idx in sorted(hits, reverse=True):
            score += 1
            # mark dead and start respawn timer instead of immediate respawn
            fruits[idx]["alive"] = False
            fruits[idx]["respawn_timer"] = RESPAWN_DELAY

            # spawn extra fruit once when reaching threshold
            if score >= 10 and not extra_fruit_spawned:
                fruits.append(spawn_fruit_local())
                extra_fruit_spawned = True
                RESPAWN_DELAY = 0.9 

            if score >= 25 and not extra_fruit_spawned2:
                fruits.append(spawn_fruit_local())
                extra_fruit_spawned2 = True
                RESPAWN_DELAY = 0.85 

            if score >= 40 and not extra_fruit_spawned3:
                fruits.append(spawn_fruit_local())
                extra_fruit_spawned3 = True
                RESPAWN_DELAY = 0.65 

    if not game_over:
        for f in fruits:
            if not f.get("alive", True):
                f["respawn_timer"] -= dt
                if f["respawn_timer"] <= 0:
                    # respawn in place with new properties
                    new_f = spawn_fruit_local()
                    f.update(new_f)
                continue

            # physics
            f["y"] += f["vy"]
            f["vy"] += 0.9
            f["x"] += f["vx"]
            f["angle"] += f["omega"]

            # simple horizontal bounds: wrap or reverse to keep fruit on screen
            if f["x"] < 20 or f["x"] > 630:
                f["vx"] *= -1

            # game over when any alive fruit reaches bottom
            if f["y"] > 480:
                game_over = True
                winsound.PlaySound("asset\gameover.wav", winsound.SND_ASYNC)

    for f in fruits:
        if f.get("alive", True):
            rot = rotate_img(f["img"], f["angle"])
            draw_png(frame, rot, int(f["x"] - 30), int(f["y"] - 30))
            # draw_png(frame, f["img"], int(f["x"] - 30), int(f["y"] - 30))

    # HUD
    cv2.putText(frame, f"Score: {score}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

    if game_over:
        overlay = frame.copy()
        overlay[:] = (0, 0, 255)   # red in BGR
        frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)
        cv2.putText(frame, "GAME OVER", (180, 220), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
        cv2.putText(frame, "Press R to Restart", (190, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow("Fruit ninja", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break        

    if game_over and key == ord('r'):
        score = 0
        game_over = False
        trail.clear()
        fruits = [spawn_fruit_local()]
        extra_fruit_spawned = False
        

cap.release()
cv2.destroyAllWindows()
landmarker.close()

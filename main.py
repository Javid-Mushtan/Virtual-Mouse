import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math

CAMERA_INDEX        = 0        # Webcam index (0 = default)
FRAME_W, FRAME_H    = 640, 480 # Capture resolution
SMOOTHING           = 10      # Cursor smoothing (higher = smoother, more lag)
CLICK_THRESHOLD     = 40       # Pixel distance to trigger a click
SCROLL_SPEED        = 30       # Scroll amount per gesture
MOVE_SENSITIVITY    = 1.3      # Cursor speed multiplier
GESTURE_COOLDOWN    = 0.35     # Seconds between repeated actions

mp_hands    = mp.solutions.hands
mp_draw     = mp.solutions.drawing_utils
mp_styles   = mp.solutions.drawing_styles

WRIST = 0
INDEX_TIP = 8
INDEX_MCP = 5
MIDDLE_TIP = 12
MIDDLE_MCP = 9
RING_TIP = 16
PINKY_TIP = 20
THUMB_TIP = 4
THUMB_IP = 3

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def landmark_to_px(landmark, w, h):
    return int(landmark.x * w), int(landmark.y * h)


def is_finger_up(tip, mcp):
    return tip[1] < mcp[1]

def draw_hud(frame, gesture, fps, clicking, scrolling):
    h, w = frame.shape[:2]

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (260, 120), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    cv2.putText(frame, f"FPS: {fps:.0f}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 220, 120), 2)

    # Gesture
    color = (80, 220, 120) if gesture != "IDLE" else (140, 140, 140)
    cv2.putText(frame, f"Gesture: {gesture}", (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

    click_col  = (0, 255, 100)  if clicking  else (80, 80, 80)
    scroll_col = (0, 200, 255)  if scrolling else (80, 80, 80)
    cv2.circle(frame, (20, 85),  8, click_col,  -1)
    cv2.putText(frame, "Click",  (35, 90),  cv2.FONT_HERSHEY_SIMPLEX, 0.55, click_col,  1)
    cv2.circle(frame, (110, 85), 8, scroll_col, -1)
    cv2.putText(frame, "Scroll", (125, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, scroll_col, 1)

    cv2.putText(frame, "Press Q to quit", (10, 115),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1)

    return frame

class VirtualMouse:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        pyautogui.FAILSAFE =True
        pyautogui.PAUSE = 0

        self.prev_x = [0] * SMOOTHING
        self.prev_y = [0] * SMOOTHING

        self.last_click_time = 0
        self.last_scroll_time = 0
        self.last_screenshot_time = 0
        self.clicking = False
        self.scrolling = False
        self.gesture = "IDLE"

    def smooth_cursor(self,x,y):
        self.prev_x = self.prev_x[1:]+[x]
        self.prev_y = self.prev_y[1:]+[y]
        return int(np.mean(self.prev_x)),int(np.mean(self.prev_y))

    def map_to_screen(self,px,py,frame_w,frame_h):
        margin_x = frame_w * 0.15
        margin_y = frame_h * 0.15

        px = max(margin_x, min(frame_w-margin_x, px))
        py = max(margin_y, min(frame_h-margin_y, py))

        sx = int((px - margin_x) / (frame_w - 2 * margin_x) * self.screen_w * MOVE_SENSITIVITY)
        sy = int((py - margin_y) / (frame_h - 2 * margin_y) * self.screen_h * MOVE_SENSITIVITY)
        sx = max(0, min(self.screen_w - 1, sx))
        sy = max(0, min(self.screen_h - 1, sy))
        return sx, sy

    def process(self,landmarks,frame_w,frame_h):
        lm = landmarks.landmark

        index_tip = landmark_to_px(lm[INDEX_TIP], frame_w,frame_h)
        index_mcp = landmark_to_px(lm[INDEX_MCP],frame_w,frame_h)
        middle_tip = landmark_to_px(lm[MIDDLE_TIP],frame_w,frame_h)
        middle_mcp = landmark_to_px(lm[MIDDLE_MCP], frame_w, frame_h)
        ring_tip = landmark_to_px(lm[RING_TIP], frame_w, frame_h)
        pinky_tip = landmark_to_px(lm[PINKY_TIP], frame_w, frame_h)
        thumb_tip = landmark_to_px(lm[THUMB_TIP], frame_w, frame_h)
        thumb_ip = landmark_to_px(lm[THUMB_IP], frame_w, frame_h)

        index_up = is_finger_up(index_tip,index_mcp)
        middle_up = is_finger_up(middle_tip,middle_mcp)

        sx, sy = self.map_to_screen(index_tip[0],index_tip[1],frame_w,frame_h)
        sx,sy = self.smooth_cursor(sx,sy)
        pyautogui.moveTo(sx,sy)

        now = time.time()
        self.clicking = False
        self.scrolling = False
        self.gesture = "MOVE"

        d_left = distance(index_tip,thumb_tip)
        if d_left < CLICK_THRESHOLD and (now-self.last_click_time) > GESTURE_COOLDOWN:
            pyautogui.click()
            self.last_click_time = now
            self.clicking = True
            self.gesture = "LEFT CLICK"
            #cv2.putText(img, "MOVE",(50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        d_right = distance(middle_tip, thumb_tip)
        if d_right < CLICK_THRESHOLD and (now-self.last_click_time) > GESTURE_COOLDOWN:
            pyautogui.rightClick()
            self.last_click_time = now
            self.clicking = True
            self.gesture = "RIGHT CLICK"

        elif index_up and middle_up:
            d_fingers = distance(index_tip,middle_tip)
            if (now - self.last_scroll_time) > GESTURE_COOLDOWN * 0.5:
                if d_fingers > 60:
                    pyautogui.scroll(SCROLL_SPEED)
                    self.gesture = "SCROLL UP"
                elif d_fingers < 35:
                    pyautogui.scroll(-SCROLL_SPEED)
                    self.gesture = "SCROLL DOWN"
                self.last_scroll_time = now
                self.scrolling = True

        all_down = all([
            not is_finger_up(index_tip,index_mcp),
            not is_finger_up(middle_tip,middle_mcp),
        ])

        if all_down and (now - self.last_screenshot_time) > 2.0:
            pyautogui.screenshot("screenshot.png")
            self.last_screenshot_time = now
            self.gesture = "SCREENSHOT ✓"

        return index_tip

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

    vm = VirtualMouse()
    prev_t = time.time()

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.65,
        model_complexity=0,
    ) as hands:
        while True:
            ret,frame = cap.read()
            if not ret:
                print("ENDING !!!")
                break

            frame = cv2.flip(frame,1)
            h,w = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            cursor_pt = None
            if result.multi_hand_landmarks:
                for hand_lm in result.multi_hand_landmarks:
                    mp_draw.draw_landmarks(
                        frame,hand_lm,
                        mp_hands.HAND_CONNECTIONS,
                        mp_styles.get_default_hand_landmarks_style(),
                        mp_styles.get_default_hand_connections_style(),
                    )
                    cursor_pt = vm.process(hand_lm,w,h)

            if cursor_pt:
                cv2.circle(frame, cursor_pt, 12, (0, 255, 150), 2)
                cv2.circle(frame, cursor_pt, 4, (0, 255, 150), -1)

            now = time.time()
            fps = 1 / (now - prev_t + 1e-9)
            prev_t = now

            frame = draw_hud(frame, vm.gesture, fps, vm.clicking, vm.scrolling)

            cv2.imshow("Virtual Mouse  |  Hand Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        print("Mouse stopped.")

if __name__ == "__main__":
    main()
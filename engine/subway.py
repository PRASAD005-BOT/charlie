import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import threading

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Screen resolution and zone settings
screen_width, screen_height = 640, 640

# Zone Colors
colors = {
    "JUMP": (0, 255, 0),       # Green
    "DUCK": (255, 0, 0),       # Red
    "LEFT": (0, 0, 255),       # Blue
    "RIGHT": (255, 255, 0),    # Yellow
}

# Light versions of the colors for zone fill
light_colors = {
    "JUMP": (150, 255, 150),   # Light Green
    "DUCK": (255, 150, 150),   # Light Red
    "LEFT": (150, 150, 255),   # Light Blue
    "RIGHT": (255, 255, 150),  # Light Yellow
}

# Function to perform game control actions
def perform_action(action, last_action_time, cooldown=0.3):
    if time.time() - last_action_time[action] > cooldown:
        if action == "JUMP":
            pyautogui.press('w')  # Assuming 'w' key is used for jumping
        elif action == "DUCK":
            pyautogui.press('s')  # Assuming 's' key is used for ducking
        elif action == "LEFT":
            pyautogui.press('a')  # Assuming 'a' key is used for moving left
        elif action == "RIGHT":
            pyautogui.press('d')  # Assuming 'd' key is used for moving right
        last_action_time[action] = time.time()

# Initialize cooldown timer
last_action_time = {"JUMP": 0, "DUCK": 0, "LEFT": 0, "RIGHT": 0}

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)  # Set frame rate to 30 FPS

# Initialize previous finger positions
prev_index_x, prev_index_y = None, None
prev_middle_x, prev_middle_y = None, None

# Function to calculate Euclidean distance between two points
def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to process hand landmarks with refined gesture detection
# Function to process hand landmarks with refined gesture detection
def process_hand_landmarks(rgb_frame, frame):
    global prev_index_x, prev_index_y, prev_middle_x, prev_middle_y, hand_moved, hand_zone
    result = hands.process(rgb_frame)
    hand_moved = False  # Track if hand has moved
    hand_zone = None    # Reset hand zone

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger and middle finger positions
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            x_index = int(index_tip.x * screen_width)
            y_index = int(index_tip.y * screen_height)
            x_middle = int(middle_tip.x * screen_width)
            y_middle = int(middle_tip.y * screen_height)

            # Draw finger positions
            cv2.circle(frame, (x_index, y_index), 10, (255, 255, 255), -1)  # Index finger
            cv2.circle(frame, (x_middle, y_middle), 10, (0, 255, 0), -1)     # Middle finger

            if prev_index_x is not None and prev_index_y is not None and prev_middle_x is not None and prev_middle_y is not None:
                # Calculate movement direction of index and middle fingers
                dx_index = x_index - prev_index_x
                dy_index = y_index - prev_index_y
                dx_middle = x_middle - prev_middle_x
                dy_middle = y_middle - prev_middle_y

                # Calculate average movement direction
                dx_avg = (dx_index + dx_middle) / 2
                dy_avg = (dy_index + dy_middle) / 2

                # Define a refined movement threshold
                movement_threshold = 10  # Adjust this value as needed

                # Check if fingers are moving significantly
                if abs(dx_avg) > movement_threshold or abs(dy_avg) > movement_threshold:
                    # Determine movement direction with clearer priorities
                    if abs(dy_avg) > abs(dx_avg):
                        if dy_avg < -movement_threshold:  # Move up
                            hand_zone = "JUMP"
                        elif dy_avg > movement_threshold:  # Move down
                            hand_zone = "DUCK"
                    else:
                        if dx_avg < -movement_threshold:  # Move left
                            hand_zone = "LEFT"
                        elif dx_avg > movement_threshold:  # Move right
                            hand_zone = "RIGHT"

                    # Perform action based on movement direction
                    if hand_zone:
                        perform_action(hand_zone, last_action_time)
                        hand_moved = True

            # Update previous finger positions
            prev_index_x, prev_index_y = x_index, y_index
            prev_middle_x, prev_middle_y = x_middle, y_middle

# Initialize threading variables
hand_moved = False
hand_zone = None

def subway():
    global hand_moved, hand_zone

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip and resize the frame
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (screen_width, screen_height))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process hand landmarks in a separate thread
        hand_thread = threading.Thread(target=process_hand_landmarks, args=(rgb_frame, frame))
        hand_thread.start()
        hand_thread.join()

        # Highlight the active zone and add black text if hand moved
        if hand_moved and hand_zone:
            if hand_zone == "JUMP":
                cv2.polylines(frame, [np.array([(0, 0), (screen_width, 0)])], isClosed=False, color=light_colors["JUMP"], thickness=2)
                cv2.putText(frame, "JUMP", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            elif hand_zone == "DUCK":
                cv2.polylines(frame, [np.array([(0, screen_height), (screen_width, screen_height)])], isClosed=False, color=light_colors["DUCK"], thickness=2)
                cv2.putText(frame, "DUCK", (10, screen_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            elif hand_zone == "LEFT":
                cv2.polylines(frame, [np.array([(0, 0), (0, screen_height)])], isClosed=False, color=light_colors["LEFT"], thickness=2)
                cv2.putText(frame, "LEFT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            elif hand_zone == "RIGHT":
                cv2.polylines(frame, [np.array([(screen_width, 0), (screen_width, screen_height)])], isClosed=False, color=light_colors["RIGHT"], thickness=2)
                cv2.putText(frame, "RIGHT", (screen_width - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Display frame
        cv2.imshow("Gesture-Based Subway Surfers", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

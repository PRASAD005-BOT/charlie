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
    "ACCELERATE": (0, 255, 255),  # Cyan
    "BRAKE": (255, 0, 255),      # Magenta
}

# Light versions of the colors for zone fill
light_colors = {
    "ACCELERATE": (150, 255, 255),  # Light Cyan
    "BRAKE": (255, 150, 255),      # Light Magenta
}

# Function to perform game control actions
def perform_action(action, last_action_time, cooldown=0.3):
    if action not in last_action_time:
        last_action_time[action] = 0  # Initialize the time if action not found
    if time.time() - last_action_time[action] > cooldown:
        if action == "ACCELERATE":
            pyautogui.press('up')  # Accelerate
        elif action == "BRAKE":
            pyautogui.press('down')  # Brake
        last_action_time[action] = time.time()

# Initialize cooldown timer
last_action_time = {"ACCELERATE": 0, "BRAKE": 0}

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)  # Set frame rate to 30 FPS

# Initialize previous finger positions
prev_index_x, prev_index_y = None, None
prev_middle_x, prev_middle_y = None, None
prev_wrist_y = None

# Function to calculate Euclidean distance between two points
def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to process hand landmarks with refined gesture detection
def process_hand_landmarks(rgb_frame):
    global prev_index_x, prev_index_y, prev_middle_x, prev_middle_y, prev_wrist_y, hand_moved, hand_zone
    result = hands.process(rgb_frame)
    hand_moved = False  # Track if hand has moved
    hand_zone = None    # Reset hand zone

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger and middle finger positions
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

            x_index = int(index_tip.x * screen_width)
            y_index = int(index_tip.y * screen_height)
            x_middle = int(middle_tip.x * screen_width)
            y_middle = int(middle_tip.y * screen_height)
            y_wrist = int(wrist.y * screen_height)

            # Draw finger positions
            cv2.circle(frame, (x_index, y_index), 10, (255, 255, 255), -1)  # Index finger
            cv2.circle(frame, (x_middle, y_middle), 10, (0, 255, 0), -1)     # Middle finger
            cv2.circle(frame, (int(wrist.x * screen_width), y_wrist), 10, (255, 0, 0), -1)  # Wrist

            if prev_index_x is not None and prev_index_y is not None and prev_middle_x is not None and prev_middle_y is not None and prev_wrist_y is not None:
                # Calculate movement direction of index and middle fingers
                dy_index = y_index - prev_index_y
                dy_middle = y_middle - prev_middle_y
                dy_wrist = y_wrist - prev_wrist_y

                # Define movement thresholds
                finger_movement_threshold = 10  # Adjust this value as needed
                wrist_movement_threshold = 10  # Adjust this value as needed

                # Check if both fingers are lifted
                if dy_index < -finger_movement_threshold and dy_middle < -finger_movement_threshold:
                    hand_zone = "ACCELERATE"
                # Check if wrist is moving downwards
                elif dy_wrist > wrist_movement_threshold:
                    hand_zone = "BRAKE"
                else:  # No specific action, hand is free
                    hand_zone = "NORMAL"

                # Perform action based on movement direction
                if hand_zone:
                    perform_action(hand_zone, last_action_time)
                    hand_moved = True

            # Update previous finger and wrist positions
            prev_index_x, prev_index_y = x_index, y_index
            prev_middle_x, prev_middle_y = x_middle, y_middle
            prev_wrist_y = y_wrist

# Initialize threading variables
hand_moved = False
hand_zone = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip and resize the frame
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (screen_width, screen_height))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process hand landmarks in a separate thread
    hand_thread = threading.Thread(target=process_hand_landmarks, args=(rgb_frame,))
    hand_thread.start()
    hand_thread.join()

    # Highlight the active zone and add black text if hand moved
    if hand_moved and hand_zone:
        if hand_zone == "ACCELERATE":
            cv2.polylines(frame, [np.array([(0, 0), (screen_width, 0)])], isClosed=False, color=light_colors["ACCELERATE"], thickness=2)
            cv2.putText(frame, "ACCELERATE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        elif hand_zone == "BRAKE":
            cv2.polylines(frame, [np.array([(0, screen_height - 30), (screen_width, screen_height - 30)])], isClosed=False, color=light_colors["BRAKE"], thickness=2)
            cv2.putText(frame, "BRAKE", (10, screen_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        elif hand_zone == "NORMAL":
            cv2.putText(frame, "NORMAL", (10, screen_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  # Green text for normal state

    # Show the frame with highlighted active zone
    cv2.imshow('Hill Climb Racing Control', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

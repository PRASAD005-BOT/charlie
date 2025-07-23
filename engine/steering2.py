
import cv2
import mediapipe as mp
import math
import pyautogui
import time

# Initialize MediaPipe Hands and Face Mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Steering Wheel Parameters
wheel_center = (320, 240)  # Center of the steering wheel
wheel_radius = 150  # Radius of the steering wheel
steering_angle = 0  # Steering angle
hands_on_wheel = False  # Flag for hands holding the wheel
action = "Brake"  # Initial action
last_action = None
last_update_time = time.time()

def draw_steering_wheel(frame, center, radius, angle):
    """Draws the steering wheel with dynamic rotation based on the angle."""
    # Draw the outer circle of the wheel
    cv2.circle(frame, center, radius, (0, 0, 0), 4)

    # Draw the spokes (rotating lines)
    for i in range(0, 3):
        spoke_angle = math.radians(angle + i * 120)  # 3 spokes at 120° intervals
        x1 = int(center[0] + radius * math.cos(spoke_angle))
        y1 = int(center[1] + radius * math.sin(spoke_angle))
        cv2.line(frame, center, (x1, y1), (0, 0, 0), 2)

def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def control_car(action):
    """Control the car based on the detected action."""
    global last_action
    if action != last_action:
        if action == "Turn Left":
            pyautogui.keyDown('a')
            pyautogui.keyUp('d')
        elif action == "Turn Right":
            pyautogui.keyDown('d')
            pyautogui.keyUp('a')
        elif action == "Accelerate":
            pyautogui.keyDown('w')
            pyautogui.keyUp('s')
        elif action == "Brake":
            pyautogui.keyDown('s')
            pyautogui.keyUp('a')
            pyautogui.keyUp('d')
            pyautogui.keyUp('w')
        last_action = action

def mask(frame, image_path, face_x, face_y, scale_factor):
    """Masking function to overlay an image on the frame."""
    # Read the PNG image with transparency (alpha channel)
    mask_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Image with alpha channel
    mask_image = cv2.resize(mask_image, (int(300 * scale_factor), int(300 * scale_factor)), cv2.INTER_AREA)  # Resize based on scale factor

    # Get dimensions
    mask_height, mask_width = mask_image.shape[:2]
    frame_height, frame_width = frame.shape[:2]

    for i in range(mask_height):
        for j in range(mask_width):
            if mask_image[i, j][3] != 0:  # Check if the alpha channel is not transparent
                if 0 <= (face_y - mask_height // 2) + i < frame_height and 0 <= (face_x - mask_width // 2) + j < frame_width:
                    frame[(face_y - mask_height // 2) + i, (face_x - mask_width // 2) + j] = mask_image[i, j][:3]  # Overlay RGB on the frame

def steering_control():
    """Main function to control steering based on hand and face detection."""
    global last_update_time, action, steering_angle, hands_on_wheel

    # Webcam input
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as hands, mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True) as face_mesh:
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Resize and flip frame
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.flip(frame, 1)  # Flip for a mirror view
            h, w, _ = frame.shape  # Frame dimensions

            # Convert to RGB and process with MediaPipe Hands
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hand_results = hands.process(rgb_frame)
            face_results = face_mesh.process(rgb_frame)

            # Initialize hands on wheel flag
            hands_on_wheel = False  
            hand_positions = []

            # Hand detection logic
            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                    wrist_coords = (int(wrist.x * w), int(wrist.y * h))
                    index_coords = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))

                    hand_positions.append(wrist_coords)  # Store wrist position
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Check if hands are close to the wheel center
            hands_on_wheel = any(calculate_distance(pos, wheel_center) < wheel_radius for pos in hand_positions)

            # Determine action based on the number of hands
            if not hands_on_wheel:  # No hands on wheel
                action = "Brake"
            elif len(hand_positions) == 1:  # Single hand detected
                if hand_positions[0][1] < wheel_center[1]:
                    action = "Turn Left"
                else:
                    action = "Turn Right"
            elif len(hand_positions) >= 2:  # Both hands detected
                if hand_positions[0][1] > wheel_center[1] and hand_positions[1][1] > wheel_center[1]:
                    action = "Accelerate"
                else:
                    action = "Turn Left" if hand_positions[0][1] < wheel_center[1] else "Turn Right"

            # Update steering angle dynamically if hands are on the wheel
            if hands_on_wheel and len(hand_positions) >= 2:
                dx = hand_positions[1][0] - hand_positions[0][0]
                dy = hand_positions[1][1] - hand_positions[0][1]
                steering_angle = math.degrees(math.atan2(dy, dx))

            # Control the car based on the action at limited intervals
            if time.time() - last_update_time > 0.1:  # Update every 0.1 seconds
                control_car(action)
                last_update_time = time.time()

            # Draw the steering wheel
            draw_steering_wheel(frame, wheel_center, wheel_radius, steering_angle)

            # Display steering angle and action
            cv2.putText(frame, f"Action: {action}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)  # Black color for text
            cv2.putText(frame, f"Steering Angle: {int(steering_angle)} deg", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            # Overlay the mask based on the detected face
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    # Calculate scale based on eye distance
                    left_eye = face_landmarks.landmark[33]
                    right_eye = face_landmarks.landmark[263]
                    eye_distance = math.sqrt((right_eye.x - left_eye.x) ** 2 + (right_eye.y - left_eye.y) ** 2) * w
                    scale_factor = eye_distance / 100  # Adjust scale factor as needed

                    # Use the nose tip landmark (index 1) for mask positioning
                    nose_x = int(face_landmarks.landmark[1].x * w)
                    nose_y = int(face_landmarks.landmark[1].y * h)

                    # Apply the mask at the nose position
                    mask(frame, r"C:\Users\vadla\Downloads\hack.png", nose_x, nose_y, scale_factor)

            # Add "Tesla" in the top right corner
            cv2.putText(frame, "Tesla", (w - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            # Show output
            cv2.imshow("Steering Wheel Control", frame)

            # Quit with 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

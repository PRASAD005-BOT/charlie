import cv2
import os

def capture_samples(output_dir, num_samples=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(0)  # Open the default camera
    count = 0

    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Capture Face Sample", frame)
        key = cv2.waitKey(1)

        if key % 256 == 32:  # Space key pressed
            img_name = os.path.join(output_dir, f"face_sample_{count + 1}.jpg")
            cv2.imwrite(img_name, frame)
            print(f"Sample {count + 1} saved: {img_name}")
            count += 1

    cap.release()
    cv2.destroyAllWindows()

# Usage
capture_samples('D:\\pytho\\jarvis\\engine\\auth\\samples', num_samples=3)

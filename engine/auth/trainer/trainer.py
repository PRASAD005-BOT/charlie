import face_recognition
import os
import pickle

def train_faces(known_faces_dir, output_file):
    known_face_encodings = []
    known_face_names = []

    # Loop through all images in the known faces directory
    for image_file in os.listdir(known_faces_dir):
        if image_file.endswith(('.jpg', '.png', '.jpeg')):
            image_path = os.path.join(known_faces_dir, image_file)
            image = face_recognition.load_image_file(image_path)

            # Get face encodings
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])  # Take the first face encoding
                known_face_names.append(os.path.splitext(image_file)[0])  # Use filename without extension as name

    # Save the encodings and names to a file
    with open(output_file, 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)

    print(f"Trained on {len(known_face_names)} faces and saved to {output_file}")

# Usage
train_faces('D:\\pytho\\jarvis\\engine\\auth\\known_faces', 'D:\\pytho\\jarvis\\engine\\auth\\known_faces.dat')

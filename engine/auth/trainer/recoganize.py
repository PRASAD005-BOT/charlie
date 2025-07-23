import face_recognition
import pickle

def recognize_faces(unknown_image_path, known_faces_file):
    with open(known_faces_file, 'rb') as f:
        known_face_encodings, known_face_names = pickle.load(f)

    # Load the unknown image
    unknown_image = face_recognition.load_image_file(unknown_image_path)
    unknown_face_encodings = face_recognition.face_encodings(unknown_image)

    # If there are any face encodings found in the unknown image
    if unknown_face_encodings:
        for unknown_face_encoding in unknown_face_encodings:
            results = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)

            # Print results
            for i, match in enumerate(results):
                if match:
                    print(f"Found {known_face_names[i]}!")
                    break  # Stop after the first match
            else:
                print("Unknown face!")

# Usage
recognize_faces('D:\\pytho\\jarvis\\engine\\auth\\unknown_image.jpg', 'D:\\pytho\\jarvis\\engine\\auth\\known_faces.dat')

import cv2
from facedb import FaceDB
import time
import screeninfo  # To get screen resolution

# Create a FaceDB instance and specify where to store the database
db = FaceDB(path="facedata")

def add_face(id, name, img_path):
    """
    Adds a face to the database with a given name and image path.
    
    :param id: Custom ID for the person
    :param name: Name of the person
    :param img_path: Path to the image file
    :return: Face ID of the added face
    """
    face_id = db.add(id, img=img_path)
    db.update(id=face_id, name=name)
    print(f"Facial Recognition - Added ID: {id}, Name: {name}, face_ID: {face_id}")
    return face_id

def recognize_face(img_path):
    """
    Recognizes a face from an image.

    :param img_path: Path to the image file to recognize
    :return: Dictionary containing recognized person's ID and name, or None if not recognized
    """
    result = db.recognize(img=img_path, include=["id", "name"])
    if result:
        recognized_data = {"id": result["id"], "name": result["name"]}
        print(f"Facial Recognition - Recognized: {recognized_data}")
        return recognized_data
    else:
        print("Facial Recognition - Face not recognized.")
        return None

def facialRecognition(save_path="captured_face.jpg"):
    """
    Opens the camera in full-screen mode, waits for 3 seconds, captures a photo, and recognizes the face.
    
    :param save_path: Path where the captured image will be saved.
    :return: Dictionary containing recognized person's ID and name, or None if not recognized
    """
    cap = cv2.VideoCapture(0)  # Open the default camera
    if not cap.isOpened():
        print("Facial Recognition - Error: Could not open camera.")
        return None
    
    print("Facial Recognition - Camera opened. Capturing image in 3 seconds...")

    cv2.namedWindow("Capture Face", cv2.WND_PROP_FULLSCREEN)  # Create a full-screen window
    cv2.setWindowProperty("Capture Face", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    start_time = time.time()
    
    while time.time() - start_time < 3:  # Show camera feed for 3 seconds
        ret, frame = cap.read()
        if not ret:
            print("Facial Recognition - Failed to grab frame.")
            cap.release()
            return None

        cv2.imshow("Capture Face", frame)
        cv2.waitKey(1)  # Refresh display

    # Capture final image
    ret, frame = cap.read()
    if not ret:
        print("Facial Recognition - Failed to grab final frame.")
        cap.release()
        cv2.destroyAllWindows()
        return None

    cv2.imwrite(save_path, frame)  # Save the image
    print(f"Facial Recognition - Photo saved as {save_path}")

    cap.release()
    cv2.destroyAllWindows()

    return recognize_face(save_path)  # Return only name and ID

# Run the capture and recognition process when this script is executed
if __name__ == "__main__":
    result = facialRecognition()
    print("Facial Recognition - Recognition Result:", result)

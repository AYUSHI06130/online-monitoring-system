import cv2
import os


def capture_photo(candidate_id):

    os.makedirs("static/uploads", exist_ok=True)

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Unable to open webcam.")
        return None

    print("Press SPACE to capture.")
    print("Press ESC to cancel.")

    photo_path = f"static/uploads/{candidate_id}.jpg"

    while True:

        ret, frame = camera.read()

        if not ret:
            print("Failed to read frame.")
            break

        cv2.imshow("Candidate Photo", frame)

        key = cv2.waitKey(1) & 0xFF

        # SPACE BAR
        if key == 32:

            if cv2.imwrite(photo_path, frame):
                print("Photo Saved Successfully.")
            else:
                print("Failed to save photo.")

            break

        # ESC
        elif key == 27:

            print("Capture Cancelled.")
            photo_path = None
            break

    camera.release()
    cv2.destroyAllWindows()

    return photo_path
import cv2
import sqlite3
import time
import os

from datetime import datetime
from config import DATABASE


# Candidate ID Temporary - will  come from Flask


candidate_id = "190"

SCREENSHOT_FOLDER = "screenshots"
os.makedirs(SCREENSHOT_FOLDER,exist_ok=True)


# Load Haar Cascade


face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


# Event Logger Function


def log_event(event_type, remarks):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO EventLog
        (
            candidate_id,
            event_type,
            timestamp,
            remarks
        )

        VALUES (?, ?, ?, ?)
    """,
    (
        candidate_id,
        event_type,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        remarks
    ))

    connection.commit()
    connection.close()

def capture_screenshot(frame):

    filename = f"{candidate_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    filepath = os.path.join(
        SCREENSHOT_FOLDER,
        filename
    )

    cv2.imwrite(filepath, frame)

    print(f"Screenshot Saved: {filepath}")

    return filepath    



# Open Webcam

session_start_time = datetime.now()
camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("Unable to access webcam.")

    exit()


print(" Continuous Face Monitoring Started")
print(" Press Q to Exit")



# Stores Previous Status
# Prevents Duplicate Logging

previous_status = None

# Tracks when face disappeared
absence_start_time = None

# Current absence duration
absence_duration = 0

# Total absence duration
total_absence_duration = 0

face_not_detected_count = 0



# Continuous Monitoring


while True:

    success, frame = camera.read()

    if not success:

        print("Unable to capture frame.")

        break

    
    # Convert to Grayscale
    

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    
    # Detect Faces
    

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40, 40)
    )

    
    # Face Detected


    if len(faces) > 0:

        status = "Face Detected"

        color = (0, 255, 0)



        #face has returned
        if absence_start_time is not None:
            total_absence = int(time.time() - absence_start_time)
            total_absence_duration += total_absence
            log_event(
                "Face Returned",
                f"Candidate returned after {total_absence} seconds"
            )
            absence_start_time = None
            absence_duration = 0

        if previous_status != status:

            log_event(
                "Face Detected",
                "Candidate is visible"
            )

            previous_status = status

    
    # Face Not Detected
    

    else:

        status = "Face Not Detected"

        color = (0, 0, 255)

        #face disappeared for first time
        if absence_start_time is None:
            absence_start_time = time.time()

            screenshot_path=capture_screenshot(frame)

            log_event(
                "Screenshot Captured",
                screenshot_path
            )

        #calculate absence duration
        absence_duration = int(time.time() - absence_start_time)

        if previous_status != status:
            #increasing count by one
            face_not_detected_count += 1

            log_event(
                "Face Not Detected",
                "Candidate left webcam"
            )

            previous_status = status

    
    # Draw Bounding Box
    

    for (x, y, w, h) in faces:

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    
    # Display Status
    

    cv2.putText(
        frame,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2
    )
    #displycandidate id 

    cv2.putText(
        frame,
        f"Candidate ID: {candidate_id}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    #display current time
    current_time = datetime.now().strftime("%H:%M:%S")

    cv2.putText(
        frame,
        f"Current Time: {current_time}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )
    #display absence duration 
    cv2.putText(
        frame,
        f"Absence Duration: {absence_duration} sec",
        (20, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    #display total duration of absence
    cv2.putText(
        frame,
        f"Total Absence Duration: {total_absence_duration} sec",
        (20, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    
    # Display Webcam
    

    cv2.imshow(
        "Continuous Face Monitoring",
        frame
    )

    
    # Exit on Q
    

    if cv2.waitKey(1) & 0xFF == ord('q'):

        break


# Close Webcam


camera.release()

cv2.destroyAllWindows()

print("Monitoring Stopped Successfully.")
print("Session Summary:")
print(f"Session started at: {session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total Absence Duration: {total_absence_duration} sec")
print(f"Face Not Detected Count: {face_not_detected_count}")
import cv2
import os
 

# Loading Haar Cascade Face Detector


face_detector = cv2.CascadeClassifier(

    cv2.data.haarcascades +

    "haarcascade_frontalface_default.xml"

)

# Create Photos Folder


os.makedirs("photos", exist_ok=True)


# Open Webcam


camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("Unable to access webcam.")

    exit()

print("Webcam Started.")
print("Press Q to Exit.")


# Start Reading Frames

image_count = 1
while True:

    success, frame = camera.read()

    if not success:

        print("Failed to read frame.")

        break

    # Convert to grayscale
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # Detect faces
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40,40)
    )


    # Face Detection Status
    

    if len(faces) > 0:

        status = "Face Detected"
        color = (0,255,0)      # Green

    else:

        status = "Face Not Detected"
        color = (0,0,255)      # Red


    # Draw Rectangle
    

    for (x,y,w,h) in faces:

        cv2.rectangle(

            frame,

            (x,y),

            (x+w,y+h),

            (0,255,0),

            2

        )

    
    # Display Status Text
    

    cv2.putText(

        frame,

        status,

        (20,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        1,

        color,

        2

    )

    cv2.imshow("Face Detection", frame)

    key = cv2.waitKey(1) & 0xFF


# Capture Image


    if key == ord('c'):


        filename = f"photos/photo_{image_count}.jpg"

        cv2.imwrite(filename, frame)

        print(f"Image Saved Successfully: {filename}")

        image_count += 1


# Quit Program
 

    elif key == ord('q'):

        break


# Close Webcam


camera.release()

cv2.destroyAllWindows()

print("Program Closed.")
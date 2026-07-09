import cv2

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:

    ret, frame = camera.read()

    cv2.imshow("Test Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 32:
        cv2.imwrite("test.jpg", frame)
        print("Saved")
        break

    elif key == 27:
        break

camera.release()
cv2.destroyAllWindows()
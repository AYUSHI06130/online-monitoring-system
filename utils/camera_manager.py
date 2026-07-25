import cv2


class CameraManager:

    def __init__(self):

        self.camera = None


    # -------------------------------
    # Start Camera
    # -------------------------------

    def start_camera(self):

        if self.camera is None:

            self.camera = cv2.VideoCapture(0)

        return self.camera.isOpened()


    # -------------------------------
    # Get Frame
    # -------------------------------

    def get_frame(self):

        if self.camera is None:

            return None

        success, frame = self.camera.read()

        if not success:

            return None

        return frame


    # -------------------------------
    # Stop Camera
    # -------------------------------

    def stop_camera(self):

        if self.camera is not None:

            self.camera.release()

            self.camera = None


# ===================================
# Testing
# ===================================

if __name__ == "__main__":

    manager = CameraManager()

    if not manager.start_camera():

        print("Unable to open webcam.")

        exit()

    print("Camera Started Successfully.")
    print("Press Q to Exit.")

    while True:

        frame = manager.get_frame()

        if frame is None:

            break

        cv2.imshow("Camera Manager Test", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

    manager.stop_camera()

    cv2.destroyAllWindows()

    print("Camera Closed.")
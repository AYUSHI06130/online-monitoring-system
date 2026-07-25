import cv2
import threading


class CameraStream:

    def __init__(self):

        self.camera = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    # ---------------------------------------
    # Start Camera
    # ---------------------------------------

    def start(self):

        if self.running:
            return

        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            raise RuntimeError("Unable to open webcam.")

        self.running = True

        threading.Thread(
            target=self.update_frames,
            daemon=True
        ).start()

    # ---------------------------------------
    # Background Thread
    # ---------------------------------------

    def update_frames(self):

        while self.running:

            success, frame = self.camera.read()

            if success:

                with self.lock:
                    self.frame = frame.copy()

    # ---------------------------------------
    # Latest Frame
    # ---------------------------------------

    def get_frame(self):

        with self.lock:

            if self.frame is None:
                return None

            return self.frame.copy()

    # ---------------------------------------
    # Stop Camera
    # ---------------------------------------

    def stop(self):

        self.running = False

        if self.camera:

            self.camera.release()


camera_stream = CameraStream()
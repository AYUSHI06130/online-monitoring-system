import cv2

from utils.face_monitor import FaceMonitor


class CameraManager:

    def __init__(self, candidate_id):

        self.camera = None
        self.candidate_id = candidate_id

        self.face_monitor = FaceMonitor(candidate_id)

    # ---------------------------------
    # Start Camera
    # ---------------------------------

    def start_camera(self):

        if self.camera is None:

            self.camera = cv2.VideoCapture(0)

        return self.camera.isOpened()

    # ---------------------------------
    # Get Frame
    # ---------------------------------

    def get_frame(self):

        if self.camera is None:

            return None

        success, frame = self.camera.read()

        if not success:

            return None

        frame = self.face_monitor.process_frame(frame)

        return frame

    # ---------------------------------
    # Stop Camera
    # ---------------------------------

    def stop_camera(self):

        self.face_monitor.stop()

        if self.camera is not None:

            self.camera.release()
            self.camera = None

        cv2.destroyAllWindows()
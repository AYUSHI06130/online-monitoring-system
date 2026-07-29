import cv2
import sqlite3
import time
import os

from datetime import datetime
from config import DATABASE


class FaceMonitor:

    def __init__(self, candidate_id):

        self.candidate_id = candidate_id

        self.SCREENSHOT_FOLDER = "screenshots"
        os.makedirs(self.SCREENSHOT_FOLDER, exist_ok=True)

        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        self.previous_status = None

        self.absence_start_time = None
        self.absence_duration = 0
        self.total_absence_duration = 0

        self.face_not_detected_count = 0
        self.face_absence_count = 0

        self.session_start_time = datetime.now()

    # --------------------------------------------------

    def log_event(self, event_type, remarks):

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute("""
            SELECT session_id
            FROM Session
            WHERE candidate_id = ?
            ORDER BY session_id DESC
            LIMIT 1
        """, (self.candidate_id,))

        result = cursor.fetchone()

        if result is None:
            connection.close()
            return

        session_id = result[0]

        cursor.execute(
            """
            INSERT INTO EventLog
            (
                candidate_id,
                session_id,
                event_type,
                timestamp,
                remarks
            )

            VALUES (?, ?, ?, ?,?)
            """,
            (
                self.candidate_id,
                session_id,
                event_type,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                remarks
            )
        )

        connection.commit()
        connection.close()

    # --------------------------------------------------

    def update_monitoring_status(
        self,
        face_status,
        absence_count
    ):

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO MonitoringStatus
            (

                candidate_id,

                face_status,

                face_absence_count,

                browser_status,

                browser_focus_loss_count,

                last_updated

            )

            VALUES
            (
                ?,
                ?,
                ?,

                COALESCE(
                    (
                        SELECT browser_status
                        FROM MonitoringStatus
                        WHERE candidate_id=?
                    ),
                    'Browser Active'
                ),

                COALESCE(
                    (
                        SELECT browser_focus_loss_count
                        FROM MonitoringStatus
                        WHERE candidate_id=?
                    ),
                    0
                ),

                ?
            )
            """,
            (
                self.candidate_id,
                face_status,
                absence_count,
                self.candidate_id,
                self.candidate_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        connection.commit()
        connection.close()

    # --------------------------------------------------

    def capture_screenshot(self, frame):

        filename = (
            f"{self.candidate_id}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )

        filepath = os.path.join(
            self.SCREENSHOT_FOLDER,
            filename
        )

        cv2.imwrite(filepath, frame)

        print("Screenshot Saved:", filepath)

        return filepath

    # --------------------------------------------------

    def process_frame(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40)
        )

        if len(faces) > 0:

            status = "Face Detected"
            color = (0, 255, 0)

            if self.absence_start_time is not None:

                total_absence = int(
                    time.time() - self.absence_start_time
                )

                self.total_absence_duration += total_absence

                self.log_event(
                    "Face Returned",
                    f"Candidate returned after {total_absence} seconds"
                )

                self.absence_start_time = None
                self.absence_duration = 0

            if self.previous_status != status:

                self.log_event(
                    "Face Detected",
                    "Candidate is visible"
                )

                self.previous_status = status

                self.update_monitoring_status(
                    "Face Detected",
                    self.face_absence_count
                )

        else:

            status = "Face Not Detected"
            color = (0, 0, 255)

            if self.absence_start_time is None:

                self.absence_start_time = time.time()

                self.face_absence_count += 1

                screenshot_path = self.capture_screenshot(frame)

                self.log_event(
                    "Screenshot Captured",
                    screenshot_path
                )

            self.absence_duration = int(
                time.time() - self.absence_start_time
            )

            if self.previous_status != status:

                self.face_not_detected_count += 1

                self.log_event(
                    "Face Not Detected",
                    "Candidate left webcam"
                )

                self.previous_status = status

                self.update_monitoring_status(
                    "Face Not Detected",
                    self.face_absence_count
                )

        for (x, y, w, h) in faces:

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        cv2.putText(
            frame,
            status,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )

        cv2.putText(
            frame,
            f"Candidate ID: {self.candidate_id}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

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

        cv2.putText(
            frame,
            f"Absence Duration: {self.absence_duration} sec",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Total Absence Duration: {self.total_absence_duration} sec",
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        return frame

    # --------------------------------------------------

    def stop(self):

        print("Monitoring Stopped Successfully.")
        print("Session Summary:")
        print(
            f"Session started at: "
            f"{self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(
            f"Session ended at: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(
            f"Total Absence Duration: "
            f"{self.total_absence_duration} sec"
        )
        print(
            f"Face Not Detected Count: "
            f"{self.face_not_detected_count}"
        )
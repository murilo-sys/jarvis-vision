import ctypes
import time
import winsound


class PostureMonitor:
    def __init__(self):
        self.base_shoulders_y = 0
        self.tolarance = 15
        self.empty_since = None
        self.lock_delay = 2.0

    def calibrate(self, current_shoulders_y: int):
        self.base_shoulders_y = current_shoulders_y

    def check_posture(
        self, left_shoulder_y: int, right_shoulder_y: int
    ) -> tuple[bool, int]:
        # user is present in front of the camera, reset absence timer
        self.empty_since = None

        # calculate the medium height between shoulders
        current_shoulders_y = int((left_shoulder_y + right_shoulder_y) / 2)

        # if is the first time running the app
        if self.base_shoulders_y == 0:
            self.calibrate(current_shoulders_y)

        # calculate the limit line y
        limit_line_y = self.base_shoulders_y + self.tolarance

        if current_shoulders_y > limit_line_y:
            return False, limit_line_y

        return True, limit_line_y

    def check_absence(self) -> int:
        # start timer when user leaves the camera
        now = time.monotonic()
        if self.empty_since is None:
            self.empty_since = now

        elapsed = now - self.empty_since
        remaining = max(0, int(self.lock_delay - elapsed) + 1)

        # lock Windows after 5 seconds without anyone in front of the camera
        if elapsed >= self.lock_delay:
            ctypes.windll.user32.LockWorkStation()
            # wait 10 seconds before locking again so user can type password
            self.empty_since = now + 10.0

        return remaining

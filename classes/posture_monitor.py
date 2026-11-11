import winsound


class PostureMonitor:
    def __init__(self):
        self.base_shoulders_y = 0
        self.tolarance = 15

    def calibrate(self, current_shoulders_y: int):
        self.base_shoulders_y = current_shoulders_y

    def check_posture(
        self, left_shoulder_y: int, right_shoulder_y: int
    ) -> tuple[bool, int]:
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

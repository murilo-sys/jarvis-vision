import cv2
import math
import mediapipe as mp
from classes.volume_control import VolumeControler
from classes.posture_monitor import PostureMonitor

# Google pose detector
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose()

# Google hands intelligent
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Create the detector (max_num_hands focus only in one hand to be fast)
hands_detector = mp_hands.Hands(max_num_hands=1)

# Instance classes
volume_controler = VolumeControler()
posture_monitor = PostureMonitor()

camera = cv2.VideoCapture(0)

while True:
    sucesso, frame = camera.read()

    if not sucesso:
        print("Erro ao conectar na câmera")
        break

    # flip the frame like a mirror
    frame = cv2.flip(frame, 1)

    # get the weight and width on pixels
    height, width, _ = frame.shape

    # convert BGR from openCV to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # execute IA to find the hand
    hand_result = hands_detector.process(frame_rgb)

    # execute IA to find the shoulders/body
    pose_result = pose_detector.process(frame_rgb)

    if pose_result.pose_landmarks:
        # get landmarks from body
        landamarks = pose_result.pose_landmarks.landmark

        # get left (11) and right (12) shoulders position
        left_sh = landamarks[11]
        right_sh = landamarks[12]

        # convert the position (0.0 - 1.0) to real pixels from screen
        lx, ly = int(left_sh.x * width), int(left_sh.y * height)
        rx, ry = int(right_sh.x * width), int(right_sh.y * height)

        # check if the posture is aligned with the limit line
        posture_ok, limit_y = posture_monitor.check_posture(ly, ry)

        # green if posture is ok, red if slouching
        color = (0, 255, 0) if posture_ok else (0, 0, 255)

        # draw circles on shoulders and the limit line on screen
        cv2.circle(frame, (lx, ly), 8, color, -1)
        cv2.circle(frame, (rx, ry), 8, color, -1)
        cv2.line(frame, (lx, ly), (rx, ry), color, 3)
        cv2.line(frame, (0, limit_y), (width, limit_y), color, 2)

        if not posture_ok:
            cv2.putText(
                frame,
                "SENTA DIREITO!",
                (150, 250),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 0, 255),
                4,
            )
    else:
        # if no body is detected, start countdown to lock Windows
        seconds_left = posture_monitor.check_absence()
        cv2.putText(
            frame,
            f"Locking PC in {seconds_left}s...",
            (150, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 165, 255),
            3,
        )

    if hand_result.multi_hand_landmarks:
        for hand in hand_result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # get position from fingers
            thumb = hand.landmark[4]
            forefinger = hand.landmark[8]

            # convert the position (became like 0.0 - 1.0) to real pixels from screen
            x1, y1 = int(thumb.x * width), int(thumb.y * height)
            x2, y2 = int(forefinger.x * width), int(forefinger.y * height)

            # create the circles and lines in image
            cv2.circle(frame, (x1, y1), 10, (255, 230, 0), -1)
            cv2.circle(frame, (x2, y2), 10, (255, 230, 0), -1)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 230, 0), 3)

            # calculate the distance between the fingers
            distance = int(math.hypot(x2 - x1, y2 - y1))

            volume = volume_controler.change_by_the_distance(distance)

            cv2.putText(
                frame,
                f"Volume: {volume}%",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 230, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Distance: {distance}",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 230, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Volume Locked: {volume_controler.volume_locked}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 230, 0),
                2,
            )

    # listen to keyboard shortcuts (q = quit, v = lock volume, c = calibrate posture)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    elif key == ord("v"):
        volume_controler.volume_locked = not volume_controler.volume_locked
    elif key == ord("c"):
        if pose_result.pose_landmarks:
            posture_monitor.calibrate(int((ly + ry) / 2))

camera.release()
cv2.destroyAllWindows()

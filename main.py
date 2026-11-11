import cv2
import math
import mediapipe as mp

# Google hands inteligent
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Create the detector (max_num_hands focus only in one hand to be fast)
hands_detector = mp_hands.Hands(max_num_hands=1)

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
    result = hands_detector.process(frame_rgb)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
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

            cv2.putText(
                frame,
                f"Distance: {distance}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 230, 0),
                2,
            )

    cv2.imshow("Jarvis Vision", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

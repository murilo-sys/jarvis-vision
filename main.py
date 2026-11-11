import cv2

camera = cv2.VideoCapture(0)

while True:
    sucesso, frame = camera.read()

    if not sucesso:
        print("Erro ao conectar na câmera")
        break

    frame = cv2.flip(frame, 1)

    cv2.imshow("Jarvis Vision", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

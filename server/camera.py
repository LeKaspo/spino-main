import cv2

# Stream-URL
stream_url = 'http://192.168.0.145:8090/?action=stream'

# VideoCapture öffnen
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Fehler: Stream konnte nicht geöffnet werden.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fehler: Kein Frame empfangen.")
        break

     # Text auf das Frame zeichnen
    text = "Wuiiii Text"
    position = (10, 30)  # x, y Position
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (0, 255, 0)  # Grün
    thickness = 2

    cv2.putText(frame, text, position, font, font_scale, color, thickness)

    # Frame anzeigen
    cv2.imshow('Live Stream', frame)

    # Mit 'q' beenden
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Aufräumen
cap.release()
cv2.destroyAllWindows()

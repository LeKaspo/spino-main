
import pygame
import cv2
import numpy as np

# Pygame initialisieren
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

stream_url = 'http://192.168.0.145:8090/?action=stream'

cap = cv2.VideoCapture(stream_url)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Frame von Webcam holen
    ret, frame = cap.read()
    if not ret:
        continue

    # Frame konvertieren (BGR → RGB)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame)  # Optional: drehen
    frame = pygame.surfarray.make_surface(frame)

    # Frame anzeigen
    screen.blit(frame, (0, 0))
    pygame.display.flip()
    clock.tick(30)

# Aufräumen
cap.release()
pygame.quit()

#!/bin/bash

# Kamera-Gerät
DEVICE="/dev/video0"

# Auflösung und Framerate
RESOLUTION="640x480"
FRAMERATE="30"

# MJPG-Streamer Pfade
INPUT="/snap/mjpg-streamer/current/lib/mjpg-streamer/input_uvc.so"
OUTPUT="/snap/mjpg-streamer/current/lib/mjpg-streamer/output_http.so"
WWW="/snap/mjpg-streamer/current/www"

# Startbefehl
mjpg-streamer -i "$INPUT -r $RESOLUTION -f $FRAMERATE -d $DEVICE" \
              -o "$OUTPUT -p 8090 -w $WWW"

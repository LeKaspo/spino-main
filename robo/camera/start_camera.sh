#!/bin/bash

DEVICE="/dev/video0"

# resolución y velocidad de fotogramas
RESOLUTION="1920x1080"
FRAMERATE="30"

# ruta del archivo para MJPG
INPUT="/snap/mjpg-streamer/current/lib/mjpg-streamer/input_uvc.so"
OUTPUT="/snap/mjpg-streamer/current/lib/mjpg-streamer/output_http.so"
WWW="/snap/mjpg-streamer/current/www"

# empiezar la transmisón
mjpg-streamer -i "$INPUT -r $RESOLUTION -f $FRAMERATE -d $DEVICE" \
              -o "$OUTPUT -p 8090 -w $WWW"

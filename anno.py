#!/usr/bin/python
# video timestamp demo from http://picamera.readthedocs.org/en/release-1.8/recipes1.html

import atexit
import datetime as dt
import time
import itertools
import io
import os
import picamera
import pygame
import time
import yuv2rgb
from pygame.locals import *
from subprocess import call

# Init camera and set up default values
camera            = picamera.PiCamera()
atexit.register(camera.close)
camera.resolution = (320, 320)

camera.annotate_background = True
camera.annotate_text = dt.datetime.now().strftime('%m/%d/%Y %H:%M')
camera.start_recording('tempcam.h264')

start = dt.datetime.now()

# Init framebuffer/touchscreen environment variables
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV'      , '/dev/fb1')
os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

# Buffers for viewfinder data
rgb = bytearray(320 * 320 * 3)
yuv = bytearray(320 * 320 * 3 / 2)

# Init pygame and screen
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

while (dt.datetime.now() - start).seconds < 15:
    camera.wait_recording(0.2)
    stream = io.BytesIO() # Capture into in-memory stream
    camera.capture(stream, use_video_port=True, format='raw')
    stream.seek(0)
    stream.readinto(yuv)  # stream -> YUV buffer
    stream.close()
    yuv2rgb.convert(yuv, rgb, 320, 320)
    img = pygame.image.frombuffer(rgb[0:(320 * 320 * 3)], (320, 320), 'RGB')

    screen.blit(img,
      ((320 - img.get_width() ) / 2,
       (320 - img.get_height()) / 2))

    pygame.display.update()

camera.stop_recording()

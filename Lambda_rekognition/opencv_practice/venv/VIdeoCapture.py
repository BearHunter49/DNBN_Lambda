import cv2
from moviepy.editor import *


# video = VideoFileClip("test.mp4")
# audio = video.audio
# audio.write_audiofile("my.mp3")


cap = cv2.VideoCapture('test.mp4')
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter("result.mp4", fourcc, 23, (852, 480))

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        writer.write(frame)

    else:
        break

cap.release()
cv2.destroyAllWindows()


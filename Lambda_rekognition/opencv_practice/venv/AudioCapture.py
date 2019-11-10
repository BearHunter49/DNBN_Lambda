from moviepy.editor import *


video = VideoFileClip("result.mp4")
audio = AudioFileClip("my.mp3")
# audio = video.audio
# audio.write_audiofile("my.mp3")

muxVideo = video.set_audio(audio)

muxVideo.write_videofile("muxResult.mp4")


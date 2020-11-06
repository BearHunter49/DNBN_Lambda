import boto3
import json
from moviepy.editor import *
import os


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    os.environ['IMAGEIO_FFMPEG_EXE'] = '/tmp'
    
    s3.download_file('bylivetest', 'rekognition/test.mp4', '/tmp/test.mp4')
    s3.download_file('bylivetest', 'ffmpeg-linux64-v4.1', '/tmp/ffmpeg-linux64-v4.1')
    s3.download_file('bylivetest', 'rekognition/test_.mp4', '/tmp/test_.mp4')

    video = VideoFileClip("/tmp/test.mp4")
    audio = video.audio
    audio.write_audiofile("/tmp/my.mp3")

    resultVideo = VideoFileClip("/tmp/test_.mp4")

    resultVideo.write_videofile("/tmp/muxResult.mp4", audio="/tmp/my.mp3")
    s3.upload_file("/tmp/muxResult.mp4", "bylivetest", "result.mp4")


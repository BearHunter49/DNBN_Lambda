import boto3
from moviepy.editor import *
import os


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    os.environ['IMAGEIO_FFMPEG_EXE'] = '/tmp'

    s3.download_file('bylivetest', 'ffmpeg-linux64-v4.1', '/tmp/ffmpeg-linux64-v4.1')
    s3.download_file('bylivetest', 'rekognition/test.mp4', '/tmp/test.mp4')
    s3.download_file('bylivetest', 'rekognition/final.mp4', '/tmp/test2.mp4')

    originalVideo = VideoFileClip('/tmp/test.mp4')
    audio = originalVideo.audio
    audio.write_audiofile('/tmp/my.mp3')

    resultVideo = VideoFileClip('/tmp/test2.mp4')
    resultVideo.write_videofile('/tmp/result.mp4', audio='/tmp/my.mp3')

    s3.upload_file('/tmp/result.mp4', 'bylivetest', 'rekognition/finalResult.mp4')


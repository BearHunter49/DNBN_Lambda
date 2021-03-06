import cv2
import boto3
import json
from urllib.parse import unquote_plus
from moviepy.editor import *
import os
import time


rek = boto3.client('rekognition')
mosaic_rate = 20

# Rotate Method
def rotate(mat, angle):
    height, width = mat.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)

    abs_cos = abs(matrix[0, 0])
    abs_sin = abs(matrix[0, 1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    matrix[0, 2] += bound_w / 2 - (width / 2)
    matrix[1, 2] += bound_h / 2 - (height / 2)

    mat = cv2.warpAffine(mat, matrix, (bound_w, bound_h))
    return mat


def get_box_parameters(box, width, height):
    box_width = int(box['Width'] * width)
    box_height = int(box['Height'] * height)
    box_left = int(box['Left'] * width)
    box_top = int(box['Top'] * height)

    box_right = box_left + box_width
    box_bottom = box_top + box_height

    # check overflow
    if box_right >= width:
        box_right = width
        box_width = box_right - box_left
    if box_bottom >= height:
        box_bottom = height
        box_height = box_bottom - box_top
    if box_left < 0:
        box_left = 0
        box_width = box_right - box_left
    if box_top < 0:
        box_top = 0
        box_height = box_bottom - box_top

    box_dict = {
        'left': box_left,
        'right': box_right,
        'top': box_top,
        'bottom': box_bottom,
        'width': box_width,
        'height': box_height
    }
    return box_dict


def mosaic(box_prev, box_next, frame, width, height, ratio):

    # rotate and mosaic
    frame = rotate(frame, -90)

    # if next box is None
    if not box_next:
        box_dict = get_box_parameters(box_prev, width, height)

        # mosaic
        face_img = frame[box_dict['top']:box_dict['bottom'], box_dict['left']:box_dict['right']]
        face_img = cv2.resize(face_img, (box_dict['width'] // mosaic_rate, box_dict['height'] // mosaic_rate))
        face_img = cv2.resize(face_img, (box_dict['width'], box_dict['height']), cv2.INTER_AREA)
        frame[box_dict['top']:box_dict['bottom'], box_dict['left']:box_dict['right']] = face_img
        return frame

    # if both box exist
    else:
        box_dict_prev = get_box_parameters(box_prev, width, height)
        box_dict_next = get_box_parameters(box_next, width, height)

        box_left = 0
        box_top = 0

        # check direction
        horizon_gap = box_dict_prev['left'] - box_dict_next['left']
        if horizon_gap < 0:
            # right
            box_left = box_dict_prev['left'] + int(abs(horizon_gap) * ratio)
        else:
            # left
            box_left = box_dict_prev['left'] - int(abs(horizon_gap) * ratio)

        vertical_gap = box_dict_prev['top'] - box_dict_next['top']
        if vertical_gap < 0:
            # down
            box_top = box_dict_prev['top'] + int(abs(vertical_gap) * ratio)
        else:
            # up
            box_top = box_dict_prev['top'] - int(abs(vertical_gap) * ratio)

        box_right = box_left + box_dict_prev['width']
        box_bottom = box_top + box_dict_prev['height']

        # mosaic
        face_img = frame[box_top:box_bottom, box_left:box_right]
        face_img = cv2.resize(face_img, (box_dict_prev['width'] // mosaic_rate, box_dict_prev['height'] // mosaic_rate))
        face_img = cv2.resize(face_img, (box_dict_prev['width'], box_dict_prev['height']), cv2.INTER_AREA)
        frame[box_top:box_bottom, box_left:box_right] = face_img
        return frame


def video_processing(job_id, path):
    maxResults = 10
    paginationToken = ''
    finished = False

    # Get Meta Data
    response = rek.get_face_search(JobId=job_id, MaxResults=1)
    frameRate = response['VideoMetadata']['FrameRate']
    width = response['VideoMetadata']['FrameWidth']
    height = response['VideoMetadata']['FrameHeight']

    # OpenCV Video read and write
    cap = cv2.VideoCapture(path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    result_path = path.split(".")[0] + "_.mp4"
    writer = cv2.VideoWriter(result_path, fourcc, frameRate, (width, height))

    # MoviePy
    originalVideo = VideoFileClip(path)
    audio = originalVideo.audio
    audio.write_audiofile("/tmp/my.mp3")

    # Variables
    prev_timeStamp = 0
    cur_timeStamp = 0
    box_dict_pre = dict()
    box_dict_next = dict()
    start_check = 0
    while finished == False:
        response = rek.get_face_search(JobId=job_id, MaxResults=maxResults, NextToken=paginationToken)

        for faceDetection in response['Persons']:
            face_matches = faceDetection['FaceMatches']
            time_stamp = faceDetection['Timestamp']
            bounding_box = faceDetection['Person']['Face']['BoundingBox']
            index = faceDetection['Person']['Index']

            # when timestamp changed,
            if cur_timeStamp != time_stamp:

                # initial part
                if start_check == 0:
                    start_check = 1
                    cur_timeStamp = time_stamp
                    if not face_matches:
                        box_dict_next[index] = bounding_box

                else:
                    # implicit mosaic part
                    cap.set(cv2.CAP_PROP_POS_MSEC, prev_timeStamp)
                    prev_cur_time_gap = cur_timeStamp - prev_timeStamp
                    while True:
                        ret, frame = cap.read()

                        # if read success
                        if ret:
                            current_time = cap.get(cv2.CAP_PROP_POS_MSEC)

                            # check time
                            if current_time >= cur_timeStamp:
                                prev_timeStamp = cur_timeStamp
                                cur_timeStamp = time_stamp

                                box_dict_pre = box_dict_next
                                box_dict_next = dict()

                                # check is this first loop non_face_match
                                if not face_matches:
                                    box_dict_next[index] = bounding_box
                                break

                            # implicit mosaic
                            time_gap = current_time - prev_timeStamp
                            ratio = time_gap / prev_cur_time_gap

                            # mosaic
                            for key, value in box_dict_pre.items():
                                value_next = box_dict_next.get(key)
                                # if exist same index
                                if value_next:
                                    frame = mosaic(value, value_next, frame, width, height, ratio)
                                # if non-exist same index
                                else:
                                    frame = mosaic(value, None, frame, width, height, ratio)

                            # write video
                            writer.write(frame)
                        # fail(last)
                        else:
                            break

            # when timestamp same,
            else:
                # initial part
                if start_check == 0:
                    # exist non_face_match
                    if not face_matches:
                        box_dict_pre[index] = bounding_box
                else:
                    # exist non_face_match
                    if not face_matches:
                        box_dict_next[index] = bounding_box


            # print("width:{} height:{} left:{} top:{} right:{} bottom:{}".format(box_width, box_height, box_left,
            #                                                                     box_top, box_right, box_bottom))

        if 'NextToken' in response:
            paginationToken = response['NextToken']
        else:
            finished = True

    # write remained part
    cap.set(cv2.CAP_PROP_POS_MSEC, prev_timeStamp)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame = rotate(frame, -90)
            writer.write(frame)
        else:
            break

    cap.release()

    # Add Audio to Result Video File
    time.sleep(2)
    resultVideo = VideoFileClip(result_path)
    time.sleep(2)
    result_path = result_path.split(".")[0] + "final.mp4"
    resultVideo.write_videofile(result_path, audio="/tmp/my.mp3")

    return result_path


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    os.environ['IMAGEIO_FFMPEG_EXE'] = '/tmp'

    # string type
    # message = event['Records'][0]['Sns']['Message']
    # message_json = json.loads(message)

    # jobId = message_json["JobId"]
    # status = message_json["Status"]
    # bucket = message_json["Video"]["S3Bucket"]
    # video = message_json["Video"]["S3ObjectName"]

    jobId = '0e6bdeae52d2170386d4d00d8d9d45a2c33c533262fad3503f2be9d40a49246c'
    video = unquote_plus('rekognition/test.mp4')
    bucket = 'bylivetest'
    download_path = '/tmp/test.mp4'

    s3.download_file(bucket, 'ffmpeg-linux64-v4.1', '/tmp/ffmpeg-linux64-v4.1')

    # check success
    # if status == "SUCCEEDED":
    s3.download_file(bucket, video, download_path)

    resultPath = video_processing(jobId, download_path)

    s3.upload_file(resultPath, bucket, 'rekognition/final.mp4')

    return {}

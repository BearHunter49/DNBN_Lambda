import cv2
import boto3
import json
from urllib.parse import unquote_plus
import uuid


s3 = boto3.client('s3')
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


def mosaic(box, frame, width, height):
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

    # rotate and mosaic
    frame = rotate(frame, -90)

    # mosaic
    face_img = frame[box_top:box_bottom, box_left:box_right]
    face_img = cv2.resize(face_img, (box_width // mosaic_rate, box_height // mosaic_rate))
    face_img = cv2.resize(face_img, (box_width, box_height), cv2.INTER_AREA)
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

    # Variables
    temp_timeStamp = 0
    box_list = []
    while finished == False:
        response = rek.get_face_search(JobId=job_id, MaxResults=maxResults, NextToken=paginationToken)

        for faceDetection in response['Persons']:
            face_matches = faceDetection['FaceMatches']

            # non-exist face_match
            if not face_matches:
                # Time Stamp
                time_stamp = faceDetection['Timestamp']
                bounding_box = faceDetection['Person']['Face']['BoundingBox']

                # if same era
                if temp_timeStamp == time_stamp:
                    box_list.append(bounding_box)

                # if different era
                else:
                    # implicit mosaic part
                    cap.set(cv2.CAP_PROP_POS_MSEC, temp_timeStamp)
                    while True:
                        ret, frame = cap.read()

                        # if read success
                        if ret:
                            current_time = cap.get(cv2.CAP_PROP_POS_MSEC)

                            # check time
                            if current_time >= time_stamp:
                                temp_timeStamp = time_stamp
                                box_list.clear()
                                box_list.append(bounding_box)
                                break

                            # mosaic N face at 1 frame
                            for box in box_list:
                                frame = mosaic(box, frame, width, height)

                            # write video
                            writer.write(frame)
                        # fail(last)
                        else:
                            break

            # print("width:{} height:{} left:{} top:{} right:{} bottom:{}".format(box_width, box_height, box_left,
            #                                                                     box_top, box_right, box_bottom))

        if 'NextToken' in response:
            paginationToken = response['NextToken']
        else:
            finished = True

    # write remained part
    cap.set(cv2.CAP_PROP_POS_MSEC, temp_timeStamp)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame = rotate(frame, -90)
            writer.write(frame)
        else:
            break

    cap.release()
    return result_path


def lambda_handler(event, context):

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
    download_path = "/tmp/test.mp4"

    # check success
    # if status == "SUCCEEDED":
    s3.download_file(bucket, video, download_path)
    resultPath = video_processing(jobId, download_path)

    s3.upload_file(resultPath, bucket, 'rekognition/test_.mp4')

    return {}


import json
import boto3


def lambda_handler(event, context):
    
    roleArn = 'arn:aws:iam::733716404034:role/Rekognition_role'
    snsTopicArn = 'arn:aws:sns:ap-northeast-2:733716404034:AmazonRekognitionExample0101'
    bucket = 'bylivetest'
    video = 'rekognition/test.mp4'
    
    rek = boto3.client('rekognition')
    
    # start face detection
    response=rek.start_face_detection(Video={'S3Object': {'Bucket': bucket, 'Name': video}},
            NotificationChannel={'SNSTopicArn': snsTopicArn, 'RoleArn': roleArn})
    
    

    return {
        'JobId': response['JobId']
    }

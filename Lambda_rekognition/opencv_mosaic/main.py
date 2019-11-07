import cv2
import boto3


def lambda_handler(event, context):
    return {
        'result': str(cv2.__version__),
        'version': str(boto3.__version__)
    }


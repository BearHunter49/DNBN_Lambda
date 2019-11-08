import json
import boto3


def lambda_handler(event, context):
    
    collection_id='MyCollection'
    bucket='bylivetest'
    photo='rekognition/myFace.jpg'
    video='rekognition/test.mp4'
    
    rek = boto3.client('rekognition')
  

    # response = rek.create_collection(CollectionId=collection_id)
    # response = rek.index_faces(CollectionId=collection_id,
    #                             Image={'S3Object':{'Bucket':bucket,'Name':photo}},
    #                             MaxFaces=1,
    #                             QualityFilter="AUTO",
    #                             DetectionAttributes=['ALL'])
    
    # response = rek.list_faces(CollectionId=collection_id, MaxResults=3)
                                
    # response = rek.delete_faces(CollectionId=collection_id, FaceIds=['99415407-35b2-451f-b7ad-695b409bcc1b'])
    
    
    response = rek.start_face_search(
            Video={
            'S3Object': {
                'Bucket': bucket,
                'Name': video,
            }
        },
        CollectionId=collection_id,
        NotificationChannel={
            'SNSTopicArn': 'arn:aws:sns:ap-northeast-2:733716404034:AmazonRekognitionFaceExample01',
            'RoleArn': 'arn:aws:iam::733716404034:role/Rekognition_role'
        })
    
    
    
   
    return {
        'result': response
    }

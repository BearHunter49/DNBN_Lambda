import boto3
import mliveChannel
import mliveInput
from datetime import datetime
import time as t

# client 받아오기
client_s3 = boto3.client('s3')
client_medialive = boto3.client('medialive')

# Time
now = datetime.now()
if now.hour + 9 > 24:
    time = '{}{:02}{:02}{:02}{:02}'.format(now.year, now.month, now.day + 1, now.hour - 15, now.minute)
else:
    time = '{}{:02}{:02}{:02}{:02}'.format(now.year, now.month, now.day, now.hour + 9, now.minute)


# event = {
#     'action': 'start/stop',
#     'user': 'userName',
#     'channel_id': '1234567'
# }


def lambda_handler(event, context):
    mlive_chaClass = mliveChannel.C_mliveChannel(client_medialive)
    mlive_inpClass = mliveInput.C_mliveInput(client_medialive)

    action = event['action']
    user = event['user']
    channel_id = event['channel_id']

    # Case1: start channel
    if action == 'start':
        index = -1

        # search IDLE state
        for i in range(len(mlive_chaClass.client.list_channels()['Channels'])):
            if mlive_chaClass.getState(i) == 'IDLE':
                index = i
                break

        # Case1-1: IDLE exist
        if index != -1:
            channel_id = mlive_chaClass.getId(index)
            input_id = mlive_chaClass.getInputId(index)
            url = mlive_inpClass.getUrl(input_id)
            # source_url = 'rtmp://{}:1935/bylive/stream'.format(mlive_chaClass.getSourceIp(index))

            # path update and start
            try:
                mlive_chaClass.updateChannel(user, channel_id, time)
                mlive_chaClass.startChannel(channel_id)
            except Exception as e:
                return {
                    'error': e
                }
            else:
                return {
                    'state': 'exist',
                    'channel_id': channel_id,
                    'source_url': url,
                    'destination_url': mlive_chaClass.getDestinations(index)
                }

        # Case1-2: IDLE non-exist
        else:
            # create input
            try:
                input_response = mlive_inpClass.createInput(user, time)
            except Exception as e:
                return {
                    'error': e
                }
            else:
                input_id = input_response['Input']['Id']
                source_url = input_response['Input']['Destinations'][0]['Url']

            # create channel
            try:
                channel_response = mlive_chaClass.createChannel(user, input_id, time)
                channel_id = channel_response['Channel']['Id']
                index = mlive_chaClass.getIndexById(channel_id)

                while mlive_chaClass.getState(index) == 'CREATING':
                    t.sleep(1)
                mlive_chaClass.startChannel(channel_id)
            except Exception as e:
                return {
                    'error': e
                }

            return {
                'state': 'create',
                'channel_id': channel_id,
                'source_url': source_url,
                'destination_url': mlive_chaClass.getDestinations(index)
            }

    # Case2: stop channel
    elif action == 'stop':
        mlive_chaClass.stopChannel(channel_id)
        return {
            'state': 'stopped',
            'channel_id': channel_id,
        }





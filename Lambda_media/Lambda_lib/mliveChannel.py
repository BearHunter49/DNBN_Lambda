class C_mliveChannel:
    def __init__(self, client):
        self.client = client
        self.respMetaData = self.client.list_channels()["ResponseMetadata"]
        self.httpStatus = self.respMetaData["HTTPStatusCode"]
        self.httpHeaders = self.respMetaData["HTTPHeaders"]

    def getArn(self, index):
        channelResponse = self.client.list_channels()
        channels = channelResponse["Channels"]

        return channels[index]["Arn"]

    def getDestinations(self, index):
        channelResponse = self.client.list_channels()
        channels = channelResponse["Channels"]

        destList = channels[index]["Destinations"]
        resultDict = dict()
        for dest in destList:
            url = dest["Settings"][0]["Url"]
            if "mediastoressl" in url:
                resultDict['live'] = url
            else:
                resultDict['vod'] = url

        return resultDict

    def getInputId(self, index):
        channelResponse = self.client.list_channels()
        channels = channelResponse["Channels"]

        return channels[index]["InputAttachments"][0]["InputId"]



    def getId(self, index):
        channelResponse = self.client.list_channels()
        channels = channelResponse["Channels"]

        return channels[index]["Id"]

    def getIndexById(self, channel_id):
        channelResponse = self.client.list_channels()
        channels = channelResponse["Channels"]

        count = 0
        for channel in channels:
            if channel["Id"] == channel_id:
                return count
            else:
                count += 1

    def getName(self, index):
        channelResponse = self.client.list_channels()
        channels = channelResponse["Channels"]

        return channels[index]["Name"]

    def getState(self, index):
        channelResponse = self.client.list_channels()
        channels = channelResponse["Channels"]

        return channels[index]["State"]

    def startChannel(self, Id):
        return self.client.start_channel(ChannelId=Id)

    def stopChannel(self, Id):
        return self.client.stop_channel(ChannelId=Id)

    def updateChannel(self, name, channel_id, time):
        response = self.client.update_channel(
            ChannelId=channel_id,
            Destinations=[
                {
                    'Id': 'TestDestLive',
                    'Settings': [
                        {
                            'Url': f'mediastoressl://sywblelzxjjjqz.data.mediastore.ap-northeast-2.amazonaws.com/{name}/main',
                        },
                    ]
                },
                {
                    'Id': 'TestDestVOD',
                    'Settings': [
                        {
                            'Url': f's3://bylivetest/{name}/{time}/main',
                        },
                    ]
                }
            ]
        )
        return response

    def createChannel(self, name, input_id, time):
        response = self.client.create_channel(
            ChannelClass='SINGLE_PIPELINE',
            Destinations=[
                {
                    'Id': 'TestDestLive',
                    'Settings': [
                        {
                            'Url': f'mediastoressl://sywblelzxjjjqz.data.mediastore.ap-northeast-2.amazonaws.com/{name}/main',
                        },
                    ]
                },
                {
                    'Id': 'TestDestVOD',
                    'Settings': [
                        {
                            'Url': f's3://bylivetest/{name}/{time}/main',
                        },
                    ]
                }
            ],
            EncoderSettings={
                'AudioDescriptions': [
                    {
                        'AudioSelectorName': 'default',
                        'AudioTypeControl': 'FOLLOW_INPUT',
                        'CodecSettings': {
                            'AacSettings': {
                                "Bitrate": 128000,
                                "CodingMode": "CODING_MODE_2_0",
                                "InputType": "NORMAL",
                                "Profile": "LC",
                                "RateControlMode": "CBR",
                                "RawFormat": "NONE",
                                "SampleRate": 48000,
                                "Spec": "MPEG4"
                            }
                        },
                        'LanguageCodeControl': 'FOLLOW_INPUT',
                        'Name': 'audio_live',
                    },
                    {
                        'AudioSelectorName': 'default',
                        'AudioTypeControl': 'FOLLOW_INPUT',
                        'CodecSettings': {
                            'AacSettings': {
                                "Bitrate": 128000,
                                "CodingMode": "CODING_MODE_2_0",
                                "InputType": "NORMAL",
                                "Profile": "LC",
                                "RateControlMode": "CBR",
                                "RawFormat": "NONE",
                                "SampleRate": 48000,
                                "Spec": "MPEG4"
                            }
                        },
                        'LanguageCodeControl': 'FOLLOW_INPUT',
                        'Name': 'audio_vod',
                    }
                ],
                'CaptionDescriptions': [],
                'OutputGroups': [
                    {
                        'Name': 'Live_MediaStore',
                        'OutputGroupSettings': {
                            "HlsGroupSettings": {
                                "AdMarkers": [],
                                "CaptionLanguageMappings": [],
                                "CaptionLanguageSetting": "OMIT",
                                "ClientCache": "ENABLED",
                                "CodecSpecification": "RFC_4281",
                                "Destination": {
                                    "DestinationRefId": "TestDestLive"
                                },
                                "DirectoryStructure": "SINGLE_DIRECTORY",
                                "HlsCdnSettings": {
                                    "HlsBasicPutSettings": {
                                        "ConnectionRetryInterval": 30,
                                        "FilecacheDuration": 300,
                                        "NumRetries": 5,
                                        "RestartDelay": 5
                                    }
                                },
                                "IndexNSegments": 3,
                                "InputLossAction": "PAUSE_OUTPUT",
                                "IvInManifest": "INCLUDE",
                                "IvSource": "FOLLOWS_SEGMENT_NUMBER",
                                "KeepSegments": 21,
                                "ManifestCompression": "NONE",
                                "ManifestDurationFormat": "FLOATING_POINT",
                                "Mode": "LIVE",
                                "OutputSelection": "MANIFESTS_AND_SEGMENTS",
                                "ProgramDateTime": "INCLUDE",
                                "ProgramDateTimePeriod": 600,
                                "SegmentLength": 2,
                                "SegmentationMode": "USE_SEGMENT_DURATION",
                                "SegmentsPerSubdirectory": 10000,
                                "StreamInfResolution": "INCLUDE",
                                "TimedMetadataId3Frame": "PRIV",
                                "TimedMetadataId3Period": 10,
                                "TsFileMode": "SEGMENTED_FILES"
                            }
                        },
                        'Outputs': [
                            {
                                "AudioDescriptionNames": [
                                    "audio_live"
                                ],
                                "CaptionDescriptionNames": [],
                                "OutputSettings": {
                                    "HlsOutputSettings": {
                                        "HlsSettings": {
                                            "StandardHlsSettings": {
                                                "AudioRenditionSets": "PROGRAM_AUDIO",
                                                "M3u8Settings": {
                                                    "AudioFramesPerPes": 4,
                                                    "AudioPids": "492-498",
                                                    "EcmPid": "8182",
                                                    "PcrControl": "PCR_EVERY_PES_PACKET",
                                                    "PmtPid": "480",
                                                    "ProgramNum": 1,
                                                    "Scte35Behavior": "NO_PASSTHROUGH",
                                                    "Scte35Pid": "500",
                                                    "TimedMetadataBehavior": "NO_PASSTHROUGH",
                                                    "TimedMetadataPid": "502",
                                                    "VideoPid": "481"
                                                }
                                            }
                                        },
                                        "NameModifier": "_1080x1920"
                                    }
                                },
                                "VideoDescriptionName": "video_live"
                            }
                        ]
                    },
                    {
                        "Name": "VOD_S3",
                        "OutputGroupSettings": {
                            "HlsGroupSettings": {
                                "AdMarkers": [],
                                "CaptionLanguageMappings": [],
                                "CaptionLanguageSetting": "OMIT",
                                "ClientCache": "ENABLED",
                                "CodecSpecification": "RFC_4281",
                                "Destination": {
                                    "DestinationRefId": "TestDestVOD"
                                },
                                "DirectoryStructure": "SINGLE_DIRECTORY",
                                "HlsCdnSettings": {
                                    "HlsBasicPutSettings": {
                                        "ConnectionRetryInterval": 1,
                                        "FilecacheDuration": 300,
                                        "NumRetries": 10,
                                        "RestartDelay": 15
                                    }
                                },
                                "IndexNSegments": 10,
                                "InputLossAction": "PAUSE_OUTPUT",
                                "IvInManifest": "INCLUDE",
                                "IvSource": "FOLLOWS_SEGMENT_NUMBER",
                                "KeepSegments": 21,
                                "ManifestCompression": "NONE",
                                "ManifestDurationFormat": "FLOATING_POINT",
                                "Mode": "VOD",
                                "OutputSelection": "MANIFESTS_AND_SEGMENTS",
                                "ProgramDateTime": "EXCLUDE",
                                "ProgramDateTimePeriod": 600,
                                "SegmentLength": 10,
                                "SegmentationMode": "USE_SEGMENT_DURATION",
                                "SegmentsPerSubdirectory": 10000,
                                "StreamInfResolution": "INCLUDE",
                                "TimedMetadataId3Frame": "PRIV",
                                "TimedMetadataId3Period": 10,
                                "TsFileMode": "SEGMENTED_FILES"
                            }
                        },
                        "Outputs": [
                            {
                                "AudioDescriptionNames": [
                                    "audio_vod"
                                ],
                                "CaptionDescriptionNames": [],
                                "OutputSettings": {
                                    "HlsOutputSettings": {
                                        "HlsSettings": {
                                            "StandardHlsSettings": {
                                                "AudioRenditionSets": "program_audio",
                                                "M3u8Settings": {
                                                    "AudioFramesPerPes": 4,
                                                    "AudioPids": "492-498",
                                                    "PcrControl": "PCR_EVERY_PES_PACKET",
                                                    "PmtPid": "480",
                                                    "ProgramNum": 1,
                                                    "Scte35Behavior": "NO_PASSTHROUGH",
                                                    "Scte35Pid": "500",
                                                    "TimedMetadataBehavior": "NO_PASSTHROUGH",
                                                    "TimedMetadataPid": "502",
                                                    "VideoPid": "481"
                                                }
                                            }
                                        },
                                        "NameModifier": "_1080x1920"
                                    }
                                },
                                "VideoDescriptionName": "video_vod"
                            }
                        ]
                    }
                ],
                'TimecodeConfig': {
                    'Source': 'SYSTEMCLOCK',
                },
                'VideoDescriptions': [
                    {
                        "CodecSettings": {
                            "H264Settings": {
                                "AdaptiveQuantization": "HIGH",
                                "AfdSignaling": "NONE",
                                "Bitrate": 4700000,
                                "ColorMetadata": "INSERT",
                                "EntropyEncoding": "CABAC",
                                "FlickerAq": "ENABLED",
                                "FramerateControl": "SPECIFIED",
                                "FramerateDenominator": 1001,
                                "FramerateNumerator": 30000,
                                "GopBReference": "ENABLED",
                                "GopClosedCadence": 1,
                                "GopNumBFrames": 3,
                                "GopSize": 60,
                                "GopSizeUnits": "FRAMES",
                                "Level": "H264_LEVEL_4_1",
                                "LookAheadRateControl": "HIGH",
                                "NumRefFrames": 1,
                                "ParControl": "INITIALIZE_FROM_SOURCE",
                                "Profile": "HIGH",
                                "RateControlMode": "CBR",
                                "ScanType": "PROGRESSIVE",
                                "SceneChangeDetect": "ENABLED",
                                "SpatialAq": "ENABLED",
                                "Syntax": "DEFAULT",
                                "TemporalAq": "ENABLED",
                                "TimecodeInsertion": "DISABLED"
                            }
                        },
                        "Name": "video_live",
                        "RespondToAfd": "NONE",
                        "ScalingBehavior": "DEFAULT",
                        "Sharpness": 50,
                    },
                    {
                        "CodecSettings": {
                            "H264Settings": {
                                "AdaptiveQuantization": "MEDIUM",
                                "AfdSignaling": "NONE",
                                "Bitrate": 4700000,
                                "ColorMetadata": "INSERT",
                                "EntropyEncoding": "CABAC",
                                "FlickerAq": "ENABLED",
                                "FramerateControl": "INITIALIZE_FROM_SOURCE",
                                "GopBReference": "DISABLED",
                                "GopClosedCadence": 1,
                                "GopNumBFrames": 2,
                                "GopSize": 90,
                                "GopSizeUnits": "FRAMES",
                                "Level": "H264_LEVEL_AUTO",
                                "LookAheadRateControl": "MEDIUM",
                                "NumRefFrames": 1,
                                "ParControl": "INITIALIZE_FROM_SOURCE",
                                "Profile": "MAIN",
                                "RateControlMode": "CBR",
                                "ScanType": "PROGRESSIVE",
                                "SceneChangeDetect": "ENABLED",
                                "SpatialAq": "ENABLED",
                                "Syntax": "DEFAULT",
                                "TemporalAq": "ENABLED",
                                "TimecodeInsertion": "DISABLED"
                            }
                        },
                        "Name": "video_vod",
                        "RespondToAfd": "NONE",
                        "ScalingBehavior": "DEFAULT",
                        "Sharpness": 50,
                    }
                ]
            },
            InputAttachments=[
                {
                    'InputId': f'{input_id}',
                    "InputSettings": {
                        "AudioSelectors": [],
                        "CaptionSelectors": [],
                        "DeblockFilter": "DISABLED",
                        "DenoiseFilter": "DISABLED",
                        "FilterStrength": 1,
                        "InputFilter": "AUTO",
                        "SourceEndBehavior": "CONTINUE"
                    }
                },
            ],
            InputSpecification={
                "Codec": "AVC",
                "MaximumBitrate": "MAX_10_MBPS",
                "Resolution": "HD"
            },
            LogLevel='DISABLED',
            Name=f'{name}{time}',
            RoleArn='arn:aws:iam::733716404034:role/MediaLiveAccessRole',
        )
        return response

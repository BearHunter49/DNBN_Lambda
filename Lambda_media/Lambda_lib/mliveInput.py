class C_mliveInput:
    def __init__(self, client):
        self.client = client
        self.respMetaData = self.client.list_inputs()["ResponseMetadata"]
        self.httpStatus = self.respMetaData["HTTPStatusCode"]
        self.httpHeaders = self.respMetaData["HTTPHeaders"]

    def createInput(self, name, time):
        response = self.client.create_input(
            Destinations=[
                {
                    'StreamName': 'bylive/stream',
                },
            ],
            InputSecurityGroups=[
                '2515034',
            ],
            Name=f'{name}{time}',
            Type='RTMP_PUSH'
        )
        return response

    def getArn(self, index):
        inputResp = self.client.list_inputs()
        inputs = inputResp["Inputs"]

        return inputs[index]["Arn"]

    def getUrl(self, input_id):
        inputResp = self.client.describe_input(InputId=input_id)
        destinations = inputResp["Destinations"]

        return destinations[0]["Url"]

    def getId(self, index):
        inputResp = self.client.list_inputs()
        inputs = inputResp["Inputs"]

        return inputs[index]["Id"]

    def getName(self, index):
        inputResp = self.client.list_inputs()
        inputs = inputResp["Inputs"]

        return inputs[index]["Name"]

    def getState(self, index):
        inputResp = self.client.list_inputs()
        inputs = inputResp["Inputs"]

        return inputs[index]["State"]

    def getType(self, index):
        inputResp = self.client.list_inputs()
        inputs = inputResp["Inputs"]

        return inputs[index]["Type"]

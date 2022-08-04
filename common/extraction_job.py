class Job:
    def __init__(self, documents):
        self.documents = documents

    def toJSON(self):
        return {
            "jobId": "13a52c6a-4d34-448c-8e62-0a7335c59a06",
            "lastUpdateDateTime": "2022-06-23T14:03:24Z",
            "createdDateTime": "2022-06-23T14:03:21Z",
            "expirationDateTime": "2022-06-24T14:03:21Z",
            "status": "succeeded",
            "errors": [],
            "displayName": "CustomPartyData_extraction",
            "tasks": {
                "completed": 1,
                "failed": 0,
                "inProgress": 0,
                "total": 1,
                "customEntityRecognitionTasks": [
                    {
                        "lastUpdateDateTime": "2022-06-23T14:03:24.6752033Z",
                        "state": "succeeded",
                        "results": {
                            "documents": self.documents,
                            "errors": [],
                            "projectName": "partyentityrecognition",
                            "deploymentName": "partyentityrecognition"
                        }
                    }
                ]
            }
        }

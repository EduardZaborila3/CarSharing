import json

class CommunicationProtocol:
    def __init__(self, client_id, message_id, payload=""):
        self.client_id = client_id
        self.message_id = message_id
        self.payload = payload

    def serialize(self):
        message_dict = {
            "client_id": self.client_id,
            "message_id": self.message_id,
            "payload": self.payload
        }
        return json.dumps(message_dict)
    
    @staticmethod
    def deserialize(json_str):
        try:
            data = json.loads(json_str)
            return CommunicationProtocol(
                client_id = data["client_id"],
                message_id = data["message_id"],
                payload = data.get("payload", "")
            )
        except (json.JSONDecodeError, KeyError):
            return None

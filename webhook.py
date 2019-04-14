import requests
from requests.exceptions import ConnectTimeout, RequestException
import logging
logger = logging.getLogger(__name__)


class Webhook:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_contact_request(self, user_id, contactdetails):
        data = {
            "update_id": 999,
            "message": {
                "message_id": 999,
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "System",
                    "username": "system",
                    "language_code": "en"
                },
                "chat": {
                    "id": user_id,
                    "first_name": "System",
                    "username": "system",
                    "type": "private"
                },
                "date": 1555265276,
                "text": "/contactrequest " + str(contactdetails),
                "entities": [
                    {
                        "offset": 0,
                        "length": 15,
                        "type": "bot_command"
                    }
                ]
            }
        }
        try:
            r = requests.post(self.webhook_url, json=data, timeout=2)
            return True
        except ConnectTimeout as err:
            logger.error(err)
            return False
        except RequestException as err:
            logger.error(err)
            return False

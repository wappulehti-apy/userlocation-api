import requests
from requests.exceptions import ConnectTimeout, RequestException
from flask import current_app as app


class Webhook:
    def __init__(self, webhook_url):
        app.logger.info(f'webhook initialized with {webhook_url}')
        self.webhook_url = webhook_url

    def send_contact_request(self, user_id, buyer_id, contactdetails):
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
                    "id": 999,
                    "first_name": "System",
                    "username": "system",
                    "type": "private"
                },
                "date": 1555265276,
                "text": "/requestcall " + str(buyer_id) + " " + str(contactdetails),
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
            app.logger.info(f'webhook returned {r.status_code}')
            if r.status_code != 200:
                return False
            return True
        except ConnectTimeout as err:
            app.logger.error(err)
            return False
        except RequestException as err:
            app.logger.error(err)
            return False

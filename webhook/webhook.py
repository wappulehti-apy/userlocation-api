import requests
from requests.exceptions import ConnectTimeout, RequestException
from flask import current_app as app
import inspect


class Webhook:
    def init_app(self, app, webhook_url):
        self.app = app
        self.webhook_url = webhook_url

    def send(self, **kwargs):
        data = {
            "example": True,
            "message": "{client_id} message to {user_id}",
            "detail": "{message}"
        }
        formatted_data = {k: (v.format(**kwargs) if isinstance(v, str) else v) for k, v in data.items()}
        try:
            r = requests.post(self.webhook_url, json=formatted_data, timeout=5)
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

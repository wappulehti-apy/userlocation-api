from flask import Flask
from flask import current_app as app
from flask_restful import Resource, Api
from werkzeug.exceptions import HTTPException


class ExtendedApi(Api):
    def handle_error(self, err):
        """Extended error response formatting."""
        app.logger.error(err)
        response = {'error': True, 'message': 'unknown error'}
        if isinstance(err, HTTPException):
            if 'description' in err.__dict__:
                app.logger.error('desc')
                response['message'] = err.__dict__.get('description')
            elif 'data' in err.__dict__:
                app.logger.error('data')
                msg = err.data.get('message')
                if (isinstance(msg, dict)):
                    response['message'] = ','.join([f'invalid {k}: {v}' for k, v in msg.items()])
                else:
                    response['message'] = err.data.get('message')
        else:
            response['message'] = str(err)
        return response, err.code


def init_app(app):
    api = ExtendedApi(app)
    from . import location, message
    api.add_resource(location.LocationList, '/locations')
    api.add_resource(location.Location, '/locations/<int:user_id>')
    api.add_resource(message.Message, '/message')

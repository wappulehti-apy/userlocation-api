from flask import Flask
from flask import current_app as app
from flask_restful import Resource, Api


def init_app(app):
    api = Api(app)
    from . import location
    api.add_resource(location.LocationList, '/locations')
    api.add_resource(location.Location, '/locations/<int:user_id>')

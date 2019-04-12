import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql.json import JSONB

from database import db


class Location(db.Model):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    latitude = db.Column(Numeric(precision=8, asdecimal=False, decimal_return_scale=None))
    longitude = db.Column(Numeric(precision=8, asdecimal=False, decimal_return_scale=None))
    initials = Column(String, nullable=False)

    def __init__(self, id, latitude, longitude, initials):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.initials = initials

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_simple_json(self):
        return {
            'location': {'lat': self.latitude, 'lon': self.longitude},
            'initials': self.initials,
        }

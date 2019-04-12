import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, BigInteger, Numeric
from sqlalchemy.dialects.postgresql.json import JSONB

#db = SQLAlchemy()
from database import db


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(BigInteger, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    latitude = db.Column(Numeric(precision=8, asdecimal=False, decimal_return_scale=None))
    longitude = db.Column(Numeric(precision=8, asdecimal=False, decimal_return_scale=None))

    def __init__(self, id, latitude, longitude, contact=None):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.contact = contact

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_simple_json(self):
        return {
            "phone_number": "1023i01i2301",
            "coordinates": [5, 5]
        }

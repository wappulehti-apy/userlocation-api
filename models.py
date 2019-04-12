from app import db
from sqlalchemy import Column, DateTime, Integer, BigInteger
from sqlalchemy.dialects.postgresql.json import JSONB
import datetime


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(BigInteger, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    coordinates = Column(JSONB)

    def __init__(self, id, coordinates):
        self.id = id
        self.coordinates = coordinates

    def __repr__(self):
        return '<id {}>'.format(self.id)

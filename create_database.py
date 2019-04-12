import os
import sys
from sqlalchemy import create_engine
import config

from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.exc import OperationalError

from app import app, db, migrate
from models import Location


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

if app.config['DEVELOP']:
    logger.info("dropping database")
    db.drop_all()
    db.create_all()

logger.info("running migrations")
with app.app_context():
    from flask_migrate import upgrade as _upgrade
    _upgrade()

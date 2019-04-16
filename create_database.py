import sys
import logging
from sqlalchemy import create_engine

from models import Location
from app import create_app
from database import db
import config

app = create_app(redis_conn=None)

# Ensure logging works
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

logger.info("running migrations")
with app.app_context():
    from flask_migrate import upgrade as _upgrade
    _upgrade()

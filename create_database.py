import logging
from sqlalchemy.exc import OperationalError
from models import Location
from app import create_app
from database import db
import os
import sys
from sqlalchemy import create_engine
import config

app = create_app(redis_conn=None)

# from sqlalchemy.schema import DropTable
# from sqlalchemy.ext.compiler import compiles

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


# @compiles(DropTable, "postgresql")
# def _compile_drop_table(element, compiler, **kwargs):
#     return compiler.visit_drop_table(element) + " CASCADE"


# if app.config['DEVELOP']:
#     with app.app_context():
#         logger.info("dropping database")
#         db.session.remove()
#         db.drop_all()
#         db.create_all()

logger.info("running migrations")
with app.app_context():
    from flask_migrate import upgrade as _upgrade
    _upgrade()

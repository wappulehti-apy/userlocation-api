from flask import Blueprint, render_template

bp = Blueprint('localtest', __name__)


@bp.route('/')
def index():
    return render_template('test.html')

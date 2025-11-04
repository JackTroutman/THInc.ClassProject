from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskSetUp.auth import login_required
from flaskSetUp.db import get_db

bp = Blueprint('display', __name__)

@bp.route('/')
def index():
    db = get_db()
    items = db.execute(
        'SELECT id, wood_required, brick_required, nails_required, pipe_required created FROM homes ORDER BY created DESC').fetchall()
    return render_template('display/index.html', items=items)
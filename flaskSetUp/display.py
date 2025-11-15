from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from werkzeug.exceptions import abort
from flaskSetUp.auth import login_required
from flaskSetUp.db import get_db

bp = Blueprint('display', __name__)

@bp.route('/displayhomes', methods=('GET', 'POST'))
def displayHomes():
    db = get_db()
    items = db.execute('SELECT id, wood_required, brick_required, nails_required, pipe_required created FROM homes ORDER BY created DESC').fetchall()
    prices = db.execute('SELECT wood_price, brick_price, nails_price, pipe_price FROM prices WHERE id = 1').fetchone()

    homeSelected = None
    if request.method == 'POST':
        choice = request.form.get('homes')
        # map form values to row ids (adjust as appropriate)
        mapping = {}
        for item in items:
            mapping[str(item['id'])] = item['id']
        home_id = mapping.get(choice)

        if home_id:
            homeSelected = db.execute(
                'SELECT id, wood_required, brick_required, nails_required, pipe_required, created FROM homes WHERE id = ?',
                (home_id,)
            ).fetchone()


        else:
            flash('Invalid home selection.')
            homeSelected = None


    return render_template('display/homeDisplay.html', items=items, homeSelected=homeSelected, prices=prices)





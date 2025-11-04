from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from werkzeug.exceptions import abort
from flaskSetUp.auth import login_required
from flaskSetUp.db import get_db

bp = Blueprint('display', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    items = db.execute(
        'SELECT id, wood_required, brick_required, nails_required, pipe_required created FROM homes ORDER BY created DESC').fetchall()
        
    selected = None
    if request.method == 'POST':
        choice = request.form.get('homes')
        # map form values to row ids (adjust as appropriate)
        mapping = {'homeOne': 1, 'homeTwo': 2, 'homeThree': 3}
        home_id = mapping.get(choice)
        if home_id:
            homeSelected = db.execute(
                'SELECT id, wood_required, brick_required, nails_required, pipe_required, created FROM homes WHERE id = ?',
                (home_id,)
            ).fetchone()
            prices = db.execute(
                'SELECT wood_price, brick_price, nails_price, pipe_price FROM prices WHERE id = 1'
            ).fetchone()

            

            # get this data to display on page
            print("Selected Home Details:")
            print(f"ID: {homeSelected['id']}")
            print(f"Wood Required: {homeSelected['wood_required']}  price per unit: ${prices['wood_price']}  total: ${homeSelected['wood_required'] * prices['wood_price']}")
            print(f"Brick Required: {homeSelected['brick_required']}  price per unit: ${prices['brick_price']}  total: ${homeSelected['brick_required'] * prices['brick_price']}")
            print(f"Nails Required: {homeSelected['nails_required']}  price per unit: ${prices['nails_price']}  total: ${homeSelected['nails_required'] * prices['nails_price']}")
            print(f"Pipe Required: {homeSelected['pipe_required']}  price per unit: ${prices['pipe_price']}  total: ${homeSelected['pipe_required'] * prices['pipe_price']}")
            print(f"Total Cost: ${ (homeSelected['wood_required'] * prices['wood_price']) + (homeSelected['brick_required'] * prices['brick_price']) + (homeSelected['nails_required'] * prices['nails_price']) + (homeSelected['pipe_required'] * prices['pipe_price']) }")

        else:
            flash('Invalid home selection.')

    return render_template('display/index.html', items=items, selected=selected)




